#define GAP_OPEN %(gap_open)d
#define GAP_EXTEND %(gap_extend)d
#define MAX_INT %(max_int)d

#define QUERIES_MAXSIZE %(queries_maxsize)d
#define REFERENCE_SIZE %(reference_size)d
#define SEMIGLOBAL %(semiglobal)s

#define MAXCIGARLEN (QUERIES_MAXSIZE + 2)
#define slen (QUERIES_MAXSIZE * 2)
#define So ((1-sbase) * slen)
#define Si (sbase * slen)
#define extract_char(pos, encoded) (encoded[pos / 16] >> ((pos %% 16) * 2)) & 3u

//#pragma OPENCL EXTENSION cl_amd_printf : enable


inline void fill_traceback(int2 T[], int n, int m) {
    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= m; j++) {
            int index = i * (m+1) + j;
            T[index].x = i;
            T[index].y = j;
        }
    }
}


/**
 * Debugging function.
 */
void print_traceback(int2 T[], int n, int m) {
    for(int i=0; i<n+1; i++)
    {
        printf("i=%%i: ", i);
        for(int j=0; j<m+1; j++)
        {
            printf("%%i,%%i ", T[i*(m+1) + j].x, T[i*(m+1) + j].y);
        }
        printf("\n");
    }
}


inline int score(char refbase, char readbase) {
    if (refbase == 'N' || refbase == readbase) {
        return 1;
    }
    return -1;
}


inline void fill_scores(int S[], int I[], int D[], int s) {
    for(int i=0; i<s * 2; i++)
    {
        S[i] = 0;
        I[i] = -MAX_INT;
        D[i] = -MAX_INT;
    }
}


__kernel void alignment(
    __global const char* queries,
    __global const int* queries_sizes,
    __global const char* reference,
    __global int* positions,
    __global int2* cigar,
    __global int* cigar_len,
    __global int* scores
)
{
    const int gid = get_global_id(0);
    const int qbase = gid * QUERIES_MAXSIZE;

    const int m = queries_sizes[gid];

    const int p = max(positions[gid] - m / 2, 0);
    const int n = min(m * 2, REFERENCE_SIZE - p); // TODO find tighter bounds
    //printf("%%i %%i %%i\n", p, n, REFERENCE_SIZE);

    // Smith waterman alignment
    int best = 0, besti = 0, bestj = 0;
    //printf("Score %%i \n", best);

    int S[slen * 2];
    int I[slen * 2];
    int D[slen * 2];
    fill_scores(S, I, D, slen);

    int2 T[(QUERIES_MAXSIZE * 2 + 1) * (QUERIES_MAXSIZE + 1)]; // TODO find tighter bounds

    fill_traceback(T, n, m);

    for(int i = 1; i <= n; i++)
    {
        const char refbase = reference[p + i - 1];
        int sbase = i %% 2;
        S[sbase * slen] = 0;

        for(int j = 1; j <= m; j++)
        {
            const char querybase = queries[qbase + j - 1];

            D[Si + j] = max(S[So + j] - GAP_OPEN, D[So + j] - GAP_EXTEND);
            I[Si + j] = max(S[Si + j - 1] - GAP_OPEN, I[Si + j - 1] - GAP_EXTEND);

#if SEMIGLOBAL
            int _scores[3] = {
                S[So + j-1] + score(refbase, querybase),
                D[Si + j],
                I[Si + j]
            };
            int2 t[3] = {
                (int2)(i - 1, j - 1),
                (int2)(i-1,j),
                (int2)(i, j-1)
            };

            S[Si + j] = _scores[2];
            for(int q = 2; q >= 0; q--)
            {
                if(_scores[q] >= S[Si + j])
                {
                    T[i*(m+1) + j] = (int2)t[q];
                    S[Si + j] = _scores[q];
                }
            }
#else
            int _scores[4] = {
                S[So + j-1] + score(refbase, querybase),
                D[Si + j],
                I[Si + j],
                0
            };
            int2 t[4] = {
                (int2)(i - 1, j - 1),
                (int2)(i-1,j),
                (int2)(i, j-1),
                (int2)(i, j)
            };

            S[Si + j] = _scores[3];
            for(int q = 3; q >= 0; q--)
            {
                if(_scores[q] >= S[Si + j])
                {
                    T[i*(m+1) + j] = (int2)t[q];
                    S[Si + j] = _scores[q];
                }
            }
            if(S[Si + j] > best)
            {
                best = S[Si + j], besti = i, bestj = j;
            }
#endif
        }
#if SEMIGLOBAL
        if(S[Si + m] > best)
        {
            best = S[Si + m], besti = i, bestj = m;
        }
#endif
    }

    //print_traceback(T, n, m);

    // compute CIGAR string from traceback
    int2 reverse_cigar[MAXCIGARLEN]; // at most there are QUERIES_MAXSIZE + 2 different items in the CIGAR
    int alast = -1;
    int acount = 0;
    int i = besti, j = bestj;
    int cigarlen = 0;
    int _sum_base_qual = 0;
    if(bestj < m)
    {
        // soft clip the missing suffix
        reverse_cigar[cigarlen++] = (int2)(4, m - bestj);
    }
    if(best > 0)  // TODO remove
    {
        while(true)
        {
            int ii = T[i*(m+1) + j].x;
            int jj = T[i*(m+1) + j].y;

            if(ii == i && jj == j)
            {
                reverse_cigar[cigarlen++] = (int2)(alast, acount);
                break;
            }
            int acode, alen;
            int ilen = i - ii, jlen = j - jj;
            if(ilen == jlen)
            {
                acode = 0;
                alen = ilen;
            }
            else if (ilen < jlen)
            {
                acode = 1; // I
                alen = jlen;
            }
            else
            {
                acode = 2; // D
                alen = ilen;
            }
            if(alast == -1)
            {
                alast = acode;
            }

            if(acode == alast)
            {
                acount += alen;
            }
            else
            {
                reverse_cigar[cigarlen++] = (int2)(alast, acount);
                alast = acode;
                acount = alen;
            }
            i = ii;
            j = jj;
        }
        if(j > 0)
        {
            // soft clip the missing prefix
            reverse_cigar[cigarlen++] = (int2)(4, j);
        }

        positions[gid] = p + i;

        int cigar_baseindex = gid * MAXCIGARLEN;
        for(int i=0; i < cigarlen; i++)
        {
            cigar[cigar_baseindex + i] = reverse_cigar[cigarlen - i - 1];
        }
    }
    cigar_len[gid] = cigarlen;
    scores[gid] = best;
}

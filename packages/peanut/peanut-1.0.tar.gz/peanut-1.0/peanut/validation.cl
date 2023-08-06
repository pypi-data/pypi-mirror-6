#define BLOCK_SIZE %(blocksize)d
#define BAND_WIDTH %(band_width)d
#define MIN_SCORE %(min_score)d
#define C 16

#define THREE 3u
#define ONES 0xffffffffu
#define ZEROS 0u
#define MSB1 0x80000000


void init_column(__global const uint* queries, __local uint* B, const int qbase)
{
    # pragma unroll 4
    for(uint c = 0; c < 4; c++)
    {
        B[c] = 0u;
    }
    const uint query_qgram = queries[qbase];
    # pragma unroll 16
    for(int j = 0; j < 16; j++)
    {
        const uint c_query = (query_qgram >> (j * 2)) & 3u;
        B[c_query] |= 1 << (BAND_WIDTH - C + j);
    }
}


int calc_column_diagonal(const uint B_c_ref, uint* VP, uint* VN)
{
    uint X = B_c_ref | *VN;
    const uint D0 = ((*VP + (X & *VP)) ^ *VP) | X;
    const uint HN = *VP & D0;
    const uint HP = *VN | ~ (*VP | D0);
    X = D0 >> 1;
    *VN = X & HP;
    *VP = HN | ~ (X | HP);

    return 1 - ((D0 >> (BAND_WIDTH - 1)) & 1u);
}


int calc_column_horizontal(const uint B_c_ref, uint* VP, uint* VN, const int s)
{
    uint X = B_c_ref | *VN;
    const uint D0 = ((*VP + (X & *VP)) ^ *VP) | X;
    const uint HN = *VP & D0;
    const uint HP = *VN | ~ (*VP | D0);
    X = D0 >> 1;
    *VN = X & HP;
    *VP = HN | ~ (X | HP);

    return ((HP >> s) & 1) - ((HN >> s) & 1);
}


uint read_character(const uint qgram, const int j)
{
    return (qgram >> j) & 3u;
}

void shift_column(__local uint* B)
{
    #pragma unroll 4
    for(uint c=0; c < 4; c++)
        B[c] >>= 1;
}


void load_column(__local uint* B, const uint query_qgram, const int j)
{
    B[read_character(query_qgram, j)] |= 1u << (BAND_WIDTH - 1);
}


void validate_hit(
    __global const uint* queries,
    __global const uint* reference,
    __local uint* B,
    //const int bbase,
    const int qbase,
    const int rbase,
    const int query_size,
    const int reference_size,
    int* best_dist,
    int* best_pos)
{

    init_column(queries, B, qbase);

    uint VP = ONES;
    uint VN = ZEROS;
    int dist = C;
    int pos = 0;
    int i = 0;
    int j = 0;
    const int posmax = reference_size - rbase * 16;

    // phase 1 (diagonal)
    for(; i < (query_size - C) / 16; i++)
    {
        const uint query_qgram = queries[qbase + i + 1];
        const uint reference_qgram = reference[rbase + i];

        #pragma unroll 32
        for(j = 0; j < 32; j += 2)
        {
            shift_column(B);//, bbase);
            load_column(B, query_qgram, j);
            const uint c_ref = read_character(reference_qgram, j);

            dist += calc_column_diagonal(B[c_ref], &VP, &VN);
            pos++;
        }
    }

    // phase 2 (diagonal)
    {
        const uint query_qgram = queries[qbase + i + 1];
        const uint reference_qgram = reference[rbase + i];

        // in contrast to Weese et al, run until pos < query_size - C here
        for(j = 0; j < 32 && pos < min(posmax - 1, query_size - C); j += 2)
        {
            shift_column(B);//, bbase);
            load_column(B, query_qgram, j);

            const uint c_ref = read_character(reference_qgram, j);

            dist += calc_column_diagonal(B[c_ref], &VP, &VN);
            pos++;
        }
    }

    // phase 3 (horizontal)
    // update rule: s = (BAND_WIDTH - 2) - (pos - (query_size - C + 1))
    int s = BAND_WIDTH - 2 + query_size - C + 1 - pos;
    for(; i <= query_size / 16 + 1; i++)
    {
        const uint reference_qgram = reference[rbase + i];

        for(; j < 32 && pos < posmax; j += 2)
        {
            shift_column(B);//, bbase);
            const uint c_ref = read_character(reference_qgram, j);

            dist += calc_column_horizontal(B[c_ref], &VP, &VN, s);
            if(dist < *best_dist)
            {
                *best_dist = dist;
                *best_pos = pos;
            }
            s--;
            pos++;
        }
        j = 0;
    }
}


__kernel void validate_hits
(
    const int hits_size,
    const int reference_size,
    const int reference_offset,
    const int queries_width,
    const int offset,
    __global const uint* reference,
    __global const uint* queries,
    __global const int* queries_sizes,
    __global int* hit_positions,  // reference positions to investigate
    __global int* hit_queries,
    __global int* hit_scores
)
{
    const int h = offset + get_global_id(0);

    if(h >= hits_size)
        return;

    const int query = hit_queries[h];
    const int rbase = hit_positions[h] / 16;

    const int qbase = query * queries_width;
    const int query_size = queries_sizes[query];
    const int lid = get_local_id(0);

    __local uint B[BLOCK_SIZE * 4];
    //const int bbase = lid * 4;

    int best_dist = ceil((100 - MIN_SCORE) / 100.0 * query_size) + 1;  // the worst dist is 100 - MIN_SCORE percent of the read
    int best_pos = 0;
    validate_hit(queries, reference, &B[lid * 4], qbase, rbase, query_size, reference_size, &best_dist, &best_pos);

    // we validate reverse, hence best pos marks the starting position relative to the reference size
    hit_positions[h] = (rbase * 16) + best_pos; //reference_size + reference_offset - (rbase * 16) - best_pos - 1;
    // percent identity as defined in the README of RazerS 3
    hit_scores[h] = 100.0 * (query_size - best_dist) / query_size;
}

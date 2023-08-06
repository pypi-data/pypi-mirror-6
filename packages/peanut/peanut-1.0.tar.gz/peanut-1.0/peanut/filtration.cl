#define INDEX_SIZE %(index_size)d
#define OUTER_POS_SIZE %(outer_pos_size)d

#define PARTITION_REFERENCE

//#define DEBUG
#ifdef DEBUG
#pragma OPENCL EXTENSION cl_amd_printf : enable
#endif


#ifndef CL_VERSION_1_2
int popcount(uint n)
{
    int c = 0;
    // use inline assembler for popcount on nvidia hardware (see https://devtalk.nvidia.com/default/topic/524601/opencl-linux-header-files-opencl-status/)
    asm("popc.b32 %%0, %%1;" : "=r"(c) : "r" (n));
    return c;
}
#endif


uint interpolate(
    const int i,
    const int j,
    __global const uint* sequence)
{
    // the indicator ensures that ref_i+1 is set to 0 if j is 0
    // this is needed because the shift is taken modulo 32 by the compiler
    const int shift = j << 1;
    return (j > 0) ? sequence[i] >> shift | (sequence[i+1] << (32 - shift)) : sequence[i];
}


uint get_qgroup(uint qgram)
{
    return qgram / 32u;
}


uint get_qbit(uint qgram)
{
    return qgram %% 32u;
}


bool contains_qgram(__global const uint* index, uint qgroup, uint qbit)
{
    return (index[qgroup] >> (qbit)) & 1u;
}


int get_occ_pos_start(__global const uint* index, __global const int* occ_outer_pos, uint qgroup, uint qbit)
{
    const uint mask = (1u << qbit) - 1;
    const int inner_pos = popcount(index[qgroup] & mask) + ((qgroup %% 2) ? popcount(index[qgroup - 1]) : 0);
    const int outer_pos = occ_outer_pos[qgroup / 2];
    return outer_pos + inner_pos;
}


int get_occ_start(__global const uint* index, __global const int* occ_outer_pos, __global int* occ_pos, uint qgroup, uint qbit)
{
    return occ_pos[get_occ_pos_start(index, occ_outer_pos, qgroup, qbit)];
}


__kernel void create_queries_index(
    const int queries_size,
    __global const uint* queries,
    __global const int* queries_sizes,
    __global uint* index)
{
    const int gid = get_global_id(0);
    const int i = get_global_id(1);
    const int j = get_global_id(2);

    if(gid >= queries_size || (i+1) * 16 + j > queries_sizes[gid])
        return;

    const uint qgram = interpolate(gid * get_local_size(1) + i, j, queries);

    atomic_or(&index[get_qgroup(qgram)], 1u << get_qbit(qgram));
}


__kernel void popcount_index(
    __global const uint* index,
    __global int* popcount_index)
{
    const int gid = get_global_id(0);

    if(gid >= OUTER_POS_SIZE)
        return;
    const int i = gid * 2;

    // we sample the popcount such that two subsequent items are counted together
    // this allows us to create the 2-sample of occ_outer_pos as a cumsum of the popcount
    popcount_index[gid + 1] = popcount(index[i]) + popcount(index[i + 1]);
}


__kernel void create_queries_occ_count
(
    const int queries_size,
    const int queries_width,
    __global const uint* queries,
    __global const int* queries_sizes,
    __global const uint* index,
    __global const int* occ_outer_pos, // prefix-sum of popcount_index
    __global int* occ_count // initialized with zeros
)
{
    const int gid = get_global_id(0);

    if(gid >= queries_size)
        return;

    const int ibase = gid * queries_width;
    const int ibase_bases = ibase * 16;
    const int size = queries_sizes[gid] - 16; // no interpolation for the last qgram needed
    int prefix = 0;
    uint last_qgram = 0u;

    for(int i = 0; i < queries_width; i++)
    {
        for(int j=0; j < 16 && (prefix + j <= size); j++)
        {
            const uint qgram = interpolate(ibase + i, j, queries);
            if(i == 0 && j == 0 || qgram != last_qgram)
            {
                const int p = get_occ_pos_start(
                    index,
                    occ_outer_pos,
                    get_qgroup(qgram),
                    get_qbit(qgram));
                // add 1 to the pos since we want to create occ_pos via cumsum from this and first element should be 0
                atomic_inc(&occ_count[p + 1]);
            }
            last_qgram = qgram;
        }
        prefix += 16;
    }
}


__kernel void create_queries_occ
(
    const int queries_size,
    const int queries_width,
    __global const uint* queries,
    __global const int* queries_sizes,
    __global const uint* index,
    __global const int* occ_outer_pos, // prefix-sum of index popcount
    __global const int* occ_pos, // prefix-sum of occ_count
    __global int* occ_count, // initialized with zeros
    __global int* occ // initialized with -1
)
{
    const int gid = get_global_id(0);

    if(gid >= queries_size)
        return;

    const int ibase = gid * queries_width;
    const int ibase_bases = ibase * 16;
    const int size = queries_sizes[gid] - 16; // no interpolation for the last qgram needed
    int prefix = 0;
    uint last_qgram = 0u;

    for(int i = 0; i < queries_width; i++)
    {
        for(int j=0; j < 16 && (prefix + j <= size); j++)
        {
            const uint qgram = interpolate(ibase + i, j, queries);
            if(i == 0 && j == 0 || qgram != last_qgram)
            {
                const int p = get_occ_pos_start(index, occ_outer_pos, get_qgroup(qgram), get_qbit(qgram));
                const int p_inner = atomic_inc(&occ_count[p]);
                occ[occ_pos[p] + p_inner] = ibase_bases + prefix + j;
            }
            last_qgram = qgram;
        }
        prefix += 16;
    }
}


__kernel void filter_reference
(
    const int reference_pos_size,
    __global const uint* reference,
    __global const uint* reference_pos,
    __global const uint* index,
    __global const int* occ_outer_pos,
    __global const int* occ_pos,
    __global int* hits
)
{
    const int gid = get_global_id(0);

    if(gid >= reference_pos_size)
        return;

    const int i = reference_pos[gid];
    const uint qgram = reference[i];
    const uint qgroup = get_qgroup(qgram);
    const uint qbit = get_qbit(qgram);
    if(contains_qgram(index, qgroup, qbit))
    {
        const int p = get_occ_pos_start(index, occ_outer_pos, qgroup, qbit);
        const int kmin = occ_pos[p];
        const int kmax = occ_pos[p+1];
        hits[gid + 1] = kmax - kmin;
    }
}


__kernel void create_candidates
(
    const int reference_pos_size,
    const int queries_width_bases,
    __global const uint* reference,
    __global const int* reference_pos,
    __global const uint* index,
    __global const int* occ_outer_pos,
    __global const int* occ_pos,
    __global const int* occ,
    __global int* hits_start,  // prefix-summed hits array
    __global int* hit_positions,
    __global int* hit_queries
)
{
    const int gid = get_global_id(0);

    if(gid >= reference_pos_size)
        return;

    const int i = reference_pos[gid];

    const int rpos = i * 16;
    const uint qgram = reference[i];
    const uint qgroup = get_qgroup(qgram);
    const uint qbit = get_qbit(qgram);

    const int p = get_occ_pos_start(index, occ_outer_pos, qgroup, qbit);
    const int kmin = occ_pos[p];
    const int kmax = occ_pos[p+1];
    const int hit_start = hits_start[gid];
    for(int k=0; k < kmax - kmin; k++)
    {
        const int o = occ[kmin + k];
        const int query = o / queries_width_bases;
        const int qpos = o %% queries_width_bases;
        const int hit_pos = hit_start + k;
        // query start can be outside of the reference, hence ensure that position is not negative
        hit_positions[hit_pos] = max(0, rpos - qpos);
        hit_queries[hit_pos] = query;
    }
}


__kernel void create_reference_index(
    const int reference_size,
    const int reference_pos_size,
    __global const uint* reference,
    __global const int* reference_pos,
    __global uint* index)
{
    const int gid = get_global_id(0);

    if(gid >= reference_pos_size)
        return;

    const int i = reference_pos[gid];

    const uint qgram = reference[i];
    atomic_or(&index[get_qgroup(qgram)], 1u << get_qbit(qgram));
}


__kernel void create_reference_occ_count
(
    const int reference_size,
    const int reference_pos_size,
    __global const uint* reference,
    __global const int* reference_pos,
    __global const uint* index,
    __global const int* occ_outer_pos, // every second item of prefix-sum of popcount_index
    __global int* occ_count // initialized with zeros
)
{
    const int gid = get_global_id(0);

    if(gid >= reference_pos_size)
        return;

    const int i = reference_pos[gid];

    const uint qgram = reference[i];

    const int p = get_occ_pos_start(index, occ_outer_pos, get_qgroup(qgram), get_qbit(qgram));
    atomic_inc(&occ_count[p + 1]);
}


__kernel void create_reference_occ
(
    const int reference_size,
    const int reference_pos_size,
    __global const uint* reference,
    __global const int* reference_pos,
    __global const uint* index,
    __global const int* occ_outer_pos,
    __global const int* occ_pos,
    __global int* occ_count, // initialized with zeros
    __global int* occ
)
{
    const int gid = get_global_id(0);

    if(gid >= reference_pos_size)
        return;

    const int i = reference_pos[gid];

    const uint qgram = reference[i];

    const int p = get_occ_pos_start(index, occ_outer_pos, get_qgroup(qgram), get_qbit(qgram));
    const int p_inner = atomic_inc(&occ_count[p]);
    occ[occ_pos[p] + p_inner] = gid;
}


__kernel void count_reference_repeats
(
    const int reference_size,
    const int reference_pos_size,
    const int max_occ_pos_address,
    __global const uint* reference,
    __global const int* reference_pos,
    __global const uint* index,
    __global const int* occ_outer_pos,
    __global const int* occ_pos,
    __global const int* occ,
    __global int* reference_pos_repeats
)
{
    const int gid = get_global_id(0);
    const int j = get_global_id(1);

    if(gid >= reference_pos_size || reference_pos[gid] * 16 + j >= reference_size)
        return;

    const int i = reference_pos[gid];
    const uint qgram = interpolate(i, j, reference);
    const uint qgroup = get_qgroup(qgram);
    const uint qbit = get_qbit(qgram);
    if(contains_qgram(index, qgroup, qbit))
    {
        const int p = get_occ_pos_start(index, occ_outer_pos, qgroup, qbit);
        const int kmin = occ_pos[p];
        const int kmax = occ_pos[p + 1];

        for(int k=kmin; k<kmax; k++)
        {
            atomic_inc(&reference_pos_repeats[occ[k]]);
        }
    }
}


#pragma OPENCL EXTENSION cl_amd_printf : enable

__kernel void pack(
    const int bitencoded_sequence_size,
    __global uchar* bitencoded_sequence,
    __global uint* packed_sequence)
{
    const int i = get_global_id(0);
    const int _i = i * 16;
    const int stop = min(16, bitencoded_sequence_size - _i);

    uint qgram = 0;
    for(int j=stop-1; j>=0; j--)
    {
        qgram <<= 2;
        qgram |= bitencoded_sequence[_i + j];
    }
    packed_sequence[i] = qgram;
}


__kernel void pack_sequences(
    const int sequences_size,
    const int sequences_width,
    const int encoded_sequences_width,
    __global const uchar* sequences,
    __global uint* encoded_sequences
)
{
    const int k = get_global_id(0);
    const int i = get_global_id(1);

    if(k >= sequences_size || i >= encoded_sequences_width)
        return;

    const int _i = i * 16;
    const int base = k * sequences_width;

    uint qgram = 0;
    for(int j=min(_i + 15, sequences_width-1); j>=_i; j--)
    {
        qgram <<= 2;
        qgram |= sequences[base + j];
    }

    encoded_sequences[k * encoded_sequences_width + i] = qgram;
}

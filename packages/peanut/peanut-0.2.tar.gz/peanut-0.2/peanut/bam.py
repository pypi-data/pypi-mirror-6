from operator import attrgetter
from struct import pack
import numpy as np

from pysam import Samfile, AlignedRead

from peanut.bitencoding import bitdecode_array


FLAGS = dict(revcomp=0x10, unmapped=0x4)


class BamWriter:

    def __init__(self, path, index, query_buffersize):
        # prepare the bam file
        header = dict(
            HD=dict(
                VN="1.0"
                ),
            SQ=[dict(SN=reference.name, LN=len(reference))
                for reference in filter(attrgetter("plusstrand"), index)])
        self.samfile = Samfile(path, "wb", header=header)

    def write_queries(
        self,
        queries,
        ids,
        mappings,
        num_mappings,
        reference):

        samfile = self.samfile
        tid = samfile.gettid(reference.name)
        flag = 0 if reference.plusstrand else FLAGS["revcomp"]
        for qid, mappings_, num_mappings_ in zip(
            ids, mappings, num_mappings):
            size = queries.sizes[qid]
            name = queries.names[qid]
            seq = bitdecode_array(queries.sequences[qid][:size])
            qual = pack(
                    "<{}B".format(size), *queries.qualities[qid][:size])
            for pos in mappings_[:num_mappings_]:
                aread = AlignedRead()
                aread.qname = name
                aread.seq = seq
                aread.qual = qual
                aread.tid = tid
                aread.pos = pos
                aread.mapq = 1
                aread.flag = flag
                samfile.write(aread)

    def write_unmapped(self, queries, mapped):
        unmapped = np.logical_not(mapped)
        flag = FLAGS["unmapped"]
        for name, sequence, quality, size in queries[unmapped]:
            aread = AlignedRead()
            aread.qname = name
            aread.seq = bitdecode_array(sequence[:size])
            aread.qual = pack("<{}B".format(size), *quality[:size])
            aread.flag = flag
            self.samfile.write(aread)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.samfile.close()

class BamReader:

    def __init__(self, path):
        self.samfile = Samfile(path, "rb")

    def __iter__(self):
        return self.samfile.__iter__()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.samfile.close()

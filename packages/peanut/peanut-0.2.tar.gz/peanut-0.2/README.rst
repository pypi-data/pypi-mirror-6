=======================================
PEANUT - The ParallEl AligNment UTility
=======================================

PEANUT is a read mapper for DNA or RNA sequence reads.
Read mapping is the process of aligning biological DNA or RNA sequencing reads to a known reference genome.

By exploiting the massive parallelism of modern graphics processors and a novel index datastructure, PEANUT achieves supreme sensitivity and speed compared to current state of the art read mappers like BWA MEM, Bowtie2 and RazerS3.
PEANUT thereby allows to report both only the best hits or all hits.

For details about PEANUT, please refer to our scientific paper "Massively Parallel Read Mapping on GPUs with PEANUT" (submission in preparation).
A preprint is available at http://arxiv.org/abs/1403.1706.


Requirements
------------

* A POSIX compatible OS (e.g. Linux, MacOS X, FreeBSD)
* an NVIDIA GPU with up-to-date proprietary drivers (this may change in the future as the AMD drivers become more mature)
* Cython >= 0.19
* Pyopencl >= 2013.1
* Numpy >= 1.7
* Python >= 3.2


Installation
------------

Using easy_install, all dependencies will be installed automatically if missing::

   $ easy_install3 peanut

When installing manually from setup.py, just execute::

   $ python3 setup.py install


Usage
-----

PEANUT will be available as a command line tool.
To index a reference genome `genome.fasta`, issue the following::

   $ peanut index genome.fasta genome.index.hdf5

To map paired end reads `reads.1.fastq` and `reads.2.fastq` onto the indexed reference,
use the following invocation::

   $ peanut map --threads 8 reads.1.fastq reads.2.fastq genome.index.hdf5 | samtools view -Sb - > mapped.bam

As can be seen, PEANUT outputs hits in the SAM format.
Hence, output has to be piped into samtools to obtain a BAM file.
PEANUT buffers reads and hits in GPU and CPU memory.
The default buffer settings of PEANUT are optimized for a GPU with at least 2.5GB memory and a CPU with 16GB memory.
You can lower both buffer sizes to adapt for weaker systems, e.g.::

   $ peanut map --read-buffer 100000 --hits-buffer 500000 ...

This however can reduce performance since the amount of possible parallelelism on the GPU is affected.
For further help, invoke::

   $ peanut --help

or visit http://peanut.readthedocs.org.

Citation
--------

If you use PEANUT in your publication, please cite the following preprint for now:

Köster, J., Rahmann, S., 2014. Massively parallel read mapping on GPUs with PEANUT. arXiv:1403.1706.

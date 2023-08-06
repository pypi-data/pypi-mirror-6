.. _utilities_index:

Seal Utilities
================

The Seal distribution includes some of the utilities and scripts we use
internally.  These may not be all maintained (it depends on whether we're using
them at the moment).  Use at your own risk!!

Note that some of these utilities don't follow the :ref:`Seal usage convention
<program_usage>`.


seal distcp_files
++++++++++++++++++++

A utility useful for uploading files to HDFS.

Under the hood, it uses ``hadoop distcp``, but it avoids you having to prepend
``file://`` to local files.

Usage::

  seal distcp_files filenames*  hdfs_dest_directory


seal tsvsort
++++++++++++++++

A distributed sorting program for large text files.  See the :ref:`tsv_sort_index`
page for details.


examples/align_script
+++++++++++++++++++++++++

A script to perform read alignment using libbwa (the same one used by Seqal).

Usage::

  examples/align_script [OPTIONS] --reference=REFERENCE PRQFILE PRQFILE

You can also pipe it input in prq format via stdin.


examples/find_fq_format
++++++++++++++++++++++++++

Reads a fastq file and tries to determine whether the base qualities are encoded
in Sanger or Illumina format.


examples/prq_local
+++++++++++++++++++++

Reformat a pair of qseq files (one for reads 1, one for reads 2) into a prq file.
Read mates have to appear on the same line of their respective files.

Usage::

  examples/prq_local reads1.qseq reads2.qseq output.prq

examples/prq_to_fastq
++++++++++++++++++++++++++

Split a prq file into two fastq files.

Usage::

  examples/prq_to_fastq input.prq reads1.fastq reads2.fastq


examples/realign_snp
+++++++++++++++++++++++

Realign SNPs.  See the documentation in the script file for details.


.. _index:

Seal
====================================

Seal is a suite of distributed applications for aligning short DNA reads, and
manipulating and analyzing short read alignments.  Seal applications generally run on the Hadoop_
framework and are made to scale well in the amount of computing nodes available
and the amount of the data to process.  This fact makes Seal particularly well
suited for processing large data sets.


Tools
++++++++++

Seal currently contains the following Hadoop-based tools.

:ref:`Bcl2Qseq <bcl2qseq_index>`
  Extract reads in ``qseq`` format from an Illumina run
  directory.

:ref:`Demux <demux_index>`
  Separate sample data in the ``qseq`` file format produced by a multiplexed Illumina run.

:ref:`PairReadsQSeq <prq_index>`
  convert files in the Illumina ``qseq`` file format to ``prq`` format to be processed by the alignment program, :ref:`Seqal <seqal_index>`.

:ref:`Seqal <seqal_index>`
  Distributed short read mapping and duplicate removal tool.

:ref:`ReadSort <read_sort_index>`
  Distributed sorting of read mappings.

:ref:`RecabTable <recab_table_index>`
  distributed calculation of covariates table to estimate empirical base qualities.

Please see each individual tool's page for specific details.


Do you need Seal?
++++++++++++++++++++++++

Seal has been built with large data sets in mind, like those produced by whole
genome sequencing runs.  If you're aligning read datasets of more than a couple
of hundred MB, and you have a cluster of computers (even a small one, say 4 or 5
nodes, and up to hundreds of nodes) then Seal might be for you.

Seal provides a number of important features.

Scalability and speed
-----------------------

Seal can efficiently use the computer power of a large number of
nodes.  We have successfully tested SEAL of 500GB datasets, running on 16- to
128-node clusters.  Thanks to its ability to scale, Seal can achieve very high
throughputs by harnessing the computing power of many machines.  And when you
need more speed, you can simply add more machines.


Memory efficiency
-------------------

Seal can use your computer's resources more efficiently than other alignment
tools.  Thanks to its use of shared memory, as many as 7 or 8 alignment
processes can be run concurrently on a single workstation with 8 GB of memory,
using a Human reference genome (UCSC HG18, for instance).


Robustness
--------------

Thanks to Hadoop, Seal provides a start-and-forget solution,
resisting node failures and transient cluster conditions that may cause your
jobs to fail.  It also avoids basing all operations on a centralized shared
stored volume, which can represent a single point of failure.


Users
+++++++

Seal is currently used to process all the DNA sequenced at the `CRS4 Sequencing
and Genotyping Platform
<http://www.crs4.it/web/sequencing-and-genotyping-platform>`_.


Contents
+++++++++

.. toctree::
   :maxdepth: 2

   news
   installation
   installation_dependencies
   installing_seal
   installation_deploying
   program_usage
   program_index
   bcl2qseq_index
   demux_index
   prq_index
   seqal_index
   seqal_options
   counters
   read_sort_index
   merge_alignments_index
   recab_table_index
   utilities_index
   tsv_sort_index
   seal_config
   file_formats
   tuning
   additional
   faq

.. _Hadoop: http://hadoop.apache.org/
.. _BWA: http://bio-bwa.sourceforge.net/
.. _PairReadsQSeq: :ref:prq_index
.. _Seqal: seqal_index
.. _ReadSort: read_sort_index

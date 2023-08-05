***************************************
Overview
***************************************

The ruffus module is a lightweight way to add support
for running computational pipelines.

Computational pipelines are often conceptually quite simple, especially
if we breakdown the process into simple stages, or separate **tasks**.

Each stage or **task** in a computational pipeline is represented by a python function
Each python function can be called in parallel to run multiple **jobs**.

Ruffus was originally designed for use in bioinformatics to analyse multiple genome
data sets.

***************************************
Documentation
***************************************

Ruffus documentation can be found `here <http://www.ruffus.org.uk/>`_ ,
with an `download notes <http://www.ruffus.org.uk/installation.html>`_ ,
a `short tutorial <http://www.ruffus.org.uk/tutorials/simple_tutorial/simple_tutorial.html>`_ and
an `in-depth manual <http://www.ruffus.org.uk/tutorials/manual/manual_introduction.html>`_ .


***************************************
Background
***************************************

The purpose of a pipeline is to determine automatically which parts of a multi-stage
process needs to be run and in what order in order to reach an objective ("targets")

Computational pipelines, especially for analysing large scientific datasets are
in widespread use.
However, even a conceptually simple series of steps can be difficult to set up and
to maintain, perhaps because the right tools are not available.

***************************************
Design
***************************************

The ruffus module has the following design goals:

* Simplicity. Can be picked up in 10 minutes
* Elegance
* Lightweight
* Unintrusive
* Flexible/Powerful

***************************************
Features
***************************************

Automatic support for

* Managing dependencies
* Parallel jobs
* Re-starting from arbitrary points, especially after errors
* Display of the pipeline as a flowchart
* Reporting

***************************************
A Simple example
***************************************

Use the **@transform(...)** python decorator before the function definitions:

  .. code-block:: python

    from ruffus import *

    # make 10 dummy DNA data files
    data_files = [(prefix + ".fastq") for prefix in range("abcdefghij")]
    for df in data_files:
        open(df, "w").close()


    @transform(data_files, suffix(".fastq"), ".bam")
    def run_bwa(input_file, output_file):
        print "Align DNA sequences in %s to a genome -> %s " % (input_file, output_file)
        # make dummy output file
        open(output_file, "w").close()


    @transform(run_bwa, suffix(".bam"), ".sorted.bam")
    def sort_bam(input_file, output_file):
        print "Sort DNA sequences in %s -> %s " % (input_file, output_file)
        # make dummy output file
        open(output_file, "w").close()

    pipeline_run([sort_bam], multithread = 5)


the ``@transform`` decorator indicate that the data flows from the ``run_bwa`` function to ``run_bwa`` down
the pipeline.

********
Usage
********

Each stage or **task** in a computational pipeline is represented by a python function
Each python function can be called in parallel to run multiple **jobs**.

1. Import module::

        import ruffus


1. Annotate functions with python decorators

2. Print dependency graph if you necessary

    - For a graphical flowchart in ``jpg``, ``svg``, ``dot``, ``png``, ``ps``, ``gif`` formats::

        pipeline_printout_graph ("flowchart.svg")

    This requires ``dot`` to be installed

    - For a text printout of all jobs ::

        pipeline_printout(sys.stdout)


3. Run the pipeline::

    pipeline_run(list_of_target_tasks, verbose = NNN, [multithread | multiprocess = NNN])

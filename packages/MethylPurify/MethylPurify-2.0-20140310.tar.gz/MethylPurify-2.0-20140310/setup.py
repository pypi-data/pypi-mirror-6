"""
MethylPurify_v2
------------------

This script is used for predicting subclone purity.


Get Dependent data
````````````````````
Get the version of genome fasta that you mapped your fastqs, 
we support hg18 and hg19 genome fasta now.

.. code:: python
   
     ## use built-in script
     cd methylpurify/db
     bash genome.sh hg18



Get Dependent software
````````````````````````
* `samtools <http://samtools.sourceforge.net>`_, version larger than 0.1.18 (r982:295)
* `numpy <http://www.numpy.org>`_, version larger than 1.6

If your system is debian-like system, try:

.. code:: python

    sudo apt-get install python-numpy
    sudo apt-get install samtools

Easy to start 
`````````````````````
Input: BAM file, this should be mapped with BSMap with -R option
* `BSMap <https://code.google.com/p/bsmap/>`_

Currently, we only support hg19 and hg18 genome index mapped BAM file.

If your fastq mapping is done with hg19 index, use following command:

.. code:: python

      MethylPurify -f input.bam -b 300 -c 20 -s 50 --species hg19 -g /path/to/hg19.fa


Options
````````````````
* -f: input BAM file
* -c: coverage level
* -b: genome bin size
* -s: sampling times
* --species: species genome version
* -g: species genome fasta file(correspond to --species)


"""

from setuptools import setup, find_packages


setup(
    name='MethylPurify',
    version='2.0',
    packages=find_packages(),
    url='',
##    license='MIT',
    author='Xiaoqi Zheng',
    author_email='zheng.shnu@gmail.com',
    description='Methylation subclone detection',
    long_description = __doc__,
    scripts = ['methylpurify/bin/MethylPurify'],
    install_requires=["pyfasta"],
    package_data = {"methylpurify" : ["db/*txt", "db/*bed"]},
    keywords = "genomics methylation",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
    )

=====
pydna
=====

Pydna provide classes and functions for molecular biology using python.
Notably, PCR, cut and paste cloning and homologous recombination between linear
DNA fragments are supported. Most functionality is implemented as methods for
the double stranded DNA sequence record classes Dseq and Dseqrecord, which
are subclasses of the `Biopython <http://biopython.org/wiki/Main_Page>`_
`Seq <http://biopython.org/wiki/Seq>`_
and
`SeqRecord <http://biopython.org/wiki/SeqRecord>`_ classes.

Pydna might be useful to automate the simulation of
`sub cloning <http://en.wikipedia.org/wiki/Subcloning>`_ experiments using
python. This could be helpful to generate examples for teaching purposes. Read
the `documentation <https://pydna.readthedocs.org/en/latest/>`_ or the
`cookbook <https://www.dropbox.com/sh/u1kr30hd22zuwse/gyXYhq0BlL>`_ with example files
for further information.

Pydna was designed to semantically imitate how sub cloning experiments are
typically documented in Scientific literature. Pydna code describing a
sub cloning is reasonably compact and meant to be easily readable.

One use case for pydna is to create executable documentation
describing a subcloning experiment. The pydna code unambiguously describe
a sub cloning experiment, and can be executed to yield the sequence of the
of the resulting DNA molecule.

An `on-line <http://pydna-shell.appspot.com/>`_ shell running Python with
pydna is avaiable for experimentation.

Please post a message in the `google group <https://groups.google.com/d/forum/pydna>`_
for pydna if you have problems, questions or comments.

Feedback is very welcome!

Typical usage at the command line could look like this::

    >>> import pydna
    >>> seq = pydna.Dseq("GGATCCAAA","TTTGGATCC",ovhg=0)
    >>> seq
    Dseq(-9)
    GGATCCAAA
    CCTAGGTTT
    >>> from Bio.Restriction import BamHI
    >>> a,b = seq.cut(BamHI)
    >>> a
    Dseq(-5)
    G
    CCTAG
    >>> b
    Dseq(-8)
    GATCCAAA
        GTTT
    >>> a+b
    Dseq(-9)
    GGATCCAAA
    CCTAGGTTT
    >>> b+a
    Dseq(-13)
    GATCCAAAG
        GTTTCCTAG
    >>> b+a+b
    Dseq(-17)
    GATCCAAAGGATCCAAA
        GTTTCCTAGGTTT
    >>> b+a+a
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/usr/local/lib/python2.7/dist-packages/pydna/dsdna.py", line 217, in __add__
        raise TypeError("sticky ends not compatible!")
    TypeError: sticky ends not compatible!
    >>>

NEWS
====

=======   ========== =============================================================
version   date       comment
=======   ========== =============================================================
0.6.0     2014-04-18 Bugfixes and improvements in documentation.

0.5.0     2013-12-16 Changes to how the amplify and assembly modules work
                     the Amplicon and Assembly classes are now subclasses of
                     Dseqrecord. 

0.2.2     2013-11-05 bugfix: changed the handling of compound features
                     to fit with the new version of BioPython (1.62) which is 
                     now a requirement.

0.2.1     2013-08-18 ---

0.1.8     2013-06-02 bugfix: changed the SeqFeatures added to PCR products in the 
                     amplify module to a dict of list of strings instead of 
                     a dict of strings.

0.1.7     2013-05-29 Changed the code in amplify.Amplicon to handle features 
                     spanning the origin of circular sequences.

0.1.6     2013-04-22 Changed the behaviour of the find method of the Dseq object
                     to find substrings that span the origin. Slicing for circular
                     Dseq objects now works slightly different.

0.1.5     2013-04-18 Changed the setup.py script to permit installation
                     of the source installer without access to a c compiler.

0.1.4     2013-04-10 Cleaned up some docstrings
                     Renamed Drecord -> Dseqrecord to be more consistent with
                     Dseq and Biopython Seq/SeqRecord.

                     Changed name of keyword argument for read and parse.
                     ds=True returns Dseqrecord(s) while ds=False returns
                     SeqRecords.

0.1.3     2013-04-09 pydna created from Python-dna.
=======   ========== =============================================================

System Requirements
===================

- `Python 2.7 <http://www.python.org>`_.

- `NumPy >= 1.6.1 <http://pypi.python.org/pypi/numpy>`_.

- `Biopython >= 1.60 <http://pypi.python.org/pypi/biopython>`_.

- `networkx >= 1.7 <http://pypi.python.org/pypi/networkx>`_.

- `distribute >= 0.6.34 <http://pypi.python.org/pypi/distribute>`_.

Python 2.x
----------

Versions other than 2.7 has not been tried with this software.
Version 2.7.3 was used to build the distribution.

Python 3.x
----------

This code has not been tried with python 3.

Installation
============

Source
------

You need to install the dependencies listed above.
If you are using Windows, you need to have a C compiler installed.
The free MS visual studio 2008 express can be used.

Open the pydna source code directory (containing the setup.py file) in
terminal and type:

    sudo python setup.py install <enter>

If you need to do additional configuration, e.g. changing the base
directory, please type `python setup.py`, or see the documentation for
Setuptools.


Binary distribution
-------------------

A `Binary installer <http://pypi.python.org/pypi/pydna/#downloads>`_ for 32 bit editions of MS Windows XP and 7 are provided.

The installer has been tested on succesfully on both.

The dependencies have to be installed from source or using binary installers
for 32 bit windows.

This is a list of locations of binary installers:

- Python          <http://www.python.org/download/>
- NumPy           <http://sourceforge.net/projects/numpy/files/NumPy/>
- Biopython       <http://biopython.org/wiki/Download>
- networkx        <http://www.lfd.uci.edu/~gohlke/pythonlibs/#networkx>


Source Code Repository
----------------------

pydna is hosted by google code:

http://code.google.com/p/pydna/


Distribution Structure
======================

README.txt          -- This file.

NEWS.txt            -- Release notes and news

LICENSE.txt         -- What you can do with the code.

MANIFEST.in         -- Tells distutils what files to distribute

setup.py            -- Installation file.

run_tests.py        -- run tests by "python run_tests.py"<enter>

pydna/              -- The actual code.

docs/               -- Documentation.

scripts/            -- Miscellaneous and perhaps useful scripts and examples.

tests/              -- Testing code.



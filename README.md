FIREL0-L1
=========

Code to process FIRE L0 data to L1

Purpose
=======
Convert the ASCII BIRD packets to FIRE L1 data.  Sorted, with metadata, and in a useable format.

Features
--------
- This is a stand alone application that can be run from the command line or run in ipython
- If only an input filename is provided the output is written to the current directory
- Input filenames must be named accoring to the convention from the L3 software

Requirements
------------
Add things here as requirements are added to the L0-L1

spacepy >=1.4 (http://spacepy.lanl.gov/)
numpy  (http://www.numpy.org/)
python 2.6 or 2.7 (http://www.python.org/)

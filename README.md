FIREL0-L1
=========

Code to process FIRE L0 data to L1

Purpose
=======
Convert the ASCII hex values from MSU into meaningful data

Thoughts
--------
- output the L1 data into JSON headed ASCII (cool LANL designed ASCII format with full metatdata) (spacepy makes this easy)
- Flag errors and put them into the header
- make this a stand alone application that we run from the command line

Requirements
------------
Add things here as requirements are added to the L0-L1

# spacepy >=1.4 (http://spacepy.lanl.gov/)
# numpy  (http://www.numpy.org/)
# python 2.6 or 2.7 (http://www.python.org/)

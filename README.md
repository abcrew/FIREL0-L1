FIREL0-L1
=========

Code to process FIRE L0 data to L1

Purpose
=======
Convert the ASCII hex values form MSU into meaning data

Thoughts
--------
- output the L1 data into JSON headed ascii (cool LANL designed ASCII format with full metatdata) (spacepy makes this easy)
- Flag errors and put them into the header
- make this a stand alone application that we run from the command line

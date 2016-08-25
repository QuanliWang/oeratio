#!/usr/bin/env python3

"""
Purpose: Convert RGN file to BED file.
Input:   RGN file.
Output:  BED file.
Author:  Ayal Gussow
"""

### Imports --------------------------------------------------------------------
import sys
import argparse

import mainlib

### Functions ------------------------------------------------------------------
def rgn2bed(rgn_file, out_file):
    """
    Convert RGN file to BED file. Note that RGNs are 1-based and end-inclusive,
    while BEDs are 0-based and non-inclusive.
    """
    for line in rgn_file:
        _, chrom, loci, _ = line.split()
        loci = loci.strip("(").strip(")")

        for locus in loci.split(","):
            start, end = locus.split("..")
            start = int(start)
            end = int(end)

            print(chrom, start - 1, end, sep="\t", file=out_file)

### Main -----------------------------------------------------------------------
class Main(mainlib.Main):
    """
    Main class. Class contains run function that runs when script is run
    directly from command line.
    """
    def run(self):
        """
        Runs when script is run from command line.
        """
        rgn2bed(self.args.rgn_file, self.args.out_file)

### Arguments ------------------------------------------------------------------
def get_parser(desc):
    """
    Returns parser for command line arguments.

    <desc>: Description of script.
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--rgn", dest="rgn_file",
                        type=argparse.FileType("r"), required=True)
    return parser

### Run ------------------------------------------------------------------------
def run():
    """
    Runs when script is run from command line. Wrapper for Main.run().
    """
    with Main(parser=get_parser(__doc__), cmd=sys.argv[1:]) as main:
        main.run()

if __name__ == '__main__':
    sys.exit(run())


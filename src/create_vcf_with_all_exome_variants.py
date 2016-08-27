#!/usr/bin/env python
"""
Take an "addjusted" CCDS intervals file and reference genome to create a VCF
with all possible exome SNVs
"""

import argparse
import pyfaidx
import sys
from ConfigParser import ConfigParser
sys.path.append("..")
from oeratioGlobals import *

cfg = ConfigParser()
cfg.read("../cfg/oeratio.cfg")

def merge_intervals(intervals_list):
    """return a sorted list of merged intervals where they overlap
    """
    merged = []
    if intervals_list:
        sorted_intervals = sorted(intervals_list, key=lambda x: x[0])
        merged.append(sorted_intervals[0])
        for start, end in sorted_intervals[1:]:
            previous = merged[-1]
            previous_start, previous_end = previous
            if start <= previous_end:
                if end > previous_end:
                    merged[-1] = [previous_start, end]
            else:
                merged.append([start, end])
    return merged

def main(reference_genome, ccds, remove_bases, output_fh):
    chromosomes = [str(c) for c in xrange(1, 23)] + ["X", "Y"]
    intervals = dict([chromosome, []] for chromosome in chromosomes)
    extra_chromosomes_found = set([])
    boundaries_regex = re.compile(cfg.get("atav", "boundaries"))
    for line in ccds:
        m = boundaries_regex.match(line.strip())
        if m:
            d = m.groupdict()
            if d["chromosome"] in intervals:
                interval_list = []
                for start, end in [interval.split("..") for interval
                                   in d["intervals"].split(",")]:
                    start = int(start) + remove_bases
                    end = int(end) - remove_bases
                    intervals[d["chromosome"]].append([start, end])
            else:
                extra_chromosomes_found.add(d["chromosome"])
        else:
            raise FormatError(
                "interval {interval} is not valid".format(interval=line))
    for extra_chromosome_found in extra_chromosomes_found:
        sys.stderr.write("found defined interval(s) for unexpected chromosome:"
                         " {}\n".format(extra_chromosome_found))
    for chromosome, intervals_list in intervals.iteritems():
        intervals[chromosome] = merge_intervals(intervals_list)

    genome = pyfaidx.Fasta(reference_genome)
    output_fh.write("##fileformat=VCFv4.1\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\t"
                    "FILTER\tINFO\n")
    bases_to_include = set(["A", "C", "G", "T"])
    output_format = "{CHROM}\t{POS}\t.\t{REF}\t{ALT}\t.\t.\t\n"
    for chromosome in chromosomes:
        for start, end in intervals[chromosome]:
            # pyfaidx uses 0-based positions with endpoint not included
            seq = genome[chromosome][start - 1:end].seq
            assert len(seq) == (end + 1 - start)
            for offset, base in enumerate(seq):
                if base not in bases_to_include:
                    continue
                for ALT in sorted(bases_to_include - set(base)):
                    output_fh.write(output_format.format(
                        CHROM=chromosome, POS=start + offset,
                        REF=base, ALT=ALT))
    if output_fh is not sys.stdout:
        output_fh.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=CustomFormatter)
    parser.add_argument("-r", "--reference_genome", type=file_exists,
                        default=cfg.get("ref", "genome"),
                        help="the samtools faidx indexed FASTA reference genome")
    parser.add_argument("-C", "--CCDS", type=argparse.FileType("r"),
                        default=cfg.get("ref", "ccds"),
                        help="the addjusted CCDS file")
    parser.add_argument("--remove_bases", type=int, default=2, help="remove "
                        "this many bases from each interval (2 are added on "
                        "to the addjusted CCDS normally)")
    parser.add_argument("-o", "--output", default=sys.stdout,
                        type=argparse.FileType("w"), help="the output VCF file")
    args = parser.parse_args()
    main(args.reference_genome, args.CCDS, args.remove_bases, args.output)

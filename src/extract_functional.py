#!/usr/bin/env python
"""
Take an VCF and output all functional annotations
"""

import argparse
import sys
from oeratioGlobals import *

OUTPUT_FORMAT = "{CHROM}\t{POS}\t{ID}\t{REF}\t{ALT}\t{QUAL}\t{FILTER}\t{FUNC}\n"

def main(vcf,output):
    """output every SNV (chromosome & position)
    """

    for line in vcf:
        if line.startswith("#CHROM"):
            break

    for line in vcf:
        try: 
            fields = get_vcf_fields_dict(line)
            CHROM = fields["CHROM"]
            if fields["CHROM"] not in CHROMOSOME_LENGTHS:
                break
            POS = fields["POS"]
            ID = fields["ID"] 
            REF = fields["REF"]
            ALT = fields["ALT"]
            QUAL = fields["QUAL"]
            FILTER = fields["FILTER"]
            INFO_dict = create_INFO_dict(fields["INFO"])
            FUNC = INFO_dict["ANN"].split("|")[1]
            output.write(OUTPUT_FORMAT.format(
                CHROM=CHROM, POS=POS, ID=ID, REF=REF,ALT=ALT,QUAL=QUAL,FILTER=FILTER,FUNC=FUNC))
        except:
            print(line)

    if output is not sys.stdout:
        output.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=CustomFormatter)
    parser.add_argument("-v", "--VCF", type=argparse.FileType("r"),
                        help="the VCF to process")
    parser.add_argument("-o", "--output", default=sys.stdout,
                        type=argparse.FileType("w"), help="the output file")
    args = parser.parse_args()
    main(args.VCF, args.output)

#!/usr/bin/env python3
"""
Purpose:  Library for genomic data.
Authors:  Ayal Gussow, Matt Halvorsen, William Weir
"""

### Constants -----------------------------------------------------------------
AUTOSOMES = [str(x) for x in range(1, 23)]
ALLOSOMES = ["X", "Y", "XY"]
HUMAN_CHROMS = AUTOSOMES + ALLOSOMES
MT = ["MT"]

CHROMS = HUMAN_CHROMS + MT

# Allow for O(1) lookup when sorting chromosomes
CHROMS = dict([chrom, num] for num, chrom in enumerate(CHROMS))

BASES = ["A", "C", "G", "T"]

### Classes -------------------------------------------------------------------
class Region(object):
    """
    A single genomic region, defined here as a set of continuous sequences
    on the same chromosome.

    Region coordinates are 1-based and end-point inclusive.
    """
    def __init__(self, line=None):
        """
        Initialize a genomic region.
        """
        if line is not None:
            self.__parse(line)
        else:
            self.name = None
            self.chrom = None
            self.loci = []
            self.size = 0
            self.strand = None

    def __parse(self, line):
        """
        Parse a line from an RGN file.
        """
        try:
            (name, chrom, regions_txt, size) = line.split(" ")
        except ValueError:
            print("Error parsing line:", line)
            raise

        self.name = name
        self.chrom = format_chrom(chrom)
        self.loci = []
        self.size = 0
        self.strand = None

        loci_txt = regions_txt[1:-1].split(",")
        for locus_txt in loci_txt:
            try:
                (start, stop) = [int(x) for x in locus_txt.split("..")]
            except ValueError:
                print("Error parsing locus:", locus_txt)
                raise

            # Since we are parsing from a line, we can sort at the end
            self.add_locus(Locus(self.chrom,
                                 start,
                                 stop,
                                 self.strand),
                           sort=False)

        self.__sort_loci()

        assert self.size == int(size)

    def __sort_loci(self):
        """
        Sort the loci by genomic coordinates.
        """
        self.loci = sorted(self.loci)

    def __get_size(self):
        """
        Calculate the Region's size.
        """
        size = 0
        for locus in self.loci:
            size += locus.size
        return size

    def __update_size(self):
        """
        Update the Region's size.
        """
        self.size = self.__get_size()

    def __eq__(self, other):
        """
        Equality function for Region.
        """
        if self.name != other.name:
            return False
        if self.chrom != other.chrom:
            return False
        if self.size != other.size:
            return False
        if self.strand != other.strand:
            return False
        if self.loci != other.loci:
            return False
        return True


    def add_locus(self, locus, sort=True):
        """
        Add a locus to the Region.
        """
        try:
            assert self.chrom == locus.chrom, "Wrong chromosome"
            assert self.strand == locus.strand, "Wrong strand"
        except AssertionError:
            print("Chroms - self:", self.chrom, " Locus: ", locus.chrom,
                  "; Strands - self:", self.strand, " Locus:", locus.strand)
            raise

        self.loci.append(locus)

        if sort:
            self.__sort_loci()

        self.__update_size()

    def add_loci(self, loci):
        """
        Add multiple loci to the Region.
        """
        for locus in loci:
            self.add_locus(locus)


    def __str__(self):
        """
        Returns a string representation of the Region in RGN format.
        """
        locus_strs = []
        for locus in self.loci:
            locus_strs.append("%s..%s" % (locus.start, locus.stop))
        loci_str = ",".join(locus_strs)
        return "%s %s (%s) %s" % (self.name, self.chrom, loci_str, self.size)

class Locus(object):
    """
    A single genomic locus, defined here as a continuous stretch of sequence.

    Locus coordinates are 1-based and end-point inclusive.
    """
    def __init__(self, chrom, start, stop, strand=None):
        """
        Initialize a genomic locus.
        """
        chrom = format_chrom(chrom)
        start = int(start)
        stop = int(stop)

        try:
            assert chrom in CHROMS, "Wrong chromosome"
            assert start <= stop, "Start is greater than stop"
            assert strand in ["+", "-", None], "Unknown strand"
        except AssertionError:
            print("Chr:", chrom, "; Start:", start, "Stop: ", stop,
                  "Strand: ", strand)
            raise

        self.chrom = chrom
        self._start = start
        self._stop = stop
        self.strand = strand

        self.size = None
        self.__update_size()

        self.__chrom_index = CHROMS[self.chrom]

    def __gt__(self, other):
        """
        Greater than function for loci.
        """
        if self.__chrom_index == other.__chrom_index:
            return self.start > other.start
        return self.__chrom_index > other.__chrom_index

    def __lt__(self, other):
        """
        Less than function for loci.
        """
        if self.__chrom_index == other.__chrom_index:
            return self.start < other.start
        return self.__chrom_index < other.__chrom_index

    def __eq__(self, other):
        """
        Equality function for Locus.
        """
        return(self.chrom == other.chrom and
               self.start == other.start and
               self.stop == other.stop and
               self.strand == other.strand)

    @property
    def start(self):
        """
        Get or set the start coordinate of the Locus.
        """
        return self._start

    @start.setter
    def start(self, value):
        self._start = int(value)
        self.__update_size()

    @property
    def stop(self):
        """
        Get or set the stop coordinate of the Locus.
        """
        return self._stop

    @stop.setter
    def stop(self, value):
        self._stop = int(value)
        self.__update_size()

    def __update_size(self):
        """
        Update the Locus size.
        """
        self.size = self.stop - self.start + 1

class Regions(object):
    """
    Several genomic regions.
    """
    def __init__(self, regions_file=None):
        """
        Initialize a set of genomic regions.
        """
        self.regions = {}.fromkeys(CHROMS)
        for chrom in CHROMS:
            self.regions[chrom] = {}
        self.__len = 0

        if regions_file:
            self.__parse(regions_file)

    def __parse(self, regions_file):
        """
        Parse a file in the RGN format in the Region.
        """
        for line in regions_file:
            if line.startswith("#"):
                continue
            region = Region(line)
            self.add_region(region)
        return self

    def __len__(self):
        return self.__len


    def add_region(self, region):
        """
        Add a Region.
        """
        assert region.name not in self.regions[region.chrom], \
                "double region entry"

        self.regions[region.chrom][region.name] = region
        self.__len += 1


    def iterrgns(self):
        """
        Iterator over name, region.
        """
        for chrom in CHROMS:
            yield from self.regions[chrom].items()

    def _write_chrom(self, chrom, out_file):
        """
        Write single chromosome to file.
        """
        if self.regions[chrom] != {}:
            names = sorted(self.regions[chrom].keys())
            for name in names:
                region = self.regions[chrom][name]
                print(region, file=out_file)

    def write(self, handle):
        """
        Write Regions to file in RGN format.
        """
        for chrom in CHROMS:
            self._write_chrom(chrom, handle)

### Functions ------------------------------------------------------------------
def format_chrom(chrom):
    """
    Format chromosome name and return as string.

    Preceding "chr" is removed.
    """
    if isinstance(chrom, int):
        return str(chrom)

    chrom = chrom.replace("chr", "")
    if chrom == "M":
        chrom = "MT"

    assert chrom in CHROMS, "Unrecognized chromosome: {}".format(chrom)

    return chrom

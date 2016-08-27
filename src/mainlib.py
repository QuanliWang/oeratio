#!/usr/bin/env python3

"""
Purpose:  Main library for scripts.
Author:   Ayal Gussow, Quanli Wang
"""

### Imports --------------------------------------------------------------------
import sys
import argparse
import logging
import datetime
from oeratioGlobals import CustomFormatter

### Constants ------------------------------------------------------------------
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"

### Functions-------------------------------------------------------------------
def debug_func(error_type, value, error_tb):
    """
    Function for debugging with pdb.
    """
    if error_type != KeyboardInterrupt:
        print(error_type)
        print(value)
        import traceback
        traceback.print_tb(error_tb)
        import pdb
        pdb.pm()

### Classes --------------------------------------------------------------------
class Main(object):
    """
    Main class for use by scripts.

    Includes logging set-up and a run function intended for use
    when script is run directly from command line.
    """
    def __init__(self, parser=None, cmd=None,
                 log_level=LOG_LEVEL, log_format=LOG_FORMAT, desc=None):
        """
        Initializes standard script variables.

        <cmd>: command line for parser, usually sys.argv.
        """
        assert isinstance(cmd, list), "cmd must be list"

        self.start_time = datetime.datetime.now()
        self.cmd = cmd
        self.log_level = log_level
        self.log_format = log_format

        ## parse cmd args
        if parser:
            assert isinstance(parser, argparse.ArgumentParser)
            self.parser = parser
            # legacy mode where run() is overridden
            self.get_args()
            self.setup_logging()
        else:
            self.parser = argparse.ArgumentParser(
                description=desc, formatter_class=CustomFormatter)

    def __enter__(self):
        """
        Context management protocol. Returns self.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context management protocol.

        Logs run end. Returns 0.
        """
        ## end run
        run_time = datetime.datetime.now() - self.start_time
        logging.info("Run completed successfully in %s", run_time)

    def add_arguments(self):
        """override to add custom arguments for inherited class
        """
        pass

    def get_args(self):
        """parse the arguments from the ArgumentParser object
        """
        self.add_arguments()
        self.parser.add_argument(
            "--out", dest="out_file",
            help="the output file",
            type=argparse.FileType("w"),
            default=sys.stdout)
        self.parser.add_argument(
            "--log", dest="log_file",
            help="the output log",
            type=argparse.FileType("w"),
                            default=sys.stderr)
        self.args = self.parser.parse_args(self.cmd)

    def setup_logging(self):
        """set up logging
        """
        logging.basicConfig(stream=self.args.log_file,
                            format=self.log_format,
                            level=self.log_level)
        logging.info("Command: %s", " ".join(sys.argv))

    def work(self):
        """overwrite this function
        """
        pass

    def run(self, *args, **kwargs):
        """
        To be overridden.
        """
        self.get_args()
        self.setup_logging()
        self.work(*args, **kwargs)

### Debugger Settings ----------------------------------------------------------
sys.excepthook = debug_func

#!/usr/bin/env python3
import sys
import ncdistributerlib
import ncdistributerlib.docopt as docopt

class DistributeApp(ncdistributerlib.Distributor):
    __doc__ = """
{appname} Copyright (c) 2014 Nicholas Cole

This application will package a script for distribution.
Usage:
    {appname} <filename>...
    {appname} [--exclude-path=<path> --exclude-path=<path>] <filename>
    {appname} -h | --help

    """.format(appname=sys.argv[0])

    def run(self,):
        for fname in self.arguments['<filename>']:
            self.package(fname)
    
    
if __name__ == "__main__":
    arguments = docopt.docopt(DistributeApp.__doc__)
    A = DistributeApp(exclude_path_list=arguments["--exclude-path"])
    A.arguments = arguments
    A.run()

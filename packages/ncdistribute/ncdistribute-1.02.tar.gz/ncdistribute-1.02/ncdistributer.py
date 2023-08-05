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
    {appname} -h | --help

    """.format(appname=sys.argv[0])

    def run(self,):
        for fname in self.arguments['<filename>']:
            self.package(fname)
    
    
if __name__ == "__main__":
    A = DistributeApp()
    A.arguments = docopt.docopt(DistributeApp.__doc__)
    A.run()

from __future__ import print_function
import os
import sys
import logging
import argparse
from  bam2x import IO,TableIO,DBI
def help():
    return "pileup bed"
def set_parser(parser):
    #parser.add_argument("-m",type=str,choices=("seq","cDNA","cdna","cds","utr5","utr3"),dest="method")
    
    
def run(args):
    fin=IO.fopen(args.input,"r")
    out=IO.fopen(args.input,"w")

if __name__=="__main__":
    from bam2x.IO import parser_factory
    p=parser_factory(description=help())
    set_parser(p)
    if len(sys.argv)==1:
        print(p.print_help())
        exit(0)
    run(p.parse_args())








#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import logging
import argparse
from  bam2x import IO,TableIO,DBI
import itertools
def help():
    return "pileup bed according a tss ( or other one nt marker) coordinates"
def set_parser(parser):
    parser.add_argument("--x_start",type=int,dest="x_start",default=-500)
    parser.add_argument("--x_end",type=int,dest="x_end",default=500)
    parser.add_argument("-I","--format",type=str,dest="format",choices=("bed6","bed12"),default="bed12")
    parser.add_argument("-s","--score",dest="pileup_score",action="store_true",default=False,help="pile up the bed score")
    
    
def run(args):
    fin=IO.fopen(args.input,"r")
    out=IO.fopen(args.output,"w")
    p_values=[0.0 for i in xrange(args.x_start,args.x_end)]
    n_values=[0.0 for i in xrange(args.x_start,args.x_end)]
    offset=args.x_start
    length=len(p_values)
    for i in TableIO.parse(fin, args.format):
        if args.pileup_score:
            score=i.score
        else:
            score=1.0
        if i.strand=="+" or i.strand==".":
            for e in i.Exons():
                pos_start=e.start-offset
                pos_end=e.stop-offset
                for j in xrange(pos_start,pos_end):
                    if j<0: continue
                    if j>length-1: break
                    p_values[j]+=score
        elif i.strand=="-":
            for e in i.Exons():
                pos_start=e.start-offset
                pos_end=e.stop-offset
                for j in xrange(pos_start,pos_end):
                    if j<0: continue
                    if j>length-1: break
                    n_values[j]+=score
    for pos,pvalue,nvalue in itertools.izip(xrange(args.x_start,args.x_end),p_values,n_values):
        print("{pos}\t{p}\t{n}".format(pos=pos,p=pvalue,n=nvalue),file=out)


if __name__=="__main__":
    from bam2x.IO import parser_factory
    p=parser_factory(description=help())
    set_parser(p)
    if len(sys.argv)==1:
        print(p.print_help())
        exit(0)
    run(p.parse_args())


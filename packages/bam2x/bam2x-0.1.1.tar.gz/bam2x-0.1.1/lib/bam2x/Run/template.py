import os
import sys
import logging
import argparse
def help():
    return "template help"
def set_parser(parser):
    parser.add_argument("-m",type=str,choices=("seq","cDNA","cdna","cds","utr5","utr3"),dest="method")
    
    
def run(args):
    print "run template module now"
    print args








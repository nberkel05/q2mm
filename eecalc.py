import argparse
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

def main(args):
    renerg, senerg = get_data(args)
    rtotal, stotal = numdenom(args)
    if not rtotal:
        print 'S half of calculation is %f.' % stotal
    elif not stotal:
        print 'R half of calculation is %f.' % rtotal
    elif rtotal and stotal:
        ee = eecalc(args)
        rconfig, sconfig = config(args)
        if ee > 0:
            print 'Percent ee is %f (R)' % ee
        if ee < 0:
            print 'Percent ee is %f (S)' % (abs(ee))
        print 'R config is %f\nS config is %f' % (rconfig, sconfig)

def return_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    inps = parser.add_argument_group('input options')
    inps.add_argument(
        '--ren', '-r', type=str, nargs='+', metavar='somename.log',
        help='The .log file containing energies of the different r conformations.')
    inps.add_argument(
        '--sen', '-s', type=str, nargs='+', metavar='somename.log',
        help='The .log file containing energies of the different s conformations.')
    inps.add_argument(
        '--arbE', '-a', type=str, choices=['yes', 'no'], default = 'no',
        help='Arbitrary energy that is used in calculations. If yes, then min energy is taken as'
        'arb E. Default is no, which is 0.')
   # outs = parser.add_argument_group('output options')
   # outs.add_argument(
   #     '--output', '-o', type=str, metavar='somename.txt',
   #     help='Name of output file.') 
    return parser

def get_data(args):
    parser = return_parser()
    opts = parser.parse_args(args)
    # First, select the energies for just the -r files.
    if opts.ren:
        lines = []
        renerg = []
        for files in opts.ren:
            with open(files) as f:
                stuff = f.readlines()
                stuff = [line.split() for line in stuff]
                for i in stuff:
                    for j in i:
                        if j == 'Conformation':
                            lines.append(i)
        for i in lines:
            renerg.append(i[3])
        renerg = [float(i) for i in renerg]
        renerg = set(renerg)
    elif not opts.ren:
        renerg = None
    # Then, select the energies for just the -s files.
    if opts.sen:
        lines = []
        senerg = []
        for files in opts.sen:
            with open(files) as f:
                stuff = f.readlines()
                stuff = [line.split() for line in stuff]
                for i in stuff:
                    for j in i:
                        if j == 'Conformation':
                            lines.append(i)
        for i in lines:
            senerg.append(i[3])
        senerg = [float(i) for i in senerg]
        senerg = set(senerg)
    elif not opts.sen:
        senerg = None
    return renerg, senerg

def numdenom(args):
    parser = return_parser()
    opts = parser.parse_args(args)
    renerg, senerg = get_data(args)
    R = 0.008314  # kJ/mol
    T = 298  # K
    # Calculations use an arbitrary energy as reference. Default is 0. If yes, then
    # finds the lowest energy available from all select files.
    if opts.arbE == 'yes':
        if renerg != None and senerg != None:
            rarb = min(renerg)
            sarb = min(senerg)
            arb = min(rarb, sarb)
        elif renerg == None:
            arb = min(senerg)
        elif senerg == None:
            arb = min(renerg)
    elif opts.arbE == 'no':
        arb = 0
    rtotal = 0
    stotal = 0
    # rtotal and stotal are essentially part of the ee calculation in the 
    # eecalc function.
    if renerg:
        for i in renerg:
            e = i - arb
            exp = e/(R*T)
            gexp = np.exp(-exp)
            rtotal += gexp
    elif not renerg:
        rtotal = None
    if senerg:
        for i in senerg:
            e = i - arb
            exp = e/(R*T)
            gexp = np.exp(-exp)
            stotal += gexp
    elif not senerg:
        stotal = None
    return rtotal, stotal

def eecalc(args):
    # Finds the %ee here using data from numdenom.
    rtotal, stotal = numdenom(args)
    er = rtotal/stotal
    ee = (er - 1)/(er + 1) * 100
    return ee

def config(args):
    # Calculates the percentage that is in R and S conformations.
    ee = eecalc(args)
    rconfig = ee + (100 - ee)/2
    sconfig = (100 - ee)/2
    return rconfig, sconfig

if __name__ == '__main__':
    main(sys.argv[1:])

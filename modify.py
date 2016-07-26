import argparse
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

def main(args):
    parser = return_parser()
    opts = parser.parse_args(args)
    top, bottom, label, weight, rval, cval, score = get_data(args)
    if opts.job == 'torsions':
        cval = torsions(args)
    # ~~~ WRITE OUTPUT ~~~
    if opts.job == 'filter' or opts.job == 'torsions':
        data = [label, weight, rval, cval, score]
        with open(opts.output[0], 'w') as f:
            for x in top:
                f.write('{}\n'.format(' '.join(x)))
            for x in zip(*data):
                f.write('{0:<35} {1:>12} {2:>12} {3:>13} {4:>13}\n'.format(*x))
            for x in bottom:
                f.write('{}\n'.format(' '.join(x))) 
    elif opts.job == 'plot' or opts.job == 'scan':
        plot(args)
#    else:
#        for line in new_lines:
#            print(line)

def return_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    inps = parser.add_argument_group('input options')
#    inps.add_argument(
#        '--directory', '-d', type=str, metavar='somepath', default=os.getcwd(),
#        help=('Directory searched for files. Default is the current directory.'))
    inps.add_argument(
        '--text', '-t', type=str, metavar='somename.txt',
        help='The .txt file containing MM and QM data. Need to list this first.')
    inps.add_argument(
        '--job', '-j', type=str, choices=['filter', 'torsions', 'scan', 'plot'], default = 'plot',
        help='Selects job type. Filter .txt file with highest scoring parameter at top, '
        'plot a scan .txt file, or plot .txt file normally.')
    outs = parser.add_argument_group('output options')
    outs.add_argument(
        '--output', '-ot', type=str, nargs='+', metavar='somename.txt',
        help='Name of output file. If not given, prints.') 
    outs.add_argument(
        '--outplot', '-op', type=str, nargs='+', metavar='somename.png',
        help='Name of output plot. If not given, then the input somename.txt file is converted into' 
        'somename.png. This needs to be listed last.')
#    outs.add_argument(
#        '--doprint', '-p', action='store_true',
#        help=("Logs data. Can generate extensive log files."))
    return parser

def get_data(args):
    parser = return_parser()
    opts = parser.parse_args(args)
    file_name = sys.argv[2]
    with open(file_name) as f:
        stuff = f.readlines()
        stuff = [line.split() for line in stuff]
        top = stuff[:1]
        data = stuff[1:-5]
        bottom = stuff[-5:]
    label = []
    weight = []
    rval = []
    cval = []
    score = []
    # Need to sort or filter score here.
    if opts.job == 'filter':
        data.sort(key = lambda x: float(x[4]), reverse = True)
    for x in data:
        label.append(x[0])
        weight.append(x[1])
        rval.append(x[2])
        cval.append(x[3])
        score.append(x[4])
    rval = [float(i) for i in rval]
    cval = [float(i) for i in cval]
  #  score = [float(i) for i in score]
    return (top, bottom, label, weight, rval, cval, score)

def filename(args):
    # First need to grab the name of the text file.
    parser = return_parser()
    opts = parser.parse_args(args)
    txtfile = opts.text
    pre, ext = os.path.splitext(txtfile)
    # Now split text file name and make a list.
    # i.e. my/name/is_neil.txt becomes ['my','name','is','neil']
    n = pre.split('/')
    n = [i.split('_') for i in n]
    name = []
    for x in n:
        for y in x:
            name.append(y)
    last = name[-1:]
    name = name[:-1]
    last = [i.split('.') for i in last]
    name.append(last[0][0])
    return name, pre

def torsions(args):
    top, bottom, label, weight, rval, cval, score = get_data(args)
    for index,x in enumerate(cval):
        if x - rval[index] > 200:
            cval[index] -= 360
        elif rval[index] - x > 200:
            cval[index] += 360
    return cval

def variable(args):
    parser = return_parser()
    opts = parser.parse_args(args)
    top, bottom, label, weight, rval, cval, score = get_data(args)
    name, pre = filename(args)
    if (opts.job == 'plot') and ('tors' in name or 'torsions' in name):
        cval = torsions(args)
    par = np.polyfit(rval, cval, 1)
    slope = par[0]
    intercept = par[1]
    xl = [min(rval), max(rval)]
    yl = [slope*xx + intercept  for xx in xl]
    variance = np.var(cval)
    residuals = np.var([(slope*xx + intercept - yy)  for xx,yy in zip(rval,cval)])
    Rsqr = 1-residuals/variance
    return xl, yl, slope, intercept, Rsqr, cval

def plot(args):
    parser = return_parser()
    opts = parser.parse_args(args)
    name, pre = filename(args)
    top, bottom, label, weight, rval, cval, score = get_data(args)
    xl, yl, slope, intercept, Rsqr, cval = variable(args)
    '''
    The plot settings will differ from person to person. plt.plot function works
    as follows:
        x1, y1, color line style, x2, y2, ...
        b = blue; r = red; y = yellow; g = green; k = black
        o = circles; - = solid line; -- = dashes; ^ = triangles; s = squares
        hollow circle example:
            plot(var1, var2, facecolors='none', edgecolors='r')
    The annotations may need to be adjusted, especially the xy = (some, stuff) and
    xy text = (more, stuff).
    '''
    if opts.job == 'plot':
        plt.plot(rval, cval, 'bo', xl, yl, 'k-')
        total_score = float(bottom[4][1])
        if intercept >= 0:
            sign = '+'
        else:
            intercept = abs(intercept)
            sign = '-'
    # Annotate graph based on the type of plot wanted. Angles, bonds, etc. 
    # will give different annotations. User may have to change if statements
    # depending on what they name their files.
        if 'angles' in name:
            plt.xlabel('QM Bond Angles [o]')
            plt.ylabel('MM Bond Angles [o]')
            plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
                         % (slope, sign, intercept, Rsqr, total_score),
                         xy = (100, 100),
                         xycoords = 'data',
                         xytext = (60, 140),
                         textcoords = 'data',
                         )
        elif 'bonds' in name:
            plt.xlabel('QM Bonds Lengths [A]')
            plt.ylabel('MM Bonds Lengths [A]')
            plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
                         % (slope, sign, intercept, Rsqr, total_score),
                         xy = (1.0, 1.0),
                         xycoords = 'data',
                         xytext = (1.2, 1.7),
                         textcoords = 'data',
                         )
        elif 'eigs' in name:
            plt.xlabel('QM Eigenvalues [Some Units]')
            plt.ylabel('MM Eigenvalues [Some Units]')
            plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
                         % (slope, sign, intercept, Rsqr, total_score),
                         xy = (1000, 1000),
                         xycoords = 'data',
                         xytext = (1000, 10000),
                         textcoords = 'data',
                         )
        elif 'tors' in name or 'torsions' in name:
            plt.xlabel('QM Torsions [Some Units]')
            plt.ylabel('MM Torsions [Some Units]')
            plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
                         % (slope, sign, intercept, Rsqr, total_score),
                         xy = (100, 100),
                         xycoords = 'data',
                         xytext = (-150, 50),
                         textcoords = 'data',
                         )
        elif 'charges' in name:
            plt.xlabel('QM Charges [e?]')
            plt.ylabel('MM Charges [e?]')
            plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
                         % (slope, sign, intercept, Rsqr, total_score),
                         xy = (0, 0),
                         xycoords = 'data',
                         xytext = (-0.9, 0.4),
                         textcoords = 'data',
                         )
    elif opts.job == 'scan':
    # XX is the arbitrary x-axis in the scan plot. It will probably have to 
    # change for each type of scan.
        XX = []
        YY = np.arange(1.58, 2.00, 0.05)
        for x in YY:
            XX.append(round(x, 2))
        plt.plot(XX , cval, 'ro', XX, rval, 'bo') 
        plt.xlabel('Scan Parameter')
        plt.ylabel('Energy [kJ/mol]')
    # Title the plot based on the name of text file.
    plt.title(' '.join(map(str, name)))
    # Name of file saved into
    if opts.outplot:
        new_file = sys.argv[-1]
        plt.savefig(new_file)
    else:
        plt.savefig(pre + '.png')
#    plt.show()

if __name__ == '__main__':
    main(sys.argv[1:])

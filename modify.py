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

def return_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    inps = parser.add_argument_group('input options')
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
        help='Name of output file.') 
    outs.add_argument(
        '--outplot', '-op', type=str, nargs='+', metavar='somename.png',
        help='Name of output plot. If not given, then the input somename.txt file is converted into' 
        'somename.png. This needs to be listed last.')
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
    # Depending on if you want the intercept at 0 or not, comment correct line.
  #  intercept = par[1]
    intercept = 0
    xl = [min(rval), max(rval)]
    yl = [slope*xx + intercept for xx in xl]
    variance = np.var(cval)
    # Residuals and Rsqr are part of the normal calculations for the normal R**2.
    # Res and Rsqr2 are for if there is an additional line with a slope of 1.
    residuals = np.var([(slope*xx + intercept - yy)  for xx,yy in zip(rval,cval)])
    res = np.var([(xx - yy)  for xx,yy in zip(rval,cval)])
    Rsqr = 1-residuals/variance
    Rsqr2 = 1-res/variance
    return xl, yl, slope, intercept, Rsqr, Rsqr2, cval

def plot(args):
    parser = return_parser()
    opts = parser.parse_args(args)
    name, pre = filename(args)
    top, bottom, label, weight, rval, cval, score = get_data(args)
    xl, yl, slope, intercept, Rsqr, Rsqr2, cval = variable(args)
    '''
    The plot settings will differ from person to person. plt.plot function works
    as follows:
        x1, y1, color line style, x2, y2, ...
        b = blue; r = red; y = yellow; g = green; k = black
        o = circles; - = solid line; -- = dashes; ^ = triangles; s = squares
        hollow circle example:
            plot(var1, var2, 'o', mec='b', mfc='none')
    The annotations may need to be adjusted, especially the xy = (some, stuff) and
    xy text = (more, stuff) lines.
    '''
    if opts.job == 'plot':
        # The next two lines are for plotting the additional line mentioned in the 
        # previous function.
       # slopeofone = [[min(rval),max(rval)],[min(rval),max(rval)]]
       # plt.plot(slopeofone[0], slopeofone[1], 'r--')
        plt.plot(rval, cval, 'o', mec='b', mfc='none')
        plt.plot(xl, yl, 'k-')
        total_score = float(bottom[4][1])
        # Corrects the sign on the intercept.
        if intercept >= 0:
            sign = '+'
        else:
            intercept = abs(intercept)
            sign = '-'
        # Annotate graph based on the type of plot wanted. Angles, bonds, etc. 
        # will give different annotations. User may have to change 'if' statements
        # depending on what they name their files.
        # Also, the commented lines are for correcting the axis dimensions if needed,
        # and for including/not including the intercept and score.
        if 'angles' in name:
	   # plt.axis([40,190,40,190])
            plt.xlabel('QM Bond Angles [$^\circ$]')
            plt.ylabel('MM Bond Angles [$^\circ$]')
           # plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
           #              % (slope, sign, intercept, Rsqr, total_score),
            plt.annotate('y = %.3fx\n$\mathrm{R^2}$ = %.3f'
                         % (slope, Rsqr),
                         xy = (100, 100),
                         xycoords = 'data',
                         xytext = (70, 140),
                         textcoords = 'data',
                         )
        elif 'bonds' in name:
	   # plt.axis([1,2,1,2])
            plt.xlabel('QM Bonds Lengths [$\AA$]')
            plt.ylabel('MM Bonds Lengths [$\AA$]')
           # plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
           #              % (slope, sign, intercept, Rsqr, total_score),
            plt.annotate('y = %.3fx\n$\mathrm{R^2}$ = %.3f'
                         % (slope, Rsqr),
                         xy = (1.0, 1.0),
                         xycoords = 'data',
                         xytext = (1.2, 1.7),
                         textcoords = 'data',
                         )
        elif 'charges' in name:
	   # plt.axis([-1,1,-1,1])
            plt.xlabel('QM Charges [e]')
            plt.ylabel('MM Charges [e]')
            plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
                         % (slope, sign, intercept, Rsqr, total_score),
           # plt.annotate('y = %.3fx\n$\mathrm{R^2}$ = %.3f'
           #              % (slope, Rsqr),
                         xy = (0, 0),
                         xycoords = 'data',
                         xytext = (-0.9, 0.1),
                         textcoords = 'data',
                         )
            # For Neil's use. Puts another red line on plot.
           # plt.annotate('y = x\n$\mathrm{R^2}$ = %.3f'
           #              % (Rsqr2),
           #              color = 'r',
           #              xy = (0, 0),
           #              xycoords = 'data',
           #              xytext = (-0.6, -0.9),
           #              textcoords = 'data',
           #              )
        elif 'eigs' in name:
	   # plt.axis([-500,5500,-7000,25000])
            plt.xlabel('QM Eigenvalues [kJ / mol$\cdot\AA^2$]')
            plt.ylabel('MM Eigenvalues [kJ / mol$\cdot\AA^2$]')
            plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
                         % (slope, sign, intercept, Rsqr, total_score),
           # plt.annotate('y = %.3fx\n$\mathrm{R^2}$ = %.3f'
           #              % (slope, Rsqr),
                         xy = (1000, 1000),
                         xycoords = 'data',
                         xytext = (1000, 7500),
                         textcoords = 'data',
                         )
        elif 'hessian' in name or 'hes' in name:
	   # plt.axis([0,8000,0,8000])
            plt.xlabel('QM Hessian Elements [Some Units]')
            plt.ylabel('MM Hessian Elements [Some Units]')
            plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
                         % (slope, sign, intercept, Rsqr, total_score),
           # plt.annotate('y = %.3fx\n$\mathrm{R^2}$ = %.3f'
           #              % (slope, Rsqr),
                         xy = (-1000, 1000),
                         xycoords = 'data',
                         xytext = (-2000, 1000),
                         textcoords = 'data',
                         )
            # For Neil's use. Puts another red line on plot.
           # plt.annotate('y = x\n$\mathrm{R^2}$ = %.3f'
           #              % (Rsqr2),
           #              color = 'r',
           #              xy = (0, 0),
           #              xycoords = 'data',
           #              xytext = (-2500, -4000),
           #              textcoords = 'data',
           #              )
        elif 'tors' in name or 'torsions' in name:
	   # plt.axis([-200,200,-350,350])
            plt.xlabel('QM Torsions [$^\circ$]')
            plt.ylabel('MM Torsions [$^\circ$]')
            plt.annotate('y = %.3f x %s %.3f\n$R^2$ = %.3f\nScore = %f'
                         % (slope, sign, intercept, Rsqr, total_score),
           # plt.annotate('y = %.3fx\n$\mathrm{R^2}$ = %.3f'
           #              % (slope, Rsqr),
                         xy = (100, 100),
                         xycoords = 'data',
                         xytext = (-140, 50),
                         textcoords = 'data',
                         )
    elif opts.job == 'scan':
        # XX is the arbitrary x-axis in the scan plot. It will probably have to 
        # change for each type of scan.
        XX = []
        # This is where you include the x-axis values. (start, end, step)
        YY = np.arange(179.9, 128.9, -2.0)  # bend
       # YY = np.arange(90, 106, 1.0)  # cpbend
       # YY = np.arange(1.58, 2.00, 0.05)  # stretch
       # YY = np.arange(0, 73, 3)  # twist
        for x in YY:
            XX.append(round(x, 2))
        line1, = plt.plot(XX , cval, 'ro')  # MM is red
        line2, = plt.plot(XX, rval, 'bo')  # QM is blue
        # plt.axis is same as in 'plot' section. If not included, it is 
        # automatically fitted to data.
       # plt.axis([125,185,-150,375])  # bend1
       # plt.axis([125,185,-175,500])  # bend2
       # plt.axis([88,107,-30,55])  # cpbend
       # plt.axis([1.55,2.0,-25,40])  # stretch
       # plt.axis([-3,75,-1.5,2.0])  # twist1
       # plt.axis([-3,75,-2,2])  # twist2
        # Legend. loc=1 is upper right corner, loc=2 is upper left corner, etc.
        plt.legend([line1, line2], ['MM Energies', 'QM Energies'], loc=1)
        # Might want to change the xlabel depending on your scan.
        plt.xlabel('Scan Parameter')
       # plt.xlabel('D1-z1 Bond Distance [$\AA^2$]')  # bonds
       # plt.xlabel('D1-z1-D1 Bond Angle [$^\circ$]')  # angles
       # plt.xlabel('CR-D1-D1-CR Torsion [$^\circ$]')  # torsions
        plt.ylabel('Energy [kJ/mol]')
        # Title the plot based on the name of text file.
        plt.title(' '.join(map(str, name)))
    # Name of file saved into.
    if opts.outplot:
        new_file = sys.argv[-1]
        plt.savefig(new_file)
    else:
        plt.savefig(pre + '.png')
   # plt.show()

if __name__ == '__main__':
    main(sys.argv[1:])

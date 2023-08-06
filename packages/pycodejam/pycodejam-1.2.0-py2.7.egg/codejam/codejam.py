from __future__ import print_function
'''
  Code Jam Problem Runner Utility

  Author: Jon Eisen
  Dec 2012

'''

import sys
import argparse
from os import path

def parmap(f, args, workers):
  from multiprocessing import Pool
  pool = Pool(processes=workers)
  results = [pool.apply_async(f, arg) for arg in args]
  return [r.get() for r in results]

class CodeJam:

  '''
  A class that provides ways to easily run a code jam problem

  The class requires two parameters to instantiate:
  parser - A generator function of one parameter (file_obj) that yields each case in a tuple. There are predominant parsers and helpful decorators in the parsers module
  solver - A solver that takes the case tuple expanded and returns a str()-able object to print as the answer

  The usual way to use this class is to call the main() function which will interpret command line arguments
  for the input file and options for debugging (-d)

  name - Something to add to the help statement
  floating_accuracy - digits of precision for floating point numbers
  include_case - Include the "Case #n: " for each case
  '''

  def __init__(self, parser, solver, name="Generic CodeJam Problem", floating_accuracy=6, include_case=True):
    self.name = name
    self.parse = parser
    self.solve = solver
    self.facc = floating_accuracy
    self.include_case = include_case

  def outans(self, ans):
    if type(ans) == float:
      return ('%%.%df' % self.facc) % ans
    else:
      return str(ans)

  def output(self, i, ans):
    oans = self.outans(ans)
    if self.include_case:
      return "Case #%d: %s" % (i, oans)
    else:
      return oans

  def run(self, inf, outf, debug=False, silent=False):
    '''
    Run the CodeJam runner with file objects inf and outf and options for debug and silent
    '''
    debug = debug and (not silent)

    for i, case in enumerate(self.parse(inf)):
      if debug:
        print("Case #%d Input: %s" % (i+1, str(case)))

      ans = self.solve(*case)
      output = self.output(i+1, ans)

      if not silent:
        print(output)

      print(output, file=outf)

  def run_multiproc(self, inf, outf, debug=False, silent=False, workers=4):
    '''
    Run the CodeJam runner utility as multiprocessing with a default of 4 workers
    '''
    from multiprocessing import Pool

    debug = debug and (not silent)

    args = list(self.parse(inf))
    if not silent:
      print("Offloading work to %d subprocesses" % workers)
    if debug:
        print("Inputs: %s" % str(args))

    results = parmap(self.solve, args, workers=workers)

    for i, case, ans in zip(range(len(args)),args,results):
      if debug:
        print("Case #%d Input: %s" % (i+1, str(case)))

      output = self.output(i+1, ans)

      if not silent:
        print(output)

      print(output, file=outf)

  def main(self, argv=None):
    '''
    Run the CodeJam runner utility from the command line
    '''
    if not argv:
      argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description='Run a %s.' % self.name)
    parser.add_argument('input', metavar='FILE', type=str, 
      help='input file (A-small-practice.in for example)')
    parser.add_argument('-o','--output', metavar='FILE', type=str, default=None,
      help='output file (defaults to input_file.out)')
    parser.add_argument('-d','--debug', action='store_true', default=False,
      help='Add some debug output')
    parser.add_argument('-q','--quiet', action='store_true', default=False,
      help='Quiet all output to stdout')
    parser.add_argument('-m','--multiproc', action='store_true', default=False,
      help="Enable multiprocessing")
    parser.add_argument('-w','--workers',type=int, action='store', default=4,
      help='Number of workers to use if multiprocessing', metavar='N')

    args = parser.parse_args(argv)
    
    if not args.output:
      args.output = ''.join(args.input.split('.')[:-1]) + '.out'

    inf = open(args.input, 'r')
    outf = open(args.output, 'w')

    if args.multiproc:
      self.run_multiproc(inf, outf, debug=args.debug, silent=args.quiet, workers=args.workers)
    else:
      self.run(inf, outf, debug=args.debug, silent=args.quiet)
#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Dec  2 12:38:08 CET 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import facereclib
import argparse
import os
import pkg_resources

def command_line_options(command_line_parameters = None):
  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-d', '--databases', nargs='+', choices = ('mobio', 'scface'), default = ('mobio', 'scface'),
      help = 'The databases to run experiments on.')

  parser.add_argument('-p', '--protocols', nargs='+', choices = ('combined', 'close', 'medium', 'far', 'male', 'female'), default = ('combined', 'close', 'medium', 'far', 'male', 'female'),
      help = 'The protocols to run; the protocols will automatically assigned to the according database.')

  parser.add_argument('-c', '--combined-zt-norm', action = 'store_true',
      help = 'If selected, the ZT norm will use all distance conditions in the cohort (only valid for database SCface)')

  parser.add_argument('-q', '--dry-run', action = 'store_true',
      help = 'Writes the actual call to the facereclib instead of executing it')

  parser.add_argument('-T', '--temp-directory', default = 'temp',
      help = "The output directory for temporary files.")

  parser.add_argument('-R', '--result-directory', default = 'results',
      help = "The output directory for result files.")

  parser.add_argument('parameters', nargs = argparse.REMAINDER,
      help = "Parameters directly passed to the face verify script. Use -- to separate this parameters from the parameters of this script. See 'bin/faceverify.py --help' for a complete list of options.")

  # add verbosity command line option
  facereclib.utils.add_logger_command_line_option(parser)
  # parse command line
  args = parser.parse_args(command_line_parameters)
  # set verbosity level
  facereclib.utils.set_verbosity_level(args.verbose)

  # return command line arguments
  return args


PROTOCOLS = {
  'scface' : ('combined', 'close', 'medium', 'far'),
  'mobio'  : ('male', 'female')
}


def main():
  args = command_line_options(sys.argv[1:])
  # get the directory, where the configuration files are stored
  config_dir = os.path.dirname(pkg_resources.resource_filename('xfacereclib.paper.IET2014', 'execute.py'))

  # iterate over all desired databases
  for database in args.databases:
    # iterate over all protocols ...
    for protocol in args.protocols:
      # ... that fit to the database
      if protocol in PROTOCOLS[database]:
        # compute sub-directory for the experiments based on command line options
        sub_directory = 'combined' if args.combined_zt_norm or database != 'scface' else protocol
        # get the correct database setup for the desired experiment
        db = 'c-%s-%s' % (database, sub_directory) if database == 'scface' else 'c-%s' % database
        # collect the parameters that will be sent to the bin/faceverify.py script,
        # which will finally execute the experiments
        parameters = ['./bin/faceverify.py',
                      '--database', db,
                      '--protocol', protocol if database == 'scface' else 'mobile0-%s' % protocol,
                      '--preprocessing', 'tan-triggs' if database == 'mobio' else 'face-crop',
                      '--features', os.path.join(config_dir, 'dct_%s.py' % database),
                      '--tool', os.path.join(config_dir, 'isv_%s.py' % database),
                      '--preprocessed-data-directory', '../combined/preprocessed',
                      '--features-directory', '../combined/features',
                      '--projector-file', '../combined/ISV-Projector.hdf5',
                      '--projected-features-directory', '../combined/projected',
                      '--temp-directory', os.path.join(args.temp_directory, database),
                      '--result-directory', os.path.join(args.result_directory, database),
                      '--sub-directory', sub_directory,
                      '--groups', 'dev', 'eval', '--zt-norm', '--calibrate-scores']

        # set the verbosity level
        if args.verbose:
          parameters.append('-' + 'v'*args.verbose)

        # add the command line arguments that were specified on command line
        if args.parameters:
          parameters.extend(args.parameters[1:])

        if args.dry_run:
          # Write what we would have executed
          print "Would have executed:"
          print " ".join(parameters)
        else:
          # Write what we will execute
          print "Launching:"
          print " ".join(parameters)
          # execute the face recognition algorithm
          facereclib.script.faceverify.main(parameters)



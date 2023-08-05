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

import bob
import facereclib
import argparse
import os

from .utils import evaluate_scores


def command_line_options(command_line_parameters = None):
  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-d', '--databases', nargs='+', choices = ('mobio', 'scface'), default = ('mobio', 'scface'),
      help = 'The databases to run experiments on.')

  parser.add_argument('-p', '--protocols', nargs='+', choices = ('combined', 'close', 'medium', 'far', 'male', 'female'), default = ('combined', 'close', 'medium', 'far', 'male', 'female'),
      help = 'The protocols to run; the protocols will automatically assigned to the according database.')

  parser.add_argument('-c', '--combined-zt-norm', action = 'store_true',
      help = 'If selected, the ZT norm will use all distance conditions in the cohort (only valid for database SCface, and without --combined-threshold)')

  parser.add_argument('-x', '--combined-threshold', action = 'store_true',
      help = 'If selected, the threshold will be based on all distance conditions (only valid for database SCface, and without --combined-zt-norm')

  parser.add_argument('-R', '--result-directory', default = 'results',
      help = "The output directory for result files.")

  parser.add_argument('-w', '--latex-directory', default = 'latex',
      help = "Change the directory into which the exported LaTeX file is written")

  facereclib.utils.add_logger_command_line_option(parser)

  # parse command line options
  args = parser.parse_args(command_line_parameters)
  facereclib.utils.set_verbosity_level(args.verbose)

  # return command line options
  return args


PROTOCOLS = {
  'scface' : ('combined', 'close', 'medium', 'far'),
  'mobio'  : ('male', 'female')
}


def main():
  args = command_line_options()

  # iterate over the desired databases
  for database in args.databases:
    # compute the directory of the scores based on the given directory
    score_dir = os.path.join(args.result_directory, database)
    # iterate over all protocols ...
    for protocol in args.protocols:
      # ... that are suitable for the current database
      if protocol in PROTOCOLS[database]:
        # get the real name of the protocol
        dev_protocol = 'combined' if args.combined_threshold else 'mobile0-%s' % protocol if database == 'mobio' else protocol
        eval_protocol = 'mobile0-%s' % protocol if database == 'mobio' else protocol
        # compute the real input directories based on the command line options
        dev_result_dir = os.path.join(score_dir, 'combined' if args.combined_threshold or database != 'scface' else protocol, 'scores', dev_protocol)
        eval_result_dir = os.path.join(score_dir, 'combined' if args.combined_zt_norm or database != 'scface' else protocol, 'scores', eval_protocol)

        # check that the result directories already exist
        if not os.path.exists(dev_result_dir):
          raise IOError("The result directory '%s' does not exist. Check your parameters!" % dev_result_dir)
        if not os.path.exists(eval_result_dir):
          raise IOError("The result directory '%s' does not exist. Check your parameters!" % eval_result_dir)

        # read score files and collect results
        results = {}
        results_at_zero = {}
        facereclib.utils.info("Evaluating scores in directories %s and %s" %(dev_result_dir, eval_result_dir))
        # collect results for both normalization types
        for norm in ('nonorm', 'ztnorm'):
          # collect results for raw and calibrated scores
          for type in ('scores', 'calibrated'):
            facereclib.utils.debug("Evaluating scores of type %s using norm %s" % (type, norm))

            neg_dev, pos_dev = bob.measure.load.split_four_column(os.path.join(dev_result_dir, norm, '%s-dev'%type))
            neg_eval, pos_eval = bob.measure.load.split_four_column(os.path.join(eval_result_dir, norm, '%s-eval'%type))

            # compute performances
            Cver_min_dev, Cver_min_eval, Cver_eval, Cver_0_dev, Cver_0_eval, Pfr_dev, Pfr_eval, Cllr_dev, Cllr_eval, Cllr_min_dev, Cllr_min_eval = evaluate_scores(neg_dev, pos_dev, neg_eval, pos_eval)

            # collect results
            results[norm+"-"+type] = (Cver_min_dev, Cver_min_eval, Cver_eval, Cllr_dev, Cllr_min_dev, Cllr_eval, Cllr_min_eval, Pfr_dev, Pfr_eval)
            results_at_zero[norm+"-"+type] = (Cver_0_dev, Cver_0_eval)


        # write LaTeX compatible file with results
        facereclib.utils.ensure_dir(args.latex_directory)
        latex_file = os.path.join(args.latex_directory, "%s_%s%s.tex" % (database, protocol, '-zt' if args.combined_zt_norm else '-thres' if args.combined_threshold else ''))
        with open(latex_file, 'w') as f:
          # write HUGE macro for verification and calibration results
          f.write("% Cver_min-dev(no) Cver_min-eval(no) Cver-eval(no) Pfr-dev(no) Pfr-eval(no) Cver_min-dev(ZT) Cver_min-eval(ZT) Cver-eval(ZT) Pfr-dev(ZT) Pfr-eval(ZT) \n% Cllr_min-eval(no) Cllr-eval-before(no) Cmc-eval-before(no) Cllr-eval-after(no) Cmc-eval-after(no) Cllr_min-eval(ZT) Cllr-eval-before(ZT) Cmc-eval-before(ZT) Cllr-eval-after(ZT) Cmc-eval-after(ZT) \n")
          f.write("\\Result{%3.2f}{%3.2f}{%3.2f}{%3.2f}{%3.2f} {%3.2f}{%3.2f}{%3.2f}{%3.2f}{%3.2f}  {%1.3f}{%1.3f}{%1.3f}{%1.3f}{%1.3f} {%1.3f}{%1.3f}{%1.3f}{%1.3f}{%1.3f}\n" % (
            # Cver verification performance for raw scores
            results['nonorm-scores'][0] * 100.,
            results['nonorm-scores'][1] * 100.,
            results['nonorm-scores'][2] * 100.,

            # Pfr verification performance for raw scores
            results['nonorm-scores'][7] * 100.,
            results['nonorm-scores'][8] * 100.,

            # Cver verification performance for ZT-normalized scores
            results['ztnorm-scores'][0] * 100.,
            results['ztnorm-scores'][1] * 100.,
            results['ztnorm-scores'][2] * 100.,

            # Pfr verification performance for ZT-normalized scores
            results['ztnorm-scores'][7] * 100.,
            results['ztnorm-scores'][8] * 100.,


            # Cllr_min for raw scores
            results['nonorm-scores'][6],
            # Cllr and Cmc for raw scores (does not make much sense, though)
            results['nonorm-scores'][5],
            results['nonorm-scores'][5] - results['nonorm-scores'][6],
            # Cllr and Cmc for calibrated raw scores
            results['nonorm-calibrated'][5],
            results['nonorm-calibrated'][5] - results['nonorm-calibrated'][6],

            # Cllr_min for ZT-normalized scores
            results['ztnorm-scores'][6],
            # Cllr and Cmc for ZT-normalized scores (nonsense)
            results['ztnorm-scores'][5],
            results['ztnorm-scores'][5] - results['ztnorm-scores'][6],
            # Cllr and Cmc for calibrated ZT-normalized scores
            results['ztnorm-calibrated'][5],
            results['ztnorm-calibrated'][5] - results['ztnorm-calibrated'][6]

            )
          )

          # write results at threshold 0 before and after calibration in an extra macro
          f.write("% Cver-dev(no) Cver-eval(no) Cver-dev(ZT) Cver-eval(ZT)   Cver-dev-cal(no) Cver-eval-cal(no) Cver-dev-cal(ZT) Cver-eval-cal(ZT)\n")
          f.write("\\ResultAtZero{%3.2f}{%3.2f}{%3.2f}{%3.2f} {%3.2f}{%3.2f}{%3.2f}{%3.2f}\n" % (
            # before calibration
            results_at_zero['nonorm-scores'][0] * 100.,
            results_at_zero['nonorm-scores'][1] * 100.,
            results_at_zero['ztnorm-scores'][0] * 100.,
            results_at_zero['ztnorm-scores'][1] * 100.,

            # after calibration
            results_at_zero['nonorm-calibrated'][0] * 100.,
            results_at_zero['nonorm-calibrated'][1] * 100.,
            results_at_zero['ztnorm-calibrated'][0] * 100.,
            results_at_zero['ztnorm-calibrated'][1] * 100.

            )
          )

          facereclib.utils.info("Wrote LaTeX-compatible file %s\n" % latex_file)

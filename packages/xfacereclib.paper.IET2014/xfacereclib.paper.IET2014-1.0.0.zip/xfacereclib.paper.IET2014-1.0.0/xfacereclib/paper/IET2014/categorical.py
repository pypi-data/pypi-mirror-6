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
import numpy
import facereclib
import argparse
import os

from .utils import split_score_file, evaluate_scores

def command_line_options(command_line_parameters = None):
  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

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

def apply_on_score_file(machine, infile, outfile):
  """Applies the given linear machine to the scores in the given input file and generate the given output file."""
  # read the input score files
  columns = bob.measure.load.four_column(infile)
  facereclib.utils.debug("Calibrating scores from file %s to file %s" % (infile, outfile))
  with open(outfile, 'w') as w:
    # iterate over the lines of the input score file
    for line in columns:
      # extract the distance from the probe file name
      distance = int(line[2].split('/')[0][-1]) - 1
      # arrange score to be used in categorical calibration
      score = numpy.array([line[3], distance==0, distance==1, distance==2], numpy.float64)
      if machine.weights.shape[0] == 1:
        # only a single weight => linear calibration
        calibrated = machine(score[:1])
      else:
        # more than one weight (should be 4 here) => categorical calibration
        calibrated = machine(score)
      # write the calibrated score
      w.write("%s %s %s %s\n" % (line[0], line[1], line[2], str(calibrated[0])))


def main():
  args = command_line_options()

  # read the raw score files
  score_dir = os.path.join(args.result_directory, 'scface', 'combined', 'scores', 'combined', 'ztnorm')
  facereclib.utils.info("Reading score files %s and %s" % (os.path.join(score_dir, 'scores-dev'), os.path.join(score_dir, 'scores-eval')))
  dev_scores = split_score_file(os.path.join(score_dir, 'scores-dev'))
  eval_scores = split_score_file(os.path.join(score_dir, 'scores-eval'))

  # arrange development set scores to perform categorical calibration
  sorted_scores = []
  for scores in dev_scores:
    data = numpy.hstack([scores[0], scores[1], scores[2]])
    line1 = numpy.hstack([numpy.ones(len(scores[0])), numpy.zeros(len(scores[1])), numpy.zeros(len(scores[2]))])
    line2 = numpy.hstack([numpy.zeros(len(scores[0])), numpy.ones(len(scores[1])), numpy.zeros(len(scores[2]))])
    line3 = numpy.hstack([numpy.zeros(len(scores[0])), numpy.zeros(len(scores[1])), numpy.ones(len(scores[2]))])
    sorted_scores.append(numpy.vstack([data, line1, line2, line3]))

  facereclib.utils.info("Calibrating scores")
  # create the Linear Logistic Regressor from Bob
  llr_trainer = bob.trainer.CGLogRegTrainer(0.5, 1e-16, 100000)
  # perform linear calibration using only the score data
  facereclib.utils.debug("Linear calibration")
  linear_machine = llr_trainer.train(sorted_scores[0][0:1].T, sorted_scores[1][0:1].T)
  # perform categorical calibration using the arranged score data
  facereclib.utils.debug("Categorical calibration")
  categorical_machine = llr_trainer.train(sorted_scores[0].T, sorted_scores[1].T)

  # Write the calibrated score files for development and evaluation set since we'll need them for plotting
  apply_on_score_file(linear_machine, os.path.join(score_dir, 'scores-dev'), os.path.join(score_dir, 'scores-dev-linear'))
  apply_on_score_file(linear_machine, os.path.join(score_dir, 'scores-eval'), os.path.join(score_dir, 'scores-eval-linear'))
  apply_on_score_file(categorical_machine, os.path.join(score_dir, 'scores-dev'), os.path.join(score_dir, 'scores-dev-categorical'))
  apply_on_score_file(categorical_machine, os.path.join(score_dir, 'scores-eval'), os.path.join(score_dir, 'scores-eval-categorical'))

  # compute raw, linear and categorical calibrated scores
  all_scores = {'none':{}, 'linear':{}, 'categorical':{}}
  for group, group_scores in (('dev', dev_scores), ('eval', eval_scores)):
    for t in all_scores: all_scores[t][group] = {}
    for type, scores in (('neg', group_scores[0]), ('pos', group_scores[1])):
      # raw scores
      all_scores['none'][group][type] = [s for d in scores for s in d]
      # linear calibrated scores
      all_scores['linear'][group][type] = numpy.array([s[0] for d in scores for s in linear_machine(d.reshape((d.shape[0],1)))])
      # categorically calibrated scores
      all_scores['categorical'][group][type] = numpy.array([categorical_machine(numpy.array([s, i==0, i==1, i==2], numpy.float64))[0] for i,d in enumerate(scores) for s in d])


  # compute performance for the three different types of calibrations
  for cal in all_scores:
    facereclib.utils.debug("Evaluating calibrated scores with type %s" % cal)
    # scores
    neg_dev = all_scores[cal]['dev']['neg']
    pos_dev = all_scores[cal]['dev']['pos']
    neg_eval = all_scores[cal]['eval']['neg']
    pos_eval = all_scores[cal]['eval']['pos']

    # compute performances for the current calibration type
    Cver_min_dev, Cver_min_eval, Cver_eval, Cver_0_dev, Cver_0_eval, Pfr_dev, Pfr_eval, Cllr_dev, Cllr_eval, Cllr_min_dev, Cllr_min_eval = evaluate_scores(neg_dev, pos_dev, neg_eval, pos_eval)

    # create output directory if needed
    facereclib.utils.ensure_dir(args.latex_directory)
    # write results in LaTeX-compatible format
    latex_file = os.path.join(args.latex_directory, "calibration-%s.tex" % cal)
    with open(latex_file, 'w') as f:
      # write header
      f.write("% Cver_min-dev Cver_min-eval Cver-eval Cllr_min-dev Cllr-dev Cmc-dev Cllr_min-eval Cllr-eval Cmc-eval\n")
      # write \Result macro
      f.write("\\Result{%3.2f}{%3.2f}{%3.2f} {%1.3f}{%1.3f}{%1.3f} {%1.3f}{%1.3f}{%1.3f}\n" % (
        Cver_min_dev * 100.,
        Cver_min_eval * 100.,
        Cver_eval * 100.,

        Cllr_min_dev,
        Cllr_dev,
        Cllr_dev - Cllr_min_dev,

        Cllr_min_eval,
        Cllr_eval,
        Cllr_eval - Cllr_min_eval,
        )
      )

      # write second macro with results threshold 0 and at FAR 1 %
      f.write("% Cver-dev Cver-eval at threshold 0; Pfr-dev and Pfr-eval at FAR 1%\n")
      f.write("\\ResultAt{%3.2f}{%3.2f} {%3.2f}{%3.2f}\n" % (
        Cver_0_dev * 100.,
        Cver_0_eval * 100.,
        Pfr_dev * 100.,
        Pfr_eval * 100.
        )
      )

      facereclib.utils.info("Wrote LaTeX-compatible file %s\n" % latex_file)

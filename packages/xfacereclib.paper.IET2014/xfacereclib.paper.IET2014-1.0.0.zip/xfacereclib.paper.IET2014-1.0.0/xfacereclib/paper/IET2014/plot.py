#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Wed Dec  4 11:24:11 CET 2013
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
import argparse
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy
import scipy.stats
import facereclib

from .utils import split_score_file

def command_line_options(command_line_parameters = None):
  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-F', '--figure', type=int, choices=(3,4), required=True,
      help = "Select the figure that you want to generate")
  parser.add_argument('-R', '--result-directory', default = 'results',
      help = "The directory where the result files are stored.")
  parser.add_argument('-w', '--output-file',
      help = "The output directory for result files.")

  facereclib.utils.add_logger_command_line_option(parser)

  # parse command line options
  args = parser.parse_args(command_line_parameters)
  facereclib.utils.set_verbosity_level(args.verbose)

  # return arguments
  return args


def plot(negatives, positives, figure, dashed, legend=None, xlabel=None):
  """Plots distributions of the given negative and positive scores into the given figure using kernel density estimation."""
  # compute the densities
  neg_density = scipy.stats.gaussian_kde(negatives)
  pos_density = scipy.stats.gaussian_kde(positives)

  # get density estimates
  first = min(min(negatives), min(positives))
  last = max(max(negatives), max(positives))
  x = numpy.arange(first, last, (last-first)/100.)
  neg = neg_density(x)
  pos = pos_density(x)

  # define line color and style based on parameters
  line_style = ':' if dashed == 2 else '--' if dashed == 1 else '-'
  colors = ['r', 'b']

  # plot curves
  plt.plot(x, pos, line_style, color=colors[1], linewidth=6)
  plt.plot(x, neg, line_style, color=colors[0], linewidth=3)

  # enable vertical grid only
  figure.axes.xaxis.grid(True)

  # add y label by default
  plt.ylabel('density')


def main():
  args = command_line_options()

  if args.figure == 3:
    # define input score directories based on the given directory
    mobio_score_dir = os.path.join(args.result_directory, 'mobio', 'combined', 'scores', 'mobile0-male')
    scface_score_dir = os.path.join(args.result_directory, 'scface', 'combined', 'scores', 'combined')

    # load score files for both databases
    facereclib.utils.info("Loading score files for Figure 3")
    files = ['nonorm/scores-eval', 'ztnorm/scores-eval', 'nonorm/calibrated-eval', 'ztnorm/calibrated-eval']
    mobio_scores = [bob.measure.load.split_four_column(os.path.join(mobio_score_dir, d)) for d in files]
    scface_scores = [bob.measure.load.split_four_column(os.path.join(scface_score_dir, d)) for d in files]

    # create figure in larger size
    figure = plt.figure(figsize=(17,12))

    # define sub-plots in a grid setup
    grid = gridspec.GridSpec(2,2)
    grid.update(left=0.06, right=0.97, top=0.97, bottom=0.06, wspace=0.3, hspace=0.4)
    inner_grid = gridspec.GridSpecFromSubplotSpec(2,1, subplot_spec=grid[0,0])

    # plot uncalibrated MOBIO distributions
    f = plt.subplot(inner_grid[0,0])
    plot(mobio_scores[0][0], mobio_scores[0][1], f, dashed=0)
    plt.ylim((0,5))
    f = plt.subplot(inner_grid[1,0])
    plot(mobio_scores[1][0], mobio_scores[1][1], f, dashed=1)
    plt.ylim((0,0.14))
    plt.yticks((0,0.1))
    plt.xlabel('Uncalibrated MOBIO male scores')

    # plot calibrated MOBIO distributions
    f = plt.subplot(grid[0, 1])
    plot(mobio_scores[2][0], mobio_scores[2][1], f, dashed=0)
    plot(mobio_scores[3][0], mobio_scores[3][1], f, dashed=1)
    plt.ylim((0,0.2))
    plt.yticks((0,0.1,0.2))
    plt.legend(['client, raw','impostor, raw','client, ZT-norm','impostor, ZT-norm'])
    plt.xlabel('Calibrated MOBIO male LLR scores')

    # plot uncalibrated SCface distributions
    f = plt.subplot(grid[1,0])
    plot(scface_scores[0][0], scface_scores[0][1], f, dashed=0)
    plot(scface_scores[1][0], scface_scores[1][1], f, dashed=1)
    plt.xlim((-3,10))
    plt.ylim((0,2))
    plt.yticks((0,1,2))
    plt.xlabel('Uncalibrated SCface combined scores')

    # plot calibrated SCface distributions
    f = plt.subplot(grid[1,1])
    plot(scface_scores[2][0], scface_scores[2][1], f, dashed=0)
    plot(scface_scores[3][0], scface_scores[3][1], f, dashed=1)
    plt.xlim((-8,17))
    plt.ylim((0,0.4))
    plt.yticks((0,0.2,0.4))
    plt.xlabel('Calibrated SCface combined LLR scores')

    # write resulting plot to file
    filename = args.output_file if args.output_file is not None else "Figure_3.pdf"
    plt.savefig(filename)
    facereclib.utils.info("Wrote plot for Figure 3 into file %s" % filename)

  if args.figure == 4:

    # score directory for the SCface scores of Figure 4
    score_dir = os.path.join(args.result_directory, 'scface', 'combined', 'scores', 'combined', 'ztnorm')

    # load score files for both databases
    facereclib.utils.info("Loading score files for Figure 4")
    files = ['scores-eval', 'scores-eval-linear', 'scores-eval-categorical']

    # create figure in larger size
    figure = plt.figure(figsize=(10,12))
    # define sub-figures
    grid = gridspec.GridSpec(3,1)
    grid.update(left=0.09, right=0.97, top=0.97, bottom=0.06, wspace=0.3, hspace=0.4)

    # plot uncalibrated scface distributions
    f = plt.subplot(grid[0,0])
    scores = split_score_file(os.path.join(score_dir, files[0]))
    plot(scores[0][2], scores[1][2], f, dashed=0)
    plot(scores[0][1], scores[1][1], f, dashed=1)
    plot(scores[0][0], scores[1][0], f, dashed=2)
    plt.xlim((-3,10))
    plt.ylim((0,0.5))
    plt.xlabel('Uncalibrated scores')
    plt.legend(['client, close','impostor, close','client, medium','impostor, medium','client, far', 'impostor, far'], prop={'size':15})

    # plot linearly calibrated scface distributions
    f = plt.subplot(grid[1,0])
    scores = split_score_file(os.path.join(score_dir, files[1]))
    plot(scores[0][2], scores[1][2], f, dashed=0)
    plot(scores[0][1], scores[1][1], f, dashed=1)
    plot(scores[0][0], scores[1][0], f, dashed=2)
    plt.xlim((-8,17))
    plt.ylim((0,0.3))
    plt.yticks((0,0.1,0.2,0.3))
    plt.xlabel('Linear calibrated LLR scores')

    # plot categorically calibrated scface distributions
    f = plt.subplot(grid[2,0])
    scores = split_score_file(os.path.join(score_dir, files[2]))
    plot(scores[0][2], scores[1][2], f, dashed=0)
    plot(scores[0][1], scores[1][1], f, dashed=1)
    plot(scores[0][0], scores[1][0], f, dashed=2)
    plt.xlim((-8,17))
    plt.ylim((0,0.3))
    plt.yticks((0,0.1,0.2,0.3))
    plt.xlabel('Categorical calibrated LLR scores')

    # write resulting plot to file
    filename = args.output_file if args.output_file is not None else "Figure_4.pdf"
    plt.savefig(filename)
    facereclib.utils.info("Wrote plot for Figure 4 into file %s" % filename)


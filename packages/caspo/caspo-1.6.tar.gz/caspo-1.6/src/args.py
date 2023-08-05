#!python
# Copyright (c) 2012-2013, Santiago Videla, Sven Thiele, CNRS, INRIA, EMBL
#
# This file is part of caspo.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caspo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.import random
# -*- coding: utf-8 -*-
import argparse
import math

VERSION = '1.6'

def fit_tolerance(string):
    value = float(string)
    allowed = 0.5
    
    if value > allowed or value < 0:
        msg = "%s. Allowed values are: 0 <= F <= %s" % (value, allowed)
        raise argparse.ArgumentTypeError(msg)
        
    return value

def size_tolerance(string):
    value = int(string)
    
    if value < 0:
        msg = "%s. Allowed values are: 0 <= S" % value
        raise argparse.ArgumentTypeError(msg)
        
    return value
    
def truncate_fn(fn):
    functions = {
        'round': round,
        'floor': math.floor,
        'ceil': math.ceil
    }
    if not functions.has_key(fn):
        msg = "%s. Allowed values are: %s" % (fn,functions.keys())
        raise argparse.ArgumentTypeError(msg)
        
    return functions[fn]
    
def get_learn_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("pkn",
                        help="Prior knowledge network in SIF format")

    parser.add_argument("midas",
                        help="Experimental dataset in MIDAS file")
    
    parser.add_argument('--version', action='version', version='caspo version ' + VERSION)
    
    parser.add_argument("--fit", dest="fit", type=fit_tolerance, default=0.,
                        help="suboptimal enumeration tolerance (Default to 0)", metavar="F")
                      
    parser.add_argument("--size", dest="size", type=size_tolerance, default=0,
                        help="suboptimal size enumeration tolerance (Default to 0). Combined with --fit could lead to a huge number of models", 
                        metavar="S")

    parser.add_argument("--discrete", dest="discrete", type=int, default=100, choices=[1, 10, 100, 1000],
                        help="discretization over [0,D] (Default to 100)", metavar="D")

    parser.add_argument("--truncate", dest="trunc", default='round', type=truncate_fn,
                        help="trunction function: round, floor, ceil (Default to round)", metavar="T")
                        
    parser.add_argument("--max-and", dest="max_and", type=int, default=0,
                        help="maximum length for AND gates (Dafault to # of predecessors)", metavar="L")

    parser.add_argument("--gtts", dest="gtts", type=int, choices=[1,2,3], metavar="V",
                        help="compute Global Truth Tables with verbose levels. This could take some time for many models.")

    parser.add_argument("--mutual", dest="mutual", action='store_true',
                        help="compute mutual exclusive/inclusive (Default to False). This could take some time for many models.")

    parser.add_argument("--cross", dest="cross", nargs=2, type=int,
                        help="compute N random K-fold cross validation", metavar=('N', 'K'))
                        
    parser.add_argument("--clasp", dest="clasp", type=argparse.FileType('r'),
                        help="text file containing custom clasp's parameters", metavar="C")

    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")
                                                
    args = parser.parse_args()
    
    return args
    
def get_control_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("models",
                        help="family of models in csv format")

    parser.add_argument("scenarios",
                        help="intervention scenarios in csv format")
                        
    parser.add_argument('--version', action='version', version='caspo version ' + VERSION)
    
    parser.add_argument("--max-size", dest="max_size", type=int, default=0,
                        help="maximum size for interventions strategies (Default to unlimited)", metavar="M")

    parser.add_argument("--allow-constraints", dest="iconstraints", action='store_true',
                        help="allow intervention over side constraints (Default to False)")
                        
    parser.add_argument("--allow-goals", dest="igoals", action='store_true',
                        help="allow intervention over goals (Default to False)")
        
    parser.add_argument("--out", dest="outdir", default='.',
                        help="output directory path (Default to current directory)", metavar="O")

    args = parser.parse_args()
    
    return args

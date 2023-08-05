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
import sys, os, csv
from __caspo__ import args, utils, BooleanFamily, Controller, MultiScenario

if __name__ == '__main__':
    arguments = args.get_control_args()

    print '\nReading input files...'
    models = csv.DictReader(open(arguments.models, 'rbU'))
    scenarios = csv.DictReader(open(arguments.scenarios, 'rbU'))
    
    family = BooleanFamily.from_matrix(models)
    controller = Controller(family)

    scenarios = MultiScenario(scenarios, arguments.igoals, arguments.iconstraints)
    
    print '\nLooking for intervention strategies with ASP...'
    
    def feedback(strategies):
        sys.stdout.write("\r%s minimal intervention strategies have been found." % len(strategies))
        sys.stdout.flush()
        
    strategies = controller.control(scenarios, arguments.max_size, feedback=feedback)
    print '\n'
    
    strategies.sort(key=len)
    writer = utils.Writer(arguments.outdir)
    writer.write(strategies.to_matrix(), 'strategies.csv', strategies.variables)

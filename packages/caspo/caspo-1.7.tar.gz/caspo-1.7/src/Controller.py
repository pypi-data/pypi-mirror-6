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
import os

from __caspo__ import Strategy, Strategies
from asp import control_prg, _
from pyasp.asp import Term, TermSet, GringoHClasp

class Controller(object):
    """
    :param family: :class:`__caspo__.BooleanFamily.BooleanFamily` instance
    """
    def __init__(self, family):
        self.family = family
        
    def control(self, scenarios, max_size=0, feedback=None):
        """
        Finds all minimal intervention strategies for the given scenarios
        
        :param scenarios: :class:`__caspo__.Scenario.MultiScenario` instance
        :param max_size: int
        :param function feedback: function to be called after parsing each strategy during search
        
        :returns: :class:`__caspo__.Strategy.Strategies` instance
        """
        instance = scenarios.termset(self.family.pkn.nodes).union(self.family.termset())
        
        strategies = Strategies(self.family.pkn.nodes)
        def cb(ts):
            strategies.append(Strategy.from_termset(filter(lambda t: t.nb_args() == 2, ts)))
            if feedback:
                feedback(strategies)
                
        self.__control__(instance, max_size, cb)
        
        return strategies
        
    def __control__(self, instance, max_size, cb=None):
        prg = [instance.to_file(), control_prg]
        solver = GringoHClasp(gringo_options='-c max=%s' % max_size, clasp_options='--enum-mode record')
        interventions = solver.run(prg, nmodels=0, collapseTerms=False, collapseAtoms=False, callback=cb)
        os.unlink(prg[0])
        
        return interventions

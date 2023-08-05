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
from asp import _
from pyasp.asp import Term, TermSet

class Scenario(object):
    """
    Intervention scenario
    
    :param dict goals: nodes names as keys and assigments (1,0,-1) as values
    :param dict constraints: nodes names as keys and assigments (1,0,-1) as values
    :param bool igoals: allow or not goal nodes in the intervention strategies
    :param bool iconstraints: allow or not constrained nodes in the intervention strategies
    """
    def __init__(self, goals, constraints, igoals, iconstraints):
        self.goals = goals
        self.constraints = constraints
        
        self.forbidden = set()
        if not igoals:
            self.forbidden = self.forbidden.union(self.goals.keys())
        
        if not iconstraints:    
            self.forbidden = self.forbidden.union(self.constraints.keys())
        
    def termset(self, i=1):
        """
        Returns the TermSet representation
        
        :param int i: scenario ID
        
        :returns: TermSet
        """
        ts = TermSet()

        ts.add(Term('scenario',[i]))
        for n,s in self.goals.iteritems():
            ts.add(Term('goal', [i,_(n),s]))
            
        for n,s in self.constraints.iteritems():
            ts.add(Term('constrained', [i,_(n),s]))
            
        return ts

class MultiScenario(list):
    """
    List of intervention scenarios
    
    :param DictReader scenarios: intervention scenarios
    :param bool igoals: allow or not goal nodes in the intervention strategies
    :param bool iconstraints: allow or not constrained nodes in the intervention strategies
    """
    def __init__(self, scenarios, igoals=False, iconstraints=False):
        super(MultiScenario, self).__init__()
        species = scenarios.fieldnames
        constraints = map(lambda name: name[3:], filter(lambda name: name.startswith('SC:'), species))
        goals = map(lambda name: name[3:], filter(lambda name: name.startswith('SG:'), species))
        
        self.forbidden = set()
        for row in scenarios:
            const = {}
            for c in constraints:
                if row['SC:' + c] != '0':
                    const[c] = int(row['SC:' + c])
                 
            goal = {}
            for g in goals:
                if row['SG:' + g] != '0':
                    goal[g] = int(row['SG:' + g])

            scenario = Scenario(goal,const,igoals,iconstraints)    
            self.forbidden = self.forbidden.union(scenario.forbidden)    
            self.append(scenario)
            
    def termset(self, variables):
        """
        Returns TermSet representation
        
        :param iterator variables: existing nodes in the logical networks
        
        :returns: TermSet
        """
        ts = TermSet()
        
        for i, scenario in enumerate(self):
            ts = ts.union(scenario.termset(i+1))
            
        for x in variables.difference(self.forbidden):
            ts.add(Term('candidate', [_(x)]))
            
        return ts

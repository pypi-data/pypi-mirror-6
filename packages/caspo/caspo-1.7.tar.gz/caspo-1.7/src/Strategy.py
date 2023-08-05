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

class Strategy(object):
    """
    Intervention strategy
    
    :param dict interventions: nodes names as keys and assigments (1,-1) as values
    """
    def __init__(self, interventions):
        self.interventions = dict(interventions)
    
    @classmethod
    def from_termset(cls, termset):
        """
        Constructor from a TermSet
        
        :param TermSet termset: TermSet from pyasp
        
        :returns: :class:`__caspo__.Strategy`
        """
        interventions = []
        for t in termset:
            interventions.append((t._arg(0),t.arg(1)))
        
        return cls(interventions)
        
    def vector(self, v=None):
        """
        Converts the Strategy to a plain vector (dict)
        
        :param dict v: optional vector to be updated
        
        :returns: dict with nodes names as keys and assigments (1,-1) as values
        """
        if v == None:
            v = {}
        
        v.update(self.interventions)
        return v

    def __len__(self):
        return len(self.interventions)
        

class Strategies(list):
    """
    List of intervention strategies
    :param iterator variables: existing nodes in the logical networks
    :param list strategies: optional existing list of strategies
    """
    def __init__(self, variables, strategies=[]):
        super(Strategies, self).__init__(strategies)
        self.variables = variables
        
    def to_matrix(self):
        """
        Returns an iterator over all strategies in the list as vectors (key-value: node name-{1,0,-1})
        
        :returns: iterator
        """
        vector = {}
        
        vector = dict.fromkeys(self.variables, 0)            
        for strategy in self:
            v = vector.copy()
            v = strategy.vector(v)
            yield v

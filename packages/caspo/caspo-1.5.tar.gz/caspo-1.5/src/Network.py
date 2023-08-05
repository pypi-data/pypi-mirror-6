# Copyright (c) 2012-2013, Santiago Videla, Sven Thiele, CNRS, INRIA, EMBL
#
# This file is part of caspo.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BioASP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BioASP.  If not, see <http://www.gnu.org/licenses/>.import random

# -*- coding: utf-8 -*-

from itertools import chain, combinations
from collections import defaultdict

from pyasp.asp import TermSet, Term
from asp import _

from __caspo__ import BooleanModel, Conjunction, Node

class Network(object):
    """
    :param sif_file: SIF filepath
    """
    def __init__(self, sif_file, max_and=0, open=open):
        self.nodes = set()
        self.edges = set()
        self.hyperedges = []
                
        f = open(sif_file, 'rbU')
        preds = defaultdict(list)
        for line in f:
            line.replace('\r\n','\n')
            source, sign, target = line[:-1].split('\t')
            self.nodes.add(source)
            self.nodes.add(target)
            self.edges.add((source,target,sign))
            preds[target].append((source,sign))
        
        for k,v in preds.iteritems():
            if max_and > 0:
                mv = min(max_and,len(v))
            else:
                mv = len(v)
                
            for subset in chain.from_iterable(combinations(v, r+1) for r in xrange(mv)):
                if self.__valid_dnf__(subset):
                    nodes = map(lambda (n,s): Node(n,int(s)), subset)
                    self.hyperedges.append(Conjunction(nodes,k))
        
        self.hyperedges.sort(key=len)
        self._em = BooleanModel(self.hyperedges)

    def termset(self):
        """
        Returns TermSet
        
        :returns: TermSet
        """
        network = TermSet()
        for node in self.nodes:
            network.add(Term('vertex', [_(node)]))
            
        for source, target, sign in self.edges:
            network.add(Term('edge', [_(source), _(target), sign]))
        
        for i,(k,cs) in enumerate(self._em.iteritems()):
            network.add(Term('formula', [_(k),i+1]))
            for c in cs:
                j = self.hyperedges.index(c)
                network.add(Term('hyperedge', [i+1,j+1,len(c)]))
                network = network.union(c.termset(j+1))

        return network
        
    def __valid_dnf__(self, subset):
        d = defaultdict(list)
        for v,s in subset:
            d[v].append(s)
        
        for k,v in d.iteritems():    
            if len(v) > 1:
                return False

        return True

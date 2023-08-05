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

import operator

from asp import _
from pyasp.asp import Term, TermSet

class Node(object):
    """
    :param name: node name
    :param sign: node sign (-1 or 1)
    
    >>> from __caspo__ import Node
    >>> n = Node('p38', 1)
    >>> print n
    p38
    >>> n = Node('p38', -1)
    >>> print n
    !p38
    """
    def __init__(self, name, sign):
        self.name = name
        self.sign = sign
        
    @classmethod
    def from_str(cls, string):
        """
        Constructor from a string
        
        :param string: the signed node string representation
        :returns: :class:`__caspo__.Conjunction.Node`
        
        >>> from __caspo__ import Node
        >>> n = Node.from_str('!Hsp27')
        >>> print n.name
        Hsp27
        >>> n.sign
        -1
        >>> n = Node.from_str('Hsp27')
        >>> print n.name
        Hsp27
        >>> n.sign
        1
        """
        sign = 1
        name = string
        if string[0] == '!':
            sign = -1
            name = string[1:]
        
        return cls(name, sign)
        
    def __str__(self):
        if self.sign == 1:
            return self.name
        else:
            return '!' + self.name
            
    def __eq__(self, other):
        return self.name == other.name and self.sign == other.sign
            
class Conjunction(object):
    """
    :param sources: list of :class:`__caspo__.Conjunction.Node` instances
    :param target: target node name
    
    >>> from __caspo__ import Node, Conjunction
    >>> c = Conjunction([Node('p38',1), Node('TNFa',-1)], 'Hsp27')
    >>> len(c)
    2
    >>> print c
    !TNFa+p38=Hsp27
    """
    def __init__(self, sources, target):
        self.sources = sources
        self.sources.sort(key=operator.attrgetter('name','sign'))
        self.target = target

    @classmethod
    def from_termset(cls, clauses, target):
        """
        Constructor from a PyASP TermSet of clauses and a target node name
        
        :param clauses: PyASP TermSet instance
        :param target: target node name
        :returns: :class:`__caspo__.Conjunction`
        
        >>> from pyasp.asp import Term, TermSet
        >>> from __caspo__ import Conjunction
        >>> ts = TermSet([Term('clause', [1,'"p38"',1]), Term('clause',[1,'"traf6"',-1])])
        >>> c = Conjunction.from_termset(ts,'Hsp27')
        >>> print c
        p38+!traf6=Hsp27
        """
        sources = []
        for term in clauses:
            sources.append(Node(term._arg(1), term.arg(2)))
                
        return cls(sources, target)
        
    @classmethod
    def from_term(cls, dnf, pkn):
        """
        Constructor from a PyASP Term and a PKN instance
        
        :param term: PyASP Term instance
        :param pkn: :class:`__caspo__.Network` instance
        :returns: :class:`__caspo__.Conjunction`
        
        >>> from pyasp.asp import Term
        >>> from StringIO import StringIO
        >>> from __caspo__ import Conjunction, Network
        >>> net = Network(None, open=lambda n,m: StringIO('a\\t1\\tc\\nb\\t-1\\tc\\n'))
        
        >>> t = Term('dnf', [1,3])
        >>> c = Conjunction.from_term(t, net)
        >>> c == net.hyperedges[3-1]
        True
        """
        return pkn.hyperedges[dnf.arg(1) - 1]
        
    @classmethod
    def from_str(cls, string):
        """
        Constructor from a string representation
        
        :param string: string representation of a conjunction
        :returns: :class:`__caspo__.Conjunction`
        
        >>> from __caspo__ import Conjunction
        >>> c1 = Conjunction.from_str('p38+traf6=Hsp27')
        >>> c2 = Conjunction.from_str('!AKT=Hsp27')
        >>> len(c1)
        2
        >>> len(c2)
        1
        >>> print [str(s) for s in c1.sources], c1.target
        ['p38', 'traf6'] Hsp27
        >>> print [str(s) for s in c2.sources], c2.target
        ['!AKT'] Hsp27
        """
        sources, target = string.split('=')
        sources = sources.split('+')
        nodes = []
        for node in sources:
            nodes.append(Node.from_str(node))

        return cls(nodes, target)
        
    def resolve(self, model, inputs, setup):
        """
        Resolve the Boolean value under the given inputs.
        
        :param model: :class:`__caspo__.BooleanModel` instance
        :param inputs: mapping of node names to bool values describing experimental condition
        :param setup: :class:`__caspo__.Dataset.Setup` instance
        :returns: bool
        
        >>> from __caspo__ import Conjunction, BooleanModel, Setup
        >>> setup = Setup(['TNFa', 'TGFa'], [], ['Hsp27'])
        >>> c = Conjunction.from_str('TNFa+TGFa=Hsp27')
        >>> b = BooleanModel([c])
        >>> c.resolve(b, {'TNFa':True, 'TGFa':False}, setup)
        False
        >>> c.resolve(b, {'TNFa':True, 'TGFa':True}, setup)
        True
        """        
        value = True
        i = 0
        while(value and i < len(self.sources)):
            node = self.sources[i]
            if node.sign == 1:
                value = value and model.resolve(node.name, inputs, setup)
            else:
                value = value and not model.resolve(node.name, inputs, setup)
                
            i += 1
            
        return value
    
    def termset(self, cc):
        """
        Converts the Conjunction instance to a TermSet instance
    
        :param cc: ID to identify this conjunction as a set of clauses
        :returns: TermSet
    
        >>> from __caspo__ import Conjunction
        >>> c = Conjunction.from_str('p38+!traf6=Hsp27')
        >>> ts = c.termset(1)
        >>> clauses = [str(c) for c in ts]
        >>> clauses.sort()
        >>> print clauses #doctest: +NORMALIZE_WHITESPACE
        ['clause(1,"p38",1)', 'clause(1,"traf6",-1)']
        """
        termset = TermSet()
        for l in self.sources:
            termset.add(Term('clause',[cc,_(l.name),l.sign]))
            
        return termset
    
    def __len__(self):
        return len(self.sources)
        
    def __str__(self):
        s = str(self.sources[0])
        for node in self.sources[1:]:
            s = s + '+' + str(node)
        
        s = s + '=' + self.target
        return s
        
    def __eq__(self, other):
        return self.target == other.target and self.sources == other.sources
        
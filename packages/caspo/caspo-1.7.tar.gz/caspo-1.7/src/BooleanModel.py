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
from pyasp.asp import TermSet, Term

from asp import _
from Conjunction import Conjunction

class BooleanModel(object):
    """
    :param conjunctions: an iterable of :class:`__caspo__.Conjunction` instances
    
    >>> from __caspo__ import Conjunction, BooleanModel
    >>> c1 = Conjunction.from_str('p38+traf6=Hsp27')
    >>> c2 = Conjunction.from_str('!AKT=Hsp27')
    >>> b = BooleanModel([c1,c2])
    >>> b.has_conjunction(c1)
    True
    >>> b.targets('Hsp27')
    True
    >>> len(b['Hsp27'])
    2
    """
    def __init__(self, conjunctions):
        self.__mapping = {}
        for c in conjunctions:
            if not self.__mapping.has_key(c.target):
                self.__mapping[c.target] = []
            
            self.__mapping[c.target].append(c)
            
        self.__conjunctions = conjunctions
        
    @classmethod
    def from_termset(cls, termset, pkn):
        """
        Constructor from a PyASP TermSet instance and a PKN instance
        
        :param termset: PyASP TermSet of conjunctions
        :param pkn: :class:`__caspo__.Network` instance
        :returns: :class:`__caspo__.BooleanModel`
                
        >>> from pyasp.asp import TermSet, Term
        >>> from __caspo__ import BooleanModel, Network
        >>> from StringIO import StringIO
        >>> fake_file = StringIO('a\\t1\\tc\\nb\\t-1\\tc\\n')
        >>> net = Network(None, open=lambda n,m: fake_file)
        
        >>> c1 = Term('dnf', [1,2])
        >>> c2 = Term('dnf', [1,3])
        >>> b = BooleanModel.from_termset(TermSet([c1,c2]), net)
        >>> [str(c) for c in b['c']]
        ['!b=c', 'a+!b=c']
        """
        conjunctions = map(lambda dnf: Conjunction.from_term(dnf,pkn), termset)
        return cls(conjunctions)
        
    @classmethod
    def from_vector(cls, vector):
        """
        Constructor from a vector representation
        
        :param vector: A mapping describing key-value pairs like ('conjunction=target',{'0','1'})
        :returns: :class:`__caspo__.BooleanModel`
        
        >>> from __caspo__ import BooleanModel
        >>> b = BooleanModel.from_vector({'TNFa=CREB': '0', '!AKT=Hsp27': '1', 'p38+traf6=Hsp27': '1'})
        >>> [str(c) for c in b['Hsp27']]
        ['!AKT=Hsp27', 'p38+traf6=Hsp27']
        """
        conjunctions = []
        for k,v in vector.iteritems():
            if int(v) == 1:
                conjunctions.append(Conjunction.from_str(k))
                
        return cls(conjunctions)

    def resolve(self, node, inputs, setup):
        """
        Resolve the Boolean value for a node under the given inputs.
        
        :param node: the name of the node to resolve
        :param inputs: mapping of node names to bool values describing experimental condition
        :param setup: :class:`__caspo__.Dataset.Setup` instance
        :returns: bool
        
        >>> from __caspo__ import Conjunction, BooleanModel, Setup
        >>> setup = Setup(['TNFa', 'TGFa'], [], ['Hsp27'])
        >>> c = Conjunction.from_str('TNFa+TGFa=Hsp27')
        >>> b = BooleanModel([c])
        >>> b.resolve('Hsp27', {'TNFa':True, 'TGFa':False}, setup)
        False
        >>> b.resolve('Hsp27', {'TNFa':True, 'TGFa':True}, setup)
        True
        """
        if (node in setup.stimuli) or (node in setup.inhibitors and inputs.has_key(node)):
            return inputs[node]
        elif not self.targets(node):
            return False
        else:
            value = False
            for c in self[node]:
                value = value or c.resolve(self, inputs, setup)

            return value

    def mse(self, dataset, testing=[]):
        """
        Compute Mean Squared Error with respect to a given dataset
        
        :param dataset: A instance of :class:`__caspo__.Dataset`
        :param testing: Optional list of experiments indices (useful for cross-validation)
        :returns: float
        
        First, we create a fake dataset containing 2 simple experiments
        
        >>> from __caspo__ import Dataset, Experiment, Conjunction, BooleanModel
        >>> e0 = Experiment({'TNFa':1}, {10: {'Hsp27':1}})
        >>> e1 = Experiment({'TNFa':0}, {10: {'Hsp27':1}})
        >>> dataset = Dataset([e0, e1], ['TNFa'], [], ['Hsp27'], 10)
        
        Now, we create a Boolean model and compute its MSE

        >>> from __caspo__ import Conjunction, BooleanModel
        >>> c = Conjunction.from_str('TNFa=Hsp27')
        >>> b = BooleanModel([c])
        >>> b.mse(dataset)
        0.5
        >>> b.mse(dataset, [0])
        0.0
        >>> b.mse(dataset, [1])
        1.0
        """
        rss = 0.
        obs = 0
        if len(testing) > 0:
            data = (dataset[i] for i in testing)
        else:
            data = dataset
            
        for exp in data:
            inputs = exp.boolean_input(dataset.setup)
            outputs = exp.outputs[dataset.time_point]
            
            for readout, value in outputs.iteritems():
                val = int(self.resolve(readout, inputs, dataset.setup))

                rss = rss + pow(value - val, 2)
                obs = obs + 1

        return rss / obs
        
    def termset(self, fidx, cidx, idm=1):
        """
        Converts the Boolean model instance to a TermSet instance
        
        :param fidx: 
        :param cidx:
        :param idm:
        :returns: TermSet
        
        >>> from __caspo__ import Conjunction, BooleanModel, Network
        >>> from StringIO import StringIO
        >>> fake_file = StringIO('a\\t1\\tc\\nb\\t1\\tc\\nd\\t-1\\tc\\n')
        >>> net = Network(None, open=lambda n,m: fake_file)

        >>> c1 = Conjunction.from_str('a+b=c')
        >>> c2 = Conjunction.from_str('!d=c')
        >>> fidx = [set([net.hyperedges.index(c1),net.hyperedges.index(c2)])]
        >>> b = BooleanModel([c1,c2])
        >>> ts = b.termset(fidx, net.hyperedges, 1)
        
        >>> conjunctions = [str(c) for c in ts]
        >>> conjunctions.sort()
        >>> print conjunctions # doctest: +NORMALIZE_WHITESPACE
        ['clause(3,"d",-1)', 'clause(4,"a",1)', 'clause(4,"b",1)', 'dnf(1,3)', 'dnf(1,4)', 'formula("c",1)', 'model(1,1)']
        """
        termset = TermSet()
        for t, cs in self.iteritems():
            cclist = list()
            for c in cs:
                cclist.append(cidx.index(c))
                
            ff = fidx.index(set(cclist)) + 1
            termset.add(Term('formula',[_(t), ff]))
            termset.add(Term('model', [idm, ff]))
            
            for i,c in enumerate(cs):
                cc = cclist[i] + 1
                termset.add(Term('dnf', [ff,cc]))
                termset = termset.union(c.termset(cc))
        
        return termset
        
    def has_conjunction(self, conjunction):
        """
        Returns whether the conjunction is present or not in the model
        
        :param conjunction: :class:`__caspo__.Conjunction` instance
        :returns: bool
        
        >>> from __caspo__ import Conjunction, BooleanModel
        >>> c1 = Conjunction.from_str('p38+traf6=Hsp27')
        >>> c2 = Conjunction.from_str('!AKT=Hsp27')
        >>> c3 = Conjunction.from_str('p38+traf6=Hsp27')
        >>> b = BooleanModel([c1])
        >>> b.has_conjunction(c1)
        True
        >>> b.has_conjunction(c2)
        False
        >>> b.has_conjunction(c3)
        True
        """
        if self.targets(conjunction.target):
            return conjunction in self[conjunction.target]
        else:
            return False
        
    def vector(self, v=None):
        """
        Converts the Boolean model instance to a vector representation.
        
        :param v: An optional mapping to overwrite.
        :returns: dict
        
        >>> from __caspo__ import Conjunction, BooleanModel
        >>> c1 = Conjunction.from_str('p38+traf6=Hsp27')
        >>> c2 = Conjunction.from_str('!AKT=Hsp27')
        >>> b = BooleanModel([c1,c2])
        >>> b.vector()
        {'!AKT=Hsp27': 1, 'p38+traf6=Hsp27': 1}
        >>> v = {'!AKT=Hsp27': 0, 'p38+traf6=Hsp27': 0, 'TNFa=CREB': 0}
        >>> b.vector(v)
        {'TNFa=CREB': 0, '!AKT=Hsp27': 1, 'p38+traf6=Hsp27': 1}
        >>> print v
        {'TNFa=CREB': 0, '!AKT=Hsp27': 1, 'p38+traf6=Hsp27': 1}
        """
        if v == None:
            v = {}
            
        for t, cs in self.iteritems():
            for c in cs:
                v[str(c)] = 1
                
        return v
        
    @property
    def conjunctions(self):
        """
        Read-only access to the list of conjunctions in the model
        
        :returns: list
        
        >>> from __caspo__ import Conjunction, BooleanModel, Setup
        >>> c = Conjunction.from_str('TNFa+TGFa=Hsp27')
        >>> b = BooleanModel([c])
        >>> [str(c) for c in b.conjunctions]
        ['TGFa+TNFa=Hsp27']
        """
        return self.__conjunctions
        
    def targets(self, node):
        """
        Returns whether the given node is a target in the model
        
        :param node: node name
        :returns: bool
        
        >>> from __caspo__ import Conjunction, BooleanModel
        >>> c = Conjunction.from_str('TNFa+TGFa=Hsp27')
        >>> b = BooleanModel([c])
        >>> b.targets('Hsp27')
        True
        >>> b.targets('p38')
        False
        """
        return self.__mapping.has_key(node)
        
    def iteritems(self):
        """
        Proxy to standard iteritems function over mapping objects.
        
        :returns: iterator of key-value pairs like: (target-node, conjunctions list)
        """
        return self.__mapping.iteritems()
        
    def __getitem__(self, k):
        return self.__mapping[k]
        
    def __len__(self):
        return sum(map(len, self.__conjunctions))    
        
class GTT(BooleanModel):
    """
    :param model: Boolean model representing the Global Truth Table
    
    >>> from __caspo__ import Conjunction, BooleanModel, GTT
    >>> c = Conjunction.from_str('TNFa+TGFa=Hsp27')
    >>> b = BooleanModel([c])
    >>> g = GTT(b)
    >>> len(g)
    1
    """
    def __init__(self, model):
        super(GTT, self).__init__(model.conjunctions)
        self.models = set()
        
    def add(self, model):
        """
        Adds a model to the GTT
        
        :param model: the boolean model to add
        
        >>> from __caspo__ import Conjunction, BooleanModel, GTT
        >>> c1 = Conjunction.from_str('TNFa+TGFa=Hsp27')
        >>> b1 = BooleanModel([c1])
        >>> g = GTT(b)
        >>> c2 = Conjunction.from_str('TNFa=p38')
        >>> b2 = BooleanModel([c2])
        >>> g.add(b2)
        >>> len(g)
        2
        """
        self.models.add(model)
        
    def to_matrix(self, setup):
        """
        Returns an iterator over all possible inputs and their corresponding outputs
        
        :param setup: :class:`__caspo__.Dataset.Setup` instance
        
        >>> from __caspo__ import Conjunction, BooleanModel, Setup, GTT
        >>> setup = Setup(['TNFa', 'TGFa'], [], ['Hsp27'])
        >>> c = Conjunction.from_str('TNFa+TGFa=Hsp27')
        >>> gtt = GTT(BooleanModel([c]))
        >>> for r in gtt.to_matrix(setup):
        ...     print r
        {'TGFa': 0, 'Hsp27': 0, 'TNFa': 0}
        {'TGFa': 0, 'Hsp27': 0, 'TNFa': 1}
        {'TGFa': 1, 'Hsp27': 0, 'TNFa': 0}
        {'TGFa': 1, 'Hsp27': 1, 'TNFa': 1}
        """    
        for inputs in setup.iter_all():
            matrix_inputs = {}
            for i in setup.stimuli:
                matrix_inputs[i] = inputs[i]
                
            for i in setup.inhibitors:
                if i in inputs.keys():
                    matrix_inputs[i + 'i'] = True
                else:
                    matrix_inputs[i + 'i'] = False

            row = {}
            for readout in setup.readouts:
                row[readout] = int(self.resolve(readout, inputs, setup))

            for k,v in matrix_inputs.iteritems():
                row[k] = int(v)

            yield row

    def __len__(self):
        return len(self.models) + 1

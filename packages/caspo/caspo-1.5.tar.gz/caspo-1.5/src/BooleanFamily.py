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
from pyasp.asp import GringoClasp, TermSet, Term

from asp import gtt_base_prg, gtt_core_prg, gtt_diff_prg, gtt_prg, mutual_prg
from __caspo__ import Network, Conjunction, BooleanModel, GTT

from itertools import chain, combinations

class BooleanFamily(set):
    """
    :param setup: :class:`__caspo__.Dataset.Setup` instance
    :param conjunctions: list of all possible :class:`__caspo__.Conjunction` among the family
    :param gtts: True to compute GTTs, False otherwise.
    
    >>> from __caspo__ import Conjunction, BooleanFamily, Setup, Network
    >>> from StringIO import StringIO
    >>> fake_file = StringIO('a\\t1\\tc\\nb\\t-1\\tc\\n')
    >>> net = Network(None, open=lambda n,m: fake_file)
    >>> setup = Setup(['a'], ['b'], ['c'])
    >>> family = BooleanFamily(net, setup, False)
    >>> len(family)
    0
    """
    def __init__(self, pkn, setup, gtts):
        super(BooleanFamily, self).__init__()
        
        self.pkn = pkn
        self.setup = setup
        self.formulas = []
        self.gtts = None
        if gtts:
            self.gtts = set()
        
        self.occurrences = dict(map(lambda c: (str(c), 0.), self.pkn.hyperedges))
        self.__combinatorics = None

    def add(self, model):
        """
        Adds a Boolean model to the family. Updates conjunction's occurrences and GTTs.
        If the model has the input-output behavior of some previously added model, it's added to the corresponding GTT.
        Otherwise, a new GTT is created with this model.
        
        :param model: :class:`__caspo__.BooleanModel` instance to add
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel, Network
        >>> from StringIO import StringIO
        >>> setup = Setup(['a','b'], [], ['c'])
        >>> c1 = Conjunction.from_str('a=c')
        >>> c2 = Conjunction.from_str('a=d')
        >>> c3 = Conjunction.from_str('d=c')
        >>> c4 = Conjunction.from_str('a+!b=c')

        >>> fake_file = StringIO('a\\t1\\tc\\nb\\t-1\\tc\\na\\t1\\td\\nd\\t1\\tc\\n')
        >>> net = Network(None, open=lambda n,m: fake_file)
        
        >>> family = BooleanFamily(net, setup, True)
        >>> len(family)
        0
        >>> len(family.gtts)
        0
        
        First, we add a model having only `c1` and since the family is empty, a new GTT is created.
        
        >>> family.add(BooleanModel([c1]))
        >>> len(family)
        1
        >>> len(family.gtts)
        1
        
        Next, we add a model having `c2` and `c3` which is equivalent to the previous model.
        
        >>> family.add(BooleanModel([c2,c3]))
        >>> len(family)
        2
        >>> len(family.gtts)
        1
        
        Finally, if we add a model having a different input-output behavior, a new GTT is created.
        
        >>> family.add(BooleanModel([c4]))
        >>> len(family)
        3
        >>> len(family.gtts)
        2
        
        Now, let's check the GTTs and their corresponding gathered models. Note that we convert 
        `family.gtts` into a list only for testing (sets don't preserve any order), but you don't 
        need to do it in your code.
        
        >>> for gtt in sorted(family.gtts, key=len):
        ...    print gtt.vector(), len(gtt)
        {'a+!b=c': 1} 1
        {'a=c': 1} 2
        """
        super(BooleanFamily, self).add(model)
        for h in model.vector():
            self.occurrences[h] += 1
            
        for t,cs in model.iteritems():
            idxc = set()
            for c in cs:
                idxc.add(self.pkn.hyperedges.index(c))
                
            if self.formulas.count(idxc) == 0:
                self.formulas.append(idxc)

        if self.gtts != None:
            self.__update_gtts__(model)
                
    @property
    def frequencies(self):
        """
        Returns an iterator over tuples (h,f) where `h` is the string representation of a conjunction 
        and `f` its frequency in the family.
        
        :returns: iterator
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel, Network
        >>> from StringIO import StringIO
        >>> fake_file = StringIO('a\\t1\\tc\\nb\\t-1\\tc\\n')
        >>> net = Network(None, open=lambda n,m: fake_file)
        >>> setup = Setup(['a'], ['b'], ['c'])
        
        >>> c1 = Conjunction.from_str('a=c')
        >>> c2 = Conjunction.from_str('!b=c')
        >>> c3 = Conjunction.from_str('a+!b=c')
        >>> c4 = Conjunction.from_str('TNFa=p38')
        >>> c5 = Conjunction.from_str('ras=p38')
        
        >>> family = BooleanFamily(net, setup, False)
        >>> family.add(BooleanModel([c1]))
        >>> family.add(BooleanModel([c2]))
        >>> family.add(BooleanModel([c3]))        
        >>> family.add(BooleanModel([c1,c2]))
        >>> print list(family.frequencies)
        [('a=c', 0.5), ('!b=c', 0.5), ('a+!b=c', 0.25)]
        """
        nmodels = len(self)
        for h,o in self.occurrences.iteritems():
            yield h, o / nmodels

    def combinatorics(self, mode, update=False):
        """
        Returns an iterator over the mutual inclusive/exclusive conjunctions.
        
        :param mode: either 'exclusive' or 'inclusive'
        :param update: True to force to re-compute combinatorics.
        :returns: iterator
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel, Network
        
        >>> from StringIO import StringIO
        >>> fake_file = StringIO('a\\t1\\tc\\na\\t1\\tb\\nb\\t1\\tc\\n')
        >>> net = Network(None, open=lambda n,m: fake_file)
        
        >>> setup = Setup(['a'], ['b'], ['c'])
        >>> c1 = Conjunction.from_str('a=c')
        >>> c2 = Conjunction.from_str('a=b')
        >>> c3 = Conjunction.from_str('b=c')
        
        >>> family = BooleanFamily(net, setup, False)
        >>> family.add(BooleanModel([c1]))
        >>> family.add(BooleanModel([c2,c3]))
        
        >>> for m in family.combinatorics('exclusive'):
        ...     print m['conjunction_A'], m['frequency_A'], m['conjunction_B'], m['frequency_B']
        a=c 0.5 a=b 0.5
        a=c 0.5 b=c 0.5
        
        >>> for m in family.combinatorics('inclusive'):
        ...     print m['conjunction_A'], m['frequency_A'], m['conjunction_B'], m['frequency_B']
        b=c 0.5 a=b 0.5
        """
        if not self.__combinatorics or update:
            self.__combinatorics = self.__mutuals__()
        
        nmodels = float(len(self))
        for mutual in self.__combinatorics:
            if mutual.pred() == mode:
                ta = mutual.arg(0) - 1
                tb = mutual.arg(1) - 1 
            
                m = dict(conjunction_A=self.pkn.hyperedges[ta], frequency_A=self.occurrences[str(self.pkn.hyperedges[ta])] / nmodels, 
                         conjunction_B=self.pkn.hyperedges[tb], frequency_B=self.occurrences[str(self.pkn.hyperedges[tb])] / nmodels)
                     
                yield m

    @classmethod
    def from_termsets(cls, termsets, pkn, setup, gtts):
        """
        Constructor from a list of PyASP TermSet instances.
        
        :param termsets: list of TermSet
        :param pkn: :class:`__caspo__.Network` instance
        :param setup: :class:`__caspo__.Dataset.Setup` instance
        :param gtts: True to compute GTTs, False otherwise.
        :returns: :class:`__caspo__.BooleanFamily`
        """
        family = cls(pkn, setup, gtts)
        for t in termsets:
            family.add(BooleanModel.from_termset(t, pkn))

        return family

    @classmethod
    def from_matrix(cls, matrix, pkn=None, setup=None, gtts=False):
        """
        Constructor from a matrix representation of logic models
        
        :param matrix: iterator over rows in the matrix. Each row describes a model
        :param pkn: :class:`__caspo__.Network` instance
        :param setup: :class:`__caspo__.Setup` instance
        :param gtts: True to compute GTTs, False otherwise.
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, Network
        >>> from StringIO import StringIO
        >>> fake_file = StringIO('a\\t1\\tc\\nb\\t-1\\tc\\n')
        >>> net = Network(None, open=lambda n,m: fake_file)
        
        >>> setup = Setup(['a'], ['b'], ['c'])

        >>> matrix = [{'a=c': '1', '!b=c': '0', 'a+!b=c': 0},{'a=c': '0', '!b=c': '0', 'a+!b=c': 1}]
        >>> family = BooleanFamily.from_matrix(matrix, net, setup, False)
        >>> len(family)
        2
        >>> print list(family.frequencies)
        [('a=c', 0.5), ('!b=c', 0.0), ('a+!b=c', 0.5)]
        """
        if not pkn:
            edges = set()
            for fn in matrix.fieldnames:
                co = Conjunction.from_str(fn)
                for src in co.sources:
                    edges.add((src.name,co.target,src.sign))
            
            temp = '.igraph.sif'
            ig = open(temp, 'w')
            for source,target,sign in edges:
                ig.write("%s\t%s\t%s\n" % (source,sign,target))
            ig.close()

            pkn = Network(temp)
            
        family = cls(pkn, setup, gtts)
        for v in matrix:
            family.add(BooleanModel.from_vector(v))

        return family
        
    def weighted_mse(self, dataset, testing=[]):
        """
        Compute the weighted MSE of the family. If GTTs were computed, each output prediction is weighted
        according to the number of models gathered by the corresponding GTT. Otherwise, output predictions
        are summed over all models in the family. If the family is complete, both computation are equivalent.
        
        :param dataset: :class:`__caspo__.Dataset` instance
        :param testing: list of experiment indices
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel, Network

        >>> from StringIO import StringIO
        >>> fake_file = StringIO('a\\t1\\tc\\na\\t1\\tb\\nb\\t1\\tc\\na\\t1\\td\\n')
        >>> net = Network(None, open=lambda n,m: fake_file)
        >>> setup = Setup(['a'], ['d'], ['c', 'd'])
        >>> c1 = Conjunction.from_str('a=c')
        >>> c2 = Conjunction.from_str('a=b')
        >>> c3 = Conjunction.from_str('b=c')
        >>> c4 = Conjunction.from_str('a=d')
        
        
        >>> family = BooleanFamily(net, setup, False)
        >>> family.add(BooleanModel([c1]))
        >>> family.add(BooleanModel([c2,c3]))
        >>> family.add(BooleanModel([c4]))
        
        Now, let's create a fake dataset and compute the family's MSE
        
        >>> from __caspo__ import Dataset, Experiment, Conjunction
        >>> e0 = Experiment({'a': 1, 'd': 0}, {10: {'c':0.8, 'd': 0}})
        >>> e1 = Experiment({'a': 0, 'd': 1}, {10: {'c':0.2, 'd':0}})
        >>> dataset = Dataset([e0, e1], ['a'], ['d'], ['c', 'd'], 10)
        >>> print "%.4f" % family.weighted_mse(dataset) # ((2/3 - 0.8)^2 + (0 - 0.2)^2) / 4
        0.0144
        """
        rss = 0.
        obs = 0
        total = float(len(self))
        
        if len(testing) == 0:
            testing = xrange(len(dataset))
            
        if self.gtts != None:
            it = self.gtts
            weight = lambda gtt: len(gtt)
        else:
            it = self
            weight = lambda model: 1
        
        for exp in (dataset[i] for i in testing):
            inputs = exp.boolean_input(dataset.setup)
            outputs = exp.outputs[dataset.time_point]
            
            for readout, value in outputs.iteritems():
                val = 0
                for g in it:
                    val = val + int(g.resolve(readout, inputs, dataset.setup)) * weight(g)

                rss = rss + pow(value - val / total, 2)
                obs = obs + 1

        return rss / obs    
                        
    def to_matrix(self, gtts=False):
        """
        Returns an iterator over all models in the family as vectors (key-value: conjunction-{0,1})
        
        >>> from __caspo__ import Conjunction, BooleanFamily, Setup, BooleanModel, Network
        >>> from StringIO import StringIO
        >>> fake_file = StringIO('a\\t1\\tc\\na\\t1\\tb\\nb\\t1\\tc\\na\\t1\\td\\n')
        >>> net = Network(None, open=lambda n,m: fake_file)
        
        >>> setup = Setup(['a'], ['d'], ['c', 'd'])
        >>> c1 = Conjunction.from_str('a=c')
        >>> c2 = Conjunction.from_str('a=b')
        >>> c3 = Conjunction.from_str('b=c')
        >>> c4 = Conjunction.from_str('a=d')

        >>> family = BooleanFamily(net, setup, False)
        >>> family.add(BooleanModel([c1]))
        >>> family.add(BooleanModel([c2,c3]))
        >>> family.add(BooleanModel([c2,c3,c4]))
        >>> for model in sorted(family.to_matrix(), key=lambda v: v.values().count(1)):
        ...     print model
        {'b=c': 0, 'a=c': 1, 'a=b': 0, 'a=d': 0, 'a+b=c': 0}
        {'b=c': 1, 'a=c': 0, 'a=b': 1, 'a=d': 0, 'a+b=c': 0}
        {'b=c': 1, 'a=c': 0, 'a=b': 1, 'a=d': 1, 'a+b=c': 0}
        """
        vector = {}
        
        vector = dict.fromkeys(map(lambda h: str(h), self.pkn.hyperedges), 0)
        if gtts:
            it = self.gtts
        else:
            it = self
            
        for model in it:
            v = vector.copy()
            v = model.vector(v)
            yield v
            
    def termset(self, gtts=False):
        instance = TermSet()
        if gtts:
            it = self.gtts
        else:
            it = self
            
        instance.add(Term('nmodels', [len(it)]))
        for i, model in enumerate(it):
            ts = model.termset(self.formulas, self.pkn.hyperedges, i+1)

            instance = instance.union(ts)
            
        return instance
                
    def variances(self, gtts=False):
        if gtts:
            it = self.gtts
        else:
            it = self
            
        n = len(it)    
        for inputs in self.setup.iter_all():
            row = {}
            matrix_inputs = {}
            for i in self.setup.stimuli:
                matrix_inputs[i] = inputs[i]
                
            for i in self.setup.inhibitors:
                if i in inputs.keys():
                    matrix_inputs[i + 'i'] = True
                else:
                    matrix_inputs[i + 'i'] = False
                    
            for k,v in matrix_inputs.iteritems():
                row[k] = int(v)

            for readout in self.setup.readouts:
                #based on online_variance from: http://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
                mean = 0.
                m2 = 0.
                for j,m in enumerate(it):                
                    s = int(m.resolve(readout, inputs, self.setup))
                    delta = s - mean
                    mean = mean + delta / (j+1)
                    m2 = m2 + delta * (s - mean)
                
                row[readout] = m2 / n
                
            yield row
                    
    def core_matrix(self):
        core, noeffect = self.__core__()
        
        header = self.setup.stimuli \
               + map(lambda i: i+'i', self.setup.inhibitors) \
               + self.setup.readouts
               
        row_tpl = dict(map(lambda c: (c, 0), header))
        
        ne = map(lambda t: t._arg(0), noeffect)
        
        for comb in chain.from_iterable(combinations(ne, r) for r in xrange(len(ne) + 1)):
            row = row_tpl.copy()
            for v in comb:
                if v in self.setup.inhibitors:
                    v = v + 'i'
                    
                row[v] = 1
                
            for exp in core:
                for t in exp:
                    v = t._arg(0)
                    if t.pred() == 'exp':
                        if v in self.setup.inhibitors:
                            v = v + 'i'
                    if v not in comb:
                        row[v] = 1
                
                yield row
        
    def __core__(self):
        solver = GringoClasp()
        
        models = self.termset(self.gtts != None)
        setup = self.setup.termset()
        
        instance = models.union(setup)
        
        prg = [instance.to_file(), gtt_base_prg]
        ne = solver.run(prg, nmodels=1, 
                       collapseTerms=False, collapseAtoms=False)
        
        os.unlink(prg[0])
        noeffect = filter(lambda t: t.pred() == 'noeffect', ne[0])
        
        prg = [instance.to_file(), gtt_base_prg, gtt_core_prg, gtt_prg]
        core = solver.run(prg, nmodels=0, 
                          collapseTerms=False, collapseAtoms=False)

        os.unlink(prg[0])
        return core, noeffect

    def __update_gtts__(self, model):
        if len(self.gtts) > 0:
            solver = GringoClasp()
    
            setup = self.setup.termset()
            m1 = model.termset(self.formulas, self.pkn.hyperedges, 1)
            inst = setup.union(m1)
            
            added = False
            for gtt in self.gtts:
                m2 = gtt.termset(self.formulas, self.pkn.hyperedges,2)
                instance = inst.union(m2)

                prg = [instance.to_file(), gtt_base_prg, gtt_diff_prg, gtt_prg]
                diff = solver.run(prg, nmodels=1, 
                                 collapseTerms=False, collapseAtoms=False)
                                 
                os.unlink(prg[0])
                if len(diff) == 0:
                    gtt.add(model)
                    added = True
                    break
                    
            if not added:
                self.gtts.add(GTT(model))
        else:
            self.gtts.add(GTT(model))
        
    def __mutuals__(self):
        solver = GringoClasp()
        
        instance = self.termset()

        prg = [instance.to_file(), mutual_prg]
        mutuals = solver.run(prg, nmodels=1, 
                             collapseTerms=False, collapseAtoms=False)

        os.unlink(prg[0])
        return mutuals[0]

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
from random import shuffle, randint
from pyasp.asp import GringoClasp, GringoClaspOpt, Term, TermSet

from asp import guess_prg, functions_prg, optimization_prg, enumeration_prg, residual_prg, genbench_prg, _
from BooleanFamily import BooleanFamily
from BooleanModel import BooleanModel
from Conjunction import Conjunction
from Dataset import Dataset

class Learner(object):
    """
    :param pkn: :class:`__caspo__.Network.Network` instance
    :param dataset: :class:`__caspo__.Dataset.Dataset` instance
    """
    def __init__(self, pkn, dataset):
        self.pkn = pkn
        self.dataset = dataset

    def learn(self, fit_tol, size_tol, discrete, fn=round, gtts=False, clasp=None, learning=[], feedback=None):
        """
        Learn logic models
        
        :param float fit_tol: fitness tolerance
        :param int size_tol: size tolerance
        :param int discrete: multi-valued discretization
        :param function fn: discretization function
        :param bool gtts: compute GTTs
        :param dict clasp: custom clasp's parameters in keys `optimal` and `suboptimal`
        :param list learning: indices to use from the dataset
        :param function feedback: function to be called after parsing each model during learning
        
        :results: :class:`__caspo__.BooleanFamily.BooleanFamily`
        """
        observations = self.dataset.termset(discrete, fn, learning)
        network = self.pkn.termset()
        setup = self.dataset.setup.termset()
        instance = observations.union(setup).union(network)

        if clasp and len(clasp["optimal"]) > 0:
            optimum = self.__learn_optimal__(instance, coptions=clasp["optimal"])
        else:
            optimum = self.__learn_optimal__(instance)
    
        fit = self.__scale_rss__(instance.union(optimum))
        size = optimum.score[1]
        
        family = BooleanFamily(self.pkn, self.dataset.setup, gtts)
        def cb(ts):
            family.add(BooleanModel.from_termset(ts, self.pkn))
            if feedback:
                feedback(family)

        if clasp and len(clasp["suboptimal"]) > 0:
            models = self.__learn_suboptimal__(instance, int(fit + fit*fit_tol), size + size_tol, callback=cb, coptions=clasp["suboptimal"])
        else:
            models = self.__learn_suboptimal__(instance, int(fit + fit*fit_tol), size + size_tol, callback=cb)
        
        return family

    def validate(self, fit_tol, size_tol, discrete, fn, times, kfolds, clasp):
        """
        Run k-fold cross validation
        
        :param fit_tol: fitness tolerance
        :param size_tol: size tolerance
        :param discrete: multi-valued discretization
        :param times: cross validation iterations
        :param kfolds: folds for the cross-validation
        :param clasp: custom clasp's parameters in keys `optimal` and `suboptimal`
        :returns: iterator over the results
        """
        for i in xrange(times):
            iresults = []
            folds = self.__k_folds__(range(len(self.dataset)), kfolds)
            
            for k, (learning, testing) in enumerate(folds):
                family = self.learn(fit_tol, size_tol, discrete, fn, True, clasp, learning)
                iresults.append(dict(gtts=len(family.gtts), mse=family.weighted_mse(self.dataset, testing), models=len(family)))

            yield iresults
            
    def random(self, size, nand):
        """
        Returns a random Boolean logic model
        
        :param tuple size: tuple with lower and upper size limits
        :param tuple nand: tuple with lower and upper number of AND gates
        
        :returns: :class:`__caspo__.BooleanModel.BooleanModel`
        """
        network = self.pkn.termset()
        setup = self.dataset.setup.termset()
        instance = setup.union(network)
        model = self.__learn_random__(instance, size, nand)
        return BooleanModel.from_termset(model, self.pkn)
        
    def __learn_random__(self, instance, size, nand):
        prg = [instance.to_file(), guess_prg, genbench_prg]
        gopt = '-c minsize=%s -c maxsize=%s -c minnand=%s -c maxnand=%s' % (size[0], size[1], nand[0], nand[1])
        copt = '--sign-def=3 --seed=%s' % randint(0,32767)
        solver = GringoClaspOpt(gringo_options=gopt, clasp_options=copt)
        addText = "#hide. #show dnf/2."
        model = solver.run(prg, collapseTerms=False, collapseAtoms=False, additionalProgramText=addText)
        os.unlink(prg[0])
        return model[0]
        
    def __k_folds__(self, xs, k):
        shuffle(xs)
        for i in xrange(k):
        	training = [x for j, x in enumerate(xs) if j % k != i]
        	validation = [x for j, x in enumerate(xs) if j % k == i]
        	yield training, validation

    def __learn_optimal__(self, instance, coptions='--conf=jumpy --opt-hier=2 --opt-heu=2'):
        prg = [instance.to_file(), guess_prg, functions_prg, optimization_prg]
        solver = GringoClaspOpt(clasp_options=coptions)
        addText = "#hide. #show dnf/2."
        optimum = solver.run(prg, collapseTerms=False, collapseAtoms=False, additionalProgramText=addText)
        os.unlink(prg[0])
        return optimum[0]
        
    def __scale_rss__(self, instance):
        prg = [instance.to_file(), functions_prg, residual_prg]
        solver = GringoClaspOpt()
        addText = "#hide."
        rss = solver.run(prg, collapseTerms=False, collapseAtoms=False, additionalProgramText=addText)
        os.unlink(prg[0])
        return rss[0].score[0]

    def __learn_suboptimal__(self, instance, fit, size, callback=None, coptions='--conf=jumpy'):
        prg = [instance.to_file(), guess_prg, functions_prg, enumeration_prg]
        goptions='--const maxresidual=%s --const maxsize=%s' % (fit, size)
        solver = GringoClasp(gringo_options=goptions,clasp_options=coptions)
        addText = "#hide. #show dnf/2."
        answers = solver.run(prg, nmodels=0, collapseTerms=False, collapseAtoms=False, additionalProgramText=addText, callback=callback)
        os.unlink(prg[0])
        return answers

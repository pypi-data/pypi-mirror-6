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
import os, sys
from __caspo__ import args, utils, Network, Dataset, Learner

if __name__ == '__main__':
    arguments = args.get_learn_args()

    print '\nReading input files with CellNOptR...'
    from __caspo__ import cno    
    temp = cno.compress(arguments.pkn, arguments.midas)    
    dataset = Dataset.from_midas(arguments.midas)
    network = Network(temp, arguments.max_and)

    print 'done.'
    
    learner = Learner(network, dataset)
    
    clasp = dict(optimal="",suboptimal="")
    if arguments.clasp:
        clasp["optimal"] = arguments.clasp.readline()[:-1]
        clasp["suboptimal"] = arguments.clasp.readline()[:-1]
        
    if arguments.gtts:
        print '\nLearning Boolean logic models and their Global Truth Tables with ASP...'
    else:
        print '\nLearning Boolean logic models with ASP...'
        
    def feedback(family):
        if arguments.gtts:
            sys.stdout.write("\r%s Boolean logic models and %s Global Truth Tables have been learned." % (len(family), len(family.gtts)))
        else:
            sys.stdout.write("\r%s Boolean logic models have been learned." % len(family))
            
        sys.stdout.flush()
        
    family = learner.learn(arguments.fit, arguments.size, arguments.discrete, arguments.trunc, arguments.gtts, clasp, feedback=feedback)
    print '\n'
    
    writer = utils.Writer(arguments.outdir)
    conjunctions = map(str, family.pkn.hyperedges)

    writer.write(family.to_matrix(), 'models.csv', conjunctions)
    writer.write(family.frequencies, 'frequencies.csv', ['conjunction','frequency'], 
                 lambda r: dict(conjunction=r[0], frequency=r[1]))
    
    if arguments.mutual:
        header = ['conjunction_A', 'frequency_A', 'conjunction_B', 'frequency_B']
        writer.write(family.combinatorics('exclusive'), 'exclusive.csv', header)
        writer.write(family.combinatorics('inclusive'), 'inclusive.csv', header)

    if arguments.gtts > 1:
        header = dataset.setup.stimuli \
               + map(lambda i: i+'i', dataset.setup.inhibitors) \
               + dataset.setup.readouts
        
        gtts = list(family.gtts)
        writer.write(family.core_matrix(), 'core.csv', header)
        writer.write(family.to_matrix(True), 'gtts.csv', conjunctions)
        
        if arguments.gtts > 2:    
            gtts_stats = []
            for i,w in enumerate(gtts):
                gtts_stats.append(dict(id=i, mse="%.4f" % w.mse(dataset), models=len(w)))
                writer.write(w.to_matrix(dataset.setup), 'gtt-%s.csv' % i, header, verbose=False)

            print "Wrote %s/gtt-%s.csv" % (arguments.outdir, list(range(len(family.gtts))))
            gtts_stats.append(dict(id='family', mse="%.4f" % family.weighted_mse(dataset), models=len(family)))
            writer.write(gtts_stats, 'gtts_stats.csv', ['id', 'mse', 'models'])
            writer.write(family.variances(True), 'variances.csv', header)
        
    if arguments.cross:
        times = arguments.cross[0]
        kfolds = arguments.cross[1]
        
        print '\nRunning %s random %s-fold cross validation... ' % (times, kfolds)
        results = learner.validate(arguments.fit, arguments.size, arguments.discrete, arguments.trunc, times, kfolds, clasp)
        for i,res in enumerate(results):
            writer.write(res, 'cross_validation_%s.csv' % (i+1), ['gtts', 'mse', 'models'])

        print 'done.'

    utils.clean_up()

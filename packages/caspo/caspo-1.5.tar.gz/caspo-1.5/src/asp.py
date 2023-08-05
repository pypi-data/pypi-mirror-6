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

from pyasp.asp import Term

#hooks to include/remove "" from terms arguments
Term._arg = lambda s,n: s.arg(n)[1:-1]
_ = lambda s: '"' + s + '"'
 
root = __file__.rsplit('/', 1)[0]

guess_prg           =  root + '/query/guess.lp'
functions_prg       =  root + '/query/functions.lp'
optimization_prg    =  root + '/query/optimization.lp'
enumeration_prg     =  root + '/query/enum.lp'
residual_prg        =  root + '/query/residual.lp'
gtt_base_prg        =  root + '/query/gtt_base.lp'
gtt_core_prg        =  root + '/query/gtt_core.lp'
gtt_diff_prg        =  root + '/query/gtt_diff.lp'
gtt_prg             =  root + '/query/gtt.lp'
mutual_prg          =  root + '/query/mutual.lp'
genbench_prg        =  root + '/query/genbench.lp'
control_prg         =  root + '/query/control.lp'
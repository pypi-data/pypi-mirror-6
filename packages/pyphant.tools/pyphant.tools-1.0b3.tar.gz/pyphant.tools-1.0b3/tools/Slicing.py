# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009, Rectorate of the University of Freiburg
# Copyright (c) 2009, Andreas W. Liehr (liehr@users.sourceforge.net)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

u"""
The Slicing Worker is a class of Pyphant's tools toolbox. It cuts out one
part of a field and provides it as a new field to work on.
"""

from pyphant.core import (Worker, Connectors, DataContainer)
from pyphant import quantities
import copy
import pkg_resources


class Slicing(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution("pyphant.tools").version
    name = "Slicing"
    _sockets = [("field", Connectors.TYPE_IMAGE)]
    _params = []

    def __init__(self, parent=None, annotations=None):
        if annotations is None:
            annotations = {}
        super(Slicing, self).__init__(parent, annotations)
        self.oldField = None

    def refreshParams(self, subscriber=None, field=None):
        if self.socketField.isFull() or field != None:
            try:
                templ = self.socketField.getResult(subscriber)
            except:
                templ = field
            if templ == self.oldField:
                return
            self.oldField = templ
            self._params = []
            for i, dim in enumerate(templ.dimensions):
                if quantities.isQuantity(dim.unit):
                    intStart = (dim.data.min() * dim.unit).value
                    intEnd   = (dim.data.max() * dim.unit).value
                    unitname = dim.unit.unit.name()
                else:
                    intStart = dim.data.min() * dim.unit
                    intEnd   = dim.data.max() * dim.unit
                    unitname = ''
                param = (
                    'dim%i' % i,
                    "%s %s (index #0:%i):" % (
                        dim.longname,
                        dim.shortname,
                        len(dim.data) - 1
                        ),
                    "%.4f %s:%.4f %s" % (
                        intStart,
                        unitname,
                        intEnd,
                        unitname
                        ),
                    None)
                self._params.append(param)
            self._params.reverse()
            self.initParams(self._params)

    @Worker.plug(Connectors.TYPE_IMAGE)
    def extract(self, field, subscriber=0):
        if not hasattr(self, 'paramDim0'):
            self.refreshParams()
        params = [str(eval('self.paramDim%i.value' % i))
                  for i in range(len(field.dimensions))]
        for dim, arg in enumerate(params):
            if arg.startswith('#'):
                step = None
                if arg == '#:':
                    start = 0
                    end = len(field.dimensions[dim].data)
                elif arg[1] == ':':
                    start = 0
                    end   = long(arg[2:]) + 1
                elif arg[-1] == ':':
                    start = long(arg[1: -1])
                    end = len(field.dimensions[dim].data)
                else:
                    ind = map(long, arg[1:].split(':'))
                    start = ind[0]
                    if len(ind) == 1:
                        end = ind[0] + 1
                    elif len(ind) >= 2:
                        end = ind[1] + 1
                    if len(ind) == 3:
                        step = ind[2]
                    if len(ind) > 3:
                        raise ValueError("Illegal slice with "
                                         "more than two colons.")
                params[dim] = slice(start, end, step)
            else:
                s = DataContainer.slice2ind(arg, field.dimensions[dim])
                params[dim] = slice(s.start,
                                    min(s.stop + 1,
                                        len(field.dimensions[dim].data)),
                                    s.step)
        result = copy.deepcopy(field[params])
        result.seal()
        return result

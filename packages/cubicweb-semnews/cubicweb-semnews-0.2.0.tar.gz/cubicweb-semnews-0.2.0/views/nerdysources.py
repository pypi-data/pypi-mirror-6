# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-semnews views/forms/actions/components for web ui"""
import csv

from nerdy import core, dataio

from cubicweb.view import Component


class NerdySourceComponent(Component):
    __abstract__ = True
    __registry__ = 'nerdy-source'

    nerdy_type = None
    query = None
    endpoint = None
    lexicon = None
    filename = None
    delimiter = None
    use_cache = True
    lang = None

    def get_nerdy_source(self):
        if self.nerdy_type == 'AppidRql':
            return core.NerdySourceAppidRql(self.query, self.endpoint,
                                            name=self.__regid__, use_cache=self.use_cache)
        elif self.nerdy_type == 'LocalRql':
            return core.NerdySourceLocalRql(self.query, self._cw,
                                            name=self.__regid__, use_cache=self.use_cache)
        elif self.nerdy_type == 'UrlRql':
            return core.NerdySourceUrlRql(self.query, self.endpoint,
                                            name=self.__regid__, use_cache=self.use_cache)
        elif self.nerdy_type == 'Sparql':
            return core.NerdySourceSparql(self.query, self.endpoint,
                                            name=self.__regid__, use_cache=self.use_cache)
        elif self.nerdy_type == 'Lexicon':
            return core.NerdySourceLexical(self.lexicon,
                                           name=self.__regid__,use_cache=self.use_cache)
        elif self.nerdy_type == 'File':
            lexicon = dict(csv.reader(open(self.filename), delimiter=self.delimiter))
            return core.NerdySourceLexical(self.lexicon,
                                           name=self.__regid__, use_cache=self.use_cache)
        else:
            raise ValueError('Unkwnon source type %s' % self.nerdy_type)

    def get_preprocessors(self):
        return ()

    def get_filters(self):
        return ()


class NerdySourceBaseLexiconComponent(NerdySourceComponent):
    __regid__ = 'semnews-lexicon'

    def get_nerdy_source(self):
        filename = self._cw.vreg.config['semnews-lexicon-file']
        if filename:
            lexicon = dict(csv.reader(open(filename), delimiter='\t'))
            return core.NerdySourceLexical(lexicon, name=self.__regid__, use_cache=True)

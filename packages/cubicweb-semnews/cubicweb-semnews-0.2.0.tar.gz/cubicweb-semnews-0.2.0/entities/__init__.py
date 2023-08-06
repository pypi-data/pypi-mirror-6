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

"""cubicweb-semnews entity's classes"""
from datetime import datetime, timedelta

from cubicweb.uilib import text_cut
from cubicweb.selectors import is_instance
from cubicweb.entities import AnyEntity

from cubes.semnews.entities.external_resources import (query_dbpedia_infos,
                                                       query_dbpedia_categories,
                                                       query_dbpedia_geo_infos)


_ = unicode


class InfoMixin(object):

    def dc_title(self):
        return self.title

    @property
    def text_content(self):
        return self.title

    @property
    def categories(self):
        return []

    @property
    def category_label(self):
        return _('Categories')

    @property
    def named_entities(self):
        return self._cw.execute('Any E WHERE X recognized_entities E, '
                                'E activated TRUE, X eid %(e)s', {'e': self.eid})



###############################################################################
### NEWS ARTICLE ##############################################################
###############################################################################
class NewsArticle(InfoMixin, AnyEntity):
    __regid__ = 'NewsArticle'

    @property
    def text_content(self):
        return self.content

    @property
    def preview_content(self):
        cut_content = text_cut(self.content, 30) if self.content else None
        if cut_content:
            return cut_content if len(cut_content) <len(self.content) else (cut_content + '[...]')
        return ''


###############################################################################
### TWEET #####################################################################
###############################################################################
class Tweet(InfoMixin, AnyEntity):
    __regid__ = 'Tweet'

    @property
    def text_content(self):
        return self.title

    @property
    def preview_content(self):
        return self.title

    @property
    def categories(self):
        return self.has_hashtags

    @property
    def category_label(self):
        return _('HashTags')


class HashTag(AnyEntity):
    __regid__ = 'HashTag'

    def dc_title(self):
        return self.label


###############################################################################
### EXTERNAL URI ##############################################################
###############################################################################
class ExternalUri(AnyEntity):
    __regid__ = 'ExternalUri'

    def dc_title(self):
        infos = query_dbpedia_infos(self.uri)
        label = infos.get('label', None)
        return label or self.uri

    def dc_description(self):
        infos = query_dbpedia_infos(self.uri)
        no_infos = self._cw._('No information available for %(u)s') % {'u': self.uri}
        abstract = infos.get('abstract')
        return abstract or no_infos

    @property
    def external_links(self):
        yield (self.uri, _('See on reference source'))
        infos = query_dbpedia_infos(self.uri)
        if infos.get('topic'):
            yield (infos.get('topic'), _('See on Wikipedia'))

    @property
    def depiction(self):
        infos = query_dbpedia_infos(self.uri)
        image = infos.get('thumbnail', None)
        if not image:
            image = infos.get('depiction', None)
        return image or self._cw.uiprops['RDF']

    @property
    def categories(self):
        return query_dbpedia_categories(self.uri)

    @property
    def latlong(self):
        infos = query_dbpedia_geo_infos(self.uri)
        latitude = infos.get('latitude')
        latitude = float(latitude) if latitude else None
        longitude = infos.get('longitude')
        longitude = float(longitude) if longitude else None
        return latitude, longitude

    def trend(self, start_past, end_past, start_now, end_now, lang=None):
        _rql = ('Any COUNT(X) WHERE X recognized_entities E, E eid %%(e)s, %s'
               'X creation_date D HAVING D > %%(ds)s AND  D <  %%(de)s')
        _rql = _rql % (('X source S, S lang "%s", ' % lang) if lang else u'')
        count_past = self._cw.execute(_rql, {'ds': start_past, 'de': end_past, 'e': self.eid})[0][0]
        count_now = self._cw.execute(_rql, {'ds': start_now, 'de': end_now, 'e': self.eid})[0][0]
        return count_past, count_now

    def trend_logo(self, hstart=96, hmiddle=48, hstop=0):
        start_past = datetime.now() - timedelta(hours=hstart)
        end_past = datetime.now() - timedelta(hours=hmiddle)
        start_now = datetime.now() - timedelta(hours=hmiddle)
        end_now = datetime.now() - timedelta(hours=hstop)
        count_past, count_now = self.trend(start_past, end_past, start_now, end_now)
        img = (self._cw.uiprops['GREEN_ARROW_UP'] if count_now >= count_past
               else self._cw.uiprops['RED_ARROW_DOWN'])
        return img

    def related_named_entities(self, limit=12):
        limit = ('LIMIT %s' % limit) if limit else ''
        _rql = ('Any E, COUNT(X) GROUPBY E ORDERBY 2 DESC %s '
                'WHERE X recognized_entities E, E activated TRUE, '
                'X recognized_entities EE, EE eid %%(e)s, NOT E eid %%(e)s' % limit)
        return self._cw.execute(_rql, {'e': self.eid})

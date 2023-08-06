# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
from itertools import izip

import numpy as np
## import scikits.learn.feature_extraction.text as sklt
## from scikits.learn.cluster import MeanShift, estimate_bandwidth, KMeans, Ward
## from scikits.learn.pipeline import
from cubicweb.selectors import is_instance
from cubicweb.view import EntityView


###############################################################################
### UTILITY FUNCTIONS #########################################################
###############################################################################
def build_articles_matrix(session, rset, uris_filter_nb=None, articles_filter_nb=None):
    """ Build a matrix from an rset of articles """
    # XXX Make it a view ?
    ext_uris = set()
    article_uris = {}
    for article in rset.entities():
        uris = [r[0] for r in article.named_entities]
        # If asked, removed uri with less than uris_filter_nb related articles
        if uris_filter_nb:
            uris = [e for e in uris if
                    len(session.entity_from_eid(e).reverse_recognized_entities)>=uris_filter_nb]
        # If asked, removed article with less than articles_filter_nb related uris
        # (after uris cleanup)
        if articles_filter_nb and len(uris)<articles_filter_nb:
            return
        ext_uris.update(uris)
        article_uris[article.eid] = uris
    X = np.zeros([len(article_uris), len(ext_uris)])
    ext_uris_pos = dict(izip(ext_uris, range(len(ext_uris))))
    article_pos = dict(izip(range(len(article_uris)), article_uris))
    for pos, article in article_pos.iteritems():
        for uri in article_uris[article]:
            X[pos, ext_uris_pos[uri]] = 1
    return X, article_pos, dict([(v,k) for (k,v) in ext_uris_pos.iteritems()])


def build_clustering_rendering(session, clusters, slices, X, x_eid, y_eid):
    # Render results
    html = u''
    for ind, eids in clusters.iteritems():
        html += u'<div class="well">'
        html += (u'<h2>%s %s - %s %s</h2>' % (session._('Cluster number'), ind,
                                             session._('Size'), len(eids)))
        # Details of external uris
        meanX = np.mean(X[slices[ind]], 0)
        exturis = np.argsort(meanX)
        for extind in np.argsort(meanX)[-10:]:
            if meanX[extind]>0:
                # Do not plot unuseful ext uri
                exturi = session.entity_from_eid(y_eid[extind])
                html += (u'<a href="%s"><span class="label label-success">%s</span></a>'
                         % (exturi.absolute_url(), exturi.uri))####exturi.dc_title()))
        # Articles
        rset = session.execute('Any X WHERE X eid IN (%s)' % ', '.join([str(e) for e in eids]))
        html += u'<ul>'
        for e in rset.entities():
            html += u'<li><a href="%s">%s</a></li>' % (e.absolute_url(), e.dc_title())
        html += u'</ul>'
        ## self.wview('list', rset)
        html += u'</div>'
    return html


###############################################################################
### CLUSTERING VIEWS ##########################################################
###############################################################################
class HiearchicalClusteringView(EntityView):
    __regid__ = 'ml-hgclustering'
    __select__ = EntityView.__select__ & is_instance('NewsArticle', 'Tweet')
    paginable = False

    def call(self, rset=None, n_clusters=15, uris_filter_nb=3, articles_filter_nb=3,
             clusters_filter_nb=2, clusters_max_frac=0.3):
        n_clusters = self._cw.form.get('n_clusters', None) or n_clusters
        uris_filter_nb = self._cw.form.get('uris_filter_nb', None) or uris_filter_nb
        articles_filter_nb = self._cw.form.get('articles_filter_nb', None) or articles_filter_nb
        clusters_filter_nb = self._cw.form.get('clusters_filter_nb', None) or clusters_filter_nb
        # Build matrix
        rset = rset or self.cw_rset
        X, x_eid, y_eid = build_articles_matrix(self._cw, rset)
        # Clustering
        labels = self.clustering(X, n_clusters)
        clusters = {}
        slices = {}
        for ind, label in enumerate(labels):
            clusters.setdefault(label, []).append(x_eid[ind])
            slices.setdefault(label, []).append(ind)
        # If asked, filtered clusters
        if clusters_filter_nb or clusters_max_frac:
            filtered_clusters = {}
            for label, eids in clusters.iteritems():
                if clusters_filter_nb and len(eids)<clusters_filter_nb:
                    # Do not keep clusters with less than clusters_filter_nb
                    continue
                if clusters_max_frac and len(eids)>(len(rset)*clusters_max_frac):
                    # Do not keep clusters with more than clusters_max_frac of the initial rset
                    # (big clusters tend to be garbage/noisy/useless)
                    continue
                filtered_clusters[label] = eids
            clusters = filtered_clusters
        # Render results
        html = build_clustering_rendering(self._cw, clusters, slices, X, x_eid, y_eid)
        self.w(html)

    def clustering(self, X, n_clusters):
        from sklearn.cluster import Ward
        ward = Ward(n_clusters=n_clusters).fit(X)
        return ward.labels_


class MeanShiftClusteringView(HiearchicalClusteringView):
    __regid__ = 'ml-msclustering'

    def clustering(self, X, n_clusters):
        from sklearn.cluster import MeanShift, estimate_bandwidth
        cluster = MeanShift()
        cluster.fit(X)
        return cluster.labels_

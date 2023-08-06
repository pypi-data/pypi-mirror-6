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

"""cubicweb-ner entity's classes"""
from logilab.common.decorators import cachedproperty

from cubicweb import dbapi
from cubicweb.cwconfig import CubicWebConfiguration
from cubicweb.entities import AnyEntity


###############################################################################
### SPARQL UTILITIES ##########################################################
###############################################################################
_SPARQL_CACHE = {}
def execute_sparql(query, endpoint):
    """ Execute a query on an endpoint """
    if (query, endpoint) in _SPARQL_CACHE:
        return _SPARQL_CACHE[(query, endpoint)]
    from SPARQLWrapper import SPARQLWrapper, JSON
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        rawresults = sparql.query().convert()
        labels = rawresults['head']['vars']
        results = rawresults["results"]["bindings"]
    except:
        # XXX ?
        print 'OOOOOUPS', query
        results = []
    _SPARQL_CACHE[(query, endpoint)] = results
    return results


###############################################################################
### NER PROCESS ###############################################################
###############################################################################
class NerProcess(AnyEntity):
    __regid__ = 'NerProcess'

    @cachedproperty
    def get_cnx(self):
        CubicWebConfiguration.load_cwctl_plugins()
        config = CubicWebConfiguration.config_for(self.host)
        sourceinfo = config.sources()['admin']
        login = sourceinfo['login']
        password = sourceinfo['password']
        _, cnx = dbapi.in_memory_repo_cnx(config, login, password=password)
        req = cnx.request()
        return req

    def query_match(self, word, endpoint, query):
        results = execute_sparql(self.entity.request % {'w': word}, self.entity.host)
        return [res['uri']['value'] for res in results]

    def match_word(self, word):
        """ Match a word """
        if self.type == 'rql':
            rset = self.get_cnx.execute(self.request, {'token': word})
            ner = rset[0][0] if len(rset) else None
        elif self.entity.type == 'sparql':
            rset = self.query_match(word, self.host, self.request)
            ner = rset[0] if len(rset) else None
        else:
            raise 'Unknown source type', self.type
        return ner

    def recognize_token(self, word, _recognized_cache={}):
        """ Recognize a token """
        preprocessor = self._cw.vreg['word-preprocessor'].select_or_none(self.host, self._cw)
        if preprocessor:
            word = preprocessor.preprocess_word(word)
        if word in _recognized_cache:
            return _recognized_cache[word]
        ner = self.match_word(word)
        _recognized_cache[word] = ner
        return ner


###############################################################################
### NER ENTRY #################################################################
###############################################################################
class NerEntry(AnyEntity):
    __regid__ = 'NerEntry'

    @classmethod
    def cw_fti_index_rql_queries(cls, req):
        count = req.execute('Any COUNT(X) WHERE X is NerEntry')[0][0]
        step_size = 500000
        rql_queries = []
        for step in range(0, step_size, count):
            rql_queries.append('Any X, L, UL ORDERBY X LIMIT %s OFFSET %s '
                               'WHERE X is NerEntry, X label L, X unormalize_label UL'
                               % (step_size, step*step_size))
        return rql_queries

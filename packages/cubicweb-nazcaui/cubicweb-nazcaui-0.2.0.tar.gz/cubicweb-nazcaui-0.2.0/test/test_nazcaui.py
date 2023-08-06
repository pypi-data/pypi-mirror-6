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

"""cubicweb-nazcaui automatic tests


uncomment code below if you want to activate automatic test for your cube:

.. sourcecode:: python

    from cubicweb.devtools.testlib import AutomaticWebTest

    class AutomaticWebTest(AutomaticWebTest):
        '''provides `to_test_etypes` and/or `list_startup_views` implementation
        to limit test scope
        '''

        def to_test_etypes(self):
            '''only test views for entities of the returned types'''
            return set(('My', 'Cube', 'Entity', 'Types'))

        def list_startup_views(self):
            '''only test startup views of the returned identifiers'''
            return ('some', 'startup', 'views')
"""

from cubicweb.devtools import testlib

from cubes.nazcaui.views.utils import parseindexes, getvars, getindexesfromvars


class ViewsTC(testlib.CubicWebTC):

    def test_parseindexes(self):
        """ Test if we correctly parse the indexes string """
        self.assertTupleEqual(parseindexes('1, 2, (3, 5), (3, 4)'),
                             (1, 2, (3, 5), (3, 4)))
        self.assertTupleEqual(parseindexes('A, BCD, (E, F), (G, (H, I, J), K)'),
                             ('A', 'BCD', ('E', 'F'), ('G', ('H', 'I', 'J'), 'K')))

    def test_getvars(self):
        """ Test if we correctly retrieve the variables"""
        self.assertTupleEqual(getvars('''
                Any U, N, LONG,
                LAT WHERE X is Location, X name N, X country C,
                C name "France", X longitude LONG, X
                latitude LAT, X population > 1000, X
                feature_class "P", X cwuri U
                ''', 'rql'),
                              ('u', 'n', 'long', 'lat'))

        self.assertTupleEqual(getvars('''
                  prefix db-owl: <http://dbpedia.org/ontology/>
                  prefix db-prop: <http://fr.dbpedia.org/property/>
                  select ?ville, ?name, ?long, ?lat where {
                       ?ville db-owl:country <http://fr.dbpedia.org/resource/France> .
                       ?ville rdf:type db-owl:PopulatedPlace .
                       ?ville db-owl:populationTotal ?population .
                       ?ville foaf:name ?name .
                       ?ville db-prop:longitude ?long .
                       ?ville db-prop:latitude ?lat .
                       FILTER (?population > 1000)
                       }''', 'sparql'),
                              ('?ville', '?name', '?long', '?lat'))

    def test_getindexesfromvars(self):
        """ Test if we correctly get the indexes from variables """
        self.assertTupleEqual(getindexesfromvars("?ville, ?name, (?long, ?lat)",
                    """
                    prefix db-owl: <http://dbpedia.org/ontology/>
                    prefix db-prop: <http://fr.dbpedia.org/property/>
                    select ?ville, ?name, ?long, ?lat where {
                          ?ville db-owl:country <http://fr.dbpedia.org/resource/France> .
                          ?ville rdf:type db-owl:PopulatedPlace .
                          ?ville db-owl:populationTotal ?population .
                          ?ville foaf:name ?name .
                          ?ville db-prop:longitude ?long .
                          ?ville db-prop:latitude ?lat .
                          FILTER (?population > 1000)
                          }""", 'sparql'),
                              (0, 1, (2, 3)))

        self.assertTupleEqual(getindexesfromvars("U, N, (LONG, LAT)",
                '''
                Any U, N, LONG,
                LAT WHERE X is Location, X name N, X country C,
                C name "France", X longitude LONG, X
                latitude LAT, X population > 1000, X
                feature_class "P", X cwuri U
                ''', 'rql'), (0, 1, (2, 3)))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

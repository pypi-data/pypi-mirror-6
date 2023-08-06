# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

""" Request on http://fr.dbpedia.org/sparql
prefix db-owl: <http://dbpedia.org/ontology/>
 select ?ville ?code ?name ?lat ?long ?dep ?depcode ?depname where {
    ?ville db-owl:country <http://fr.dbpedia.org/resource/France> . 
    ?ville dbpedia-owl:inseeCode ?code.
    ?ville foaf:name ?name.
    ?ville dbpedia-owl:department ?dep.
    ?dep dbpedia-owl:inseeCode ?depcode.
    ?dep foaf:name ?depname.
    ?ville geo:lat ?lat.
    ?ville geo:long ?long.
 }

"""
import sys
import json
import urllib

from cubicweb.dataimport import SQLGenObjectStore

filename = sys.argv[-1]
store = SQLGenObjectStore(session)
data = json.load(open(filename))
data = data['results']['bindings']
exturis = dict(store.rql('Any U, X WHERE X is ExternalUri, X uri U'))
departements = {}

for commune in data:
    # Departement
    departement = commune['depcode']['value']
    if departement in departements:
        depeid = departements[departement]
    else:
        depeid = store.create_entity('Departement',
                                     code=departement,
                                     nom=commune['depname']['value']).eid
        departements[departement] = depeid
        uri = commune['dep']['value']
        if uri in exturis:
            uri_eid = exturis[uri]
        else:
            uri_eid = store.create_entity('ExternalUri', uri=uri).eid
            exturis[uri] = uri_eid
        store.relate(depeid, 'same_as', uri_eid)
    # Commune
    c = store.create_entity('Commune',
                            departement=depeid,
                            code=commune['code']['value'],
                            nom=commune['name']['value'],
                            latitude=float(commune['lat']['value']),
                            longitude=float(commune['long']['value'])).eid
    uri = commune['ville']['value']
    if uri in exturis:
        uri_eid = exturis[uri]
    else:
        uri_eid = store.create_entity('ExternalUri', uri=uri).eid
        exturis[uri] = uri_eid
    store.relate(c, 'same_as', uri_eid)
store.flush()
store.commit()

# Add Paris...
depeid = session.create_entity('Departement', code=u'75', nom=u'Paris').eid
uri_eid = session.create_entity('ExternalUri', uri=u'http://fr.dbpedia.org/page/Paris').eid
session.add_relation(depeid, 'same_as', uri_eid)
for arr in range(1, 20):
    for subcode in ('751', '750'):
        c = session.create_entity('Commune',
                                  departement=depeid,
                                  code=subcode + u'%02d' % arr,
                                  nom=u'Paris %s' %arr,
                                  latitude=48.856579,
                                  longitude=2.351828).eid
        session.add_relation(c, 'same_as', uri_eid)

# Create geometry
rset = session.execute('Any X, LA, LO WHERE X latitude LA, X longitude LO, X is Commune')
data = [{'eid': eid, 'geometry': 'POINT(%s %s)' % (lo, la)} for eid, la, lo in rset
        if la and lo and str(la) != 'nan' and str(lo) != 'nan']
cnx = session.repo.system_source.get_connection()
crs = cnx.cursor()
crs.executemany("UPDATE cw_commune SET cw_geometry=ST_GeomFromText(%(geometry)s, 4326) "
                "WHERE cw_eid=%(eid)s", data)
cnx.commit()
cnx.close()

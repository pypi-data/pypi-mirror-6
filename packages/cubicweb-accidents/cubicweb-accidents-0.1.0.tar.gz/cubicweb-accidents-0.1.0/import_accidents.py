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

""" Importers of files """
import sys
import csv
import datetime
from itertools import izip

from cubicweb.dataimport import ucsvreader

from cubes.dataio.dataimport import MassiveObjectStore

filename = sys.argv[-1]

store = MassiveObjectStore(session, replace_sep=u' ',
                           commit_at_flush=False,
                           autoflush_metadata=False)
organismes = dict(rql('Any C, X WHERE X is Organisme, X code C'))
luminosites = dict(rql('Any C, X WHERE X is Luminosite, X code C'))
agglomerations = dict(rql('Any C, X WHERE X is Agglomeration, X code C'))
intersections = dict(rql('Any C, X WHERE X is Intersection, X code C'))
meteos = dict(rql('Any C, X WHERE X is Meteo, X code C'))
collisions = dict(rql('Any C, X WHERE X is Collision, X code C'))
routes = dict(rql('Any C, X WHERE X is Route, X code C'))
infrastructures = dict(rql('Any C, X WHERE X is Infrastructure, X code C'))
circulations = dict(rql('Any C, X WHERE X is Circulation, X code C'))
situations = dict(rql('Any C, X WHERE X is Situation, X code C'))
voiespeciales = dict(rql('Any C, X WHERE X is VoieSpeciale, X code C'))
profils = dict(rql('Any C, X WHERE X is Profil, X code C'))
traces = dict(rql('Any C, X WHERE X is TracePlan, X code C'))
communes = dict(rql('Any C, X WHERE X is Commune, X code C'))
departements = dict(rql('Any C, X WHERE X is Departement, X code C'))
vehicules = {}
for c, x in rql('Any C, X WHERE X is Vehicule, X numac C'):
    vehicules.setdefault(c, []).append(x)


for ind, line in enumerate(ucsvreader(open(filename),
                                      encoding='latin-1', separator=',', quote='"',
                                      skipfirst=True, ignore_errors=True)):
    if not len(line) == 36:
        print 'Malformed line !!!'
        continue
    depcode = str(int(line[7][:-1]))
    if depcode in departements:
        departement = departements[depcode]
    else:
        departement = None
        print 'Unknown departement', depcode
    comcode = int(line[6])
    comcode = '%s%03d' % (depcode, comcode)
    if comcode in communes:
        commune = communes[comcode]
    else:
        commune = None
        print 'Unknown commune', comcode
    if not line[35]:
        print 'Unknown numac !!!'
        continue
    entity = store.create_entity('Accident', numac=int(line[35]),
                                 organisme=organismes[int(line[0])] if line[0] else organismes[0],
                                 luminosite=luminosites[int(line[1])] if line[1] else luminosites[0],
                                 agglomeration=agglomerations[int(line[2])] if line[2] else agglomerations[0],
                                 intersection=intersections[int(line[3])] if line[3] else intersections[0],
                                 meteo=meteos[int(line[4])] if line[4] else meteos[0],
                                 collision=collisions[int(line[5])] if line[5] else collisions[0],
                                 commune=commune,
                                 departement=departement,
                                 route=routes[int(line[8])] if line[8] else routes[0],
                                 infrastructure=infrastructures[int(line[9])] if line[9] else infrastructures[0],
                                 voie=line[10],
                                 v1=line[11],
                                 v2=line[12],
                                 circulation=circulations[int(line[13])] if line[13] else circulations[0],
                                 nb_voies_total=int(line[14]) if line[14] else None,
                                 pr=line[15],
                                 pr1=line[16],
                                 voie_speciale=voiespeciales[int(line[17])] if line[17] else voiespeciales[0],
                                 profil=profils[int(line[18])] if line[18] else profils[0],
                                 trace_plan=traces[int(line[19])] if line[19] else traces[0],
                                 situation=situations[int(line[20])] if line[20] else situations[0],
                                 nb_tues=int(line[21]),
                                 nb_hospitalises=int(line[22]),
                                 nb_blesses=int(line[23]),
                                 nb_indemnes=int(line[24]),
                                 numero=line[26],
                                 distance=float(line[27]) if line[27] else None,
                                 libelle_voie=line[28],
                                 code_rivoli=line[29],
                                 gravite=float(line[30]),
                                 gps=line[31],
                                 latitude=float(line[32]) if line[32] and line[32].isdigit() else None,
                                 longitude=float(line[33]) if line[33] and line[33].isdigit() else None,
                                 adresse=line[34])
    for veh in  vehicules.get(int(line[35]), []):
        store.relate(entity.eid, 'implique', veh)
    if ind and ind % 50000 == 0:
        store.flush()

store.flush()
store.flush_meta_data()
store.cleanup()

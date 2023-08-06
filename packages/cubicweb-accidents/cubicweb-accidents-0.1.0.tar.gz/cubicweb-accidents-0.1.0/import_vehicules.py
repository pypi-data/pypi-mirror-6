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

from cubes.dataio.dataimport import MassiveObjectStore

filename = sys.argv[-1]

store = MassiveObjectStore(session, replace_sep=u' ',
                           commit_at_flush=False,
                           autoflush_metadata=False)
categories = dict(rql('Any C, X WHERE X is CategorieVehicule, X code C'))
appartenances = dict(rql('Any C, X WHERE X is AppartenanceVehicule, X code C'))
affectations = dict(rql('Any C, X WHERE X is AffectationVehicule, X code C'))
csvobj = csv.reader(open(filename), delimiter=',')
csvobj.next()
for ind, line in enumerate(csvobj):
    annee = int(line[5]) if line[5] else None
    mois = int(line[6]) if line[6] else None
    if annee and mois:
        date = datetime.date(annee, mois, 1)
    else:
        date = None
    # Affectation
    if line[2]:
        affectation = affectations.get(int(line[2]), affectations[0])
    else:
        affectation = affectations[0]
    # Appartenance
    if line[3]:
        appartenance = appartenances.get(int(line[3]), appartenances[0])
    else:
        appartenance = appartenances[0]
    entity = store.create_entity('Vehicule', numac=int(line[0]),
                                 categorie=categories[int(line[1])],
                                 affectation=affectation,
                                 appartenance=appartenance,
                                 assurance=True if line[4] == '1' else False,
                                 presentation_assurance=False if line[4] == '3' else True,
                                 annee_mise_circulation = annee,
                                 mois_mise_circulation = mois,
                                 mise_circulation = date,
                                 nb_tues = int(line[7]) if line[7] else 0,
                                 nb_hospitalises = int(line[8]) if line[8] else 0,
                                 nb_blesses = int(line[9]) if line[9] else 0,
                                 nb_indemnes = int(line[10]) if line[10] else 0)

store.flush()
store.flush_meta_data()
store.cleanup()

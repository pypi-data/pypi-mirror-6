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

"""cubicweb-accidents schema"""


from yams.buildobjs import EntityType, RelationDefinition, String, Date, Int, Float

from cubicweb.schemas.base import EmailAddress

from cubes.postgis.schema import Geometry


class Departement(EntityType):
    nom = String(indexed=True, maxsize=1024, fulltextindexed=True)
    code = String(indexed=True, maxsize=16) # Code INSEE
    same_as = SubjectRelation('ExternalUri', cardinality='**')


class Commune(EntityType):
    nom = String(indexed=True, maxsize=1024, fulltextindexed=True)
    code = String(indexed=True, maxsize=16) # Code INSEE
    departement = SubjectRelation('Departement', cardinality='?*', inlined=True)
    same_as = SubjectRelation('ExternalUri', cardinality='**')
    latitude = Float(indexed=True)
    longitude = Float(indexed=True)
    geometry = Geometry(geom_type='POINT', srid=4326, coord_dimension=2)


class Accident(EntityType):
    numac = Int(indexed=True)
    organisme = SubjectRelation('Organisme', cardinality='1*', inlined=True)
    luminosite = SubjectRelation('Luminosite', cardinality='1*', inlined=True)
    agglomeration = SubjectRelation('Agglomeration', cardinality='1*', inlined=True)
    intersection = SubjectRelation('Intersection', cardinality='1*', inlined=True)
    meteo = SubjectRelation('Meteo', cardinality='1*', inlined=True)
    collision = SubjectRelation('Collision', cardinality='1*', inlined=True)
    route = SubjectRelation('Route', cardinality='1*', inlined=True)
    situation = SubjectRelation('Situation', cardinality='1*', inlined=True)
    circulation = SubjectRelation('Circulation', cardinality='1*', inlined=True)
    infrastructure = SubjectRelation('Infrastructure', cardinality='1*', inlined=True)
    voie_speciale = SubjectRelation('VoieSpeciale', cardinality='1*', inlined=True)
    profil = SubjectRelation('Profil', cardinality='1*', inlined=True)
    trace_plan = SubjectRelation('TracePlan', cardinality='1*', inlined=True)
    adresse = String(fulltextindexed=True)
    numero = String(fulltextindexed=True)
    libelle_voie = String(fulltextindexed=True)
    code_rivoli = String(maxsize=16, indexed=True)
    departement = SubjectRelation('Departement', cardinality='1*', inlined=True)
    commune = SubjectRelation('Commune', cardinality='1*', inlined=True)
    gps = String(maxsize=8, indexed=True)
    latitude = Float(indexed=True)
    longitude = Float(indexed=True)
    voie = String(maxsize=8)
    nb_voies_total = Int(indexed=True)
    v1 = String(maxsize=1024)
    v2 = String(maxsize=1024)
    pr = String(maxsize=256)
    pr1 = String(maxsize=256)
    distance = Float(indexed=True)
    nb_tues = Int(indexed=True)
    nb_hospitalises = Int(indexed=True)
    nb_blesses = Int(indexed=True)
    nb_indemnes = Int(indexed=True)
    gravite = Float(indexed=True)


class Organisme(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Luminosite(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Agglomeration(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Intersection(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Meteo(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Collision(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Route(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Situation(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Circulation(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Infrastructure(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class VoieSpeciale(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Profil(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class TracePlan(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class Vehicule(EntityType):
    numac = Int(indexed=True)
    categorie = SubjectRelation('CategorieVehicule', cardinality='1*', inlined=True)
    appartenance = SubjectRelation('AppartenanceVehicule', cardinality='1*', inlined=True)
    affectation = SubjectRelation('AffectationVehicule', cardinality='1*', inlined=True)
    mise_circulation = Date(indexed=True)
    annee_mise_circulation = Int(indexed=True)
    mois_mise_circulation = Int(indexed=True)
    assurance = Boolean(indexed=True)
    presentation_assurance = Boolean(indexed=True)
    # Stats
    nb_tues = Int(indexed=True)
    nb_hospitalises = Int(indexed=True)
    nb_blesses = Int(indexed=True)
    nb_indemnes = Int(indexed=True)


class AppartenanceVehicule(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class AffectationVehicule(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class CategorieVehicule(EntityType):
    nom = String(maxsize=1024, fulltextindexed=True, required=True)
    code = Int(indexed=True)


class implique(RelationDefinition):
    subject = 'Accident'
    object = 'Vehicule'

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

"""cubicweb-accidents postcreate script, executed at instance creation time or when
the cube is added to an existing instance.

You could setup site properties or a workflow here for example.
"""

set_property('ui.site-title', "Data.gouv.fr Accidents")

# Categories (fichier ETALAB VEHICULES)
for code, nom in ((1, u'Bicyclette'),
                  (2, u'Cyclomoteur <50cm3'),
                  (3, u'Voiturette (Quadricycle à moteur carrossé) (anciennement "voiturette ou tricycle à moteur")'),
                  (4, u'Référence plus utilisée depuis 2006 (scooter immatriculé)'),
                  (5, u'Référence plus utilisée depuis 2006 (motocyclette)'),
                  (6, u'Référence plus utilisée depuis 2006 (side-car)'),
                  (7, u'VL seul'),
                  (8, u'Catégorie plus utilisée (VL + caravane)'),
                  (9, u'Catégorie plus utilisée (VL + remorque)'),
                  (10, u'VU seul 1,5T <= PTAC <= 3,5T avec ou sans remorque (anciennement VU seul 1,5T <= PTAC <= 3,5T)'),
                  (11, u'Référence plus utilisée depuis 2006 (VU (10) + caravane)'),
                  (12, u'Référence plus utilisée depuis 2006 (VU (10) + remorque)'),
                  (13, u'PL seul 3,5T <PTCA <= 7,5T'),
                  (14, u'PL seul > 7,5T'),
                  (15, u'PL > 3,5T + remorque'),
                  (16, u'Tracteur routier seul'),
                  (17, u'Tracteur routier + semi-remorque'),
                  (18, u'Référence plus utilisée depuis 2006 (transport en commun)'),
                  (19, u'Référence plus utilisée depuis 2006 (tramway)'),
                  (20, u'Engin spécial'),
                  (21, u'Tracteur agricole'),
                  (30, u'Scooter < 50 cm3'),
                  (31, u'Motocyclette > 50 cm3 et <= 125 cm3'),
                  (32, u'Scooter > 50 cm3 et <= 125 cm3'),
                  (33, u'Motocyclette > 125 cm3'),
                  (34, u'Scooter > 125 cm3'),
                  (35, u'Quad léger <= 50 cm3 (Quadricycle à moteur non carrossé)'),
                  (36, u'Quad lourd > 50 cm3 (Quadricycle à moteur non carrossé)'),
                  (37, u'Autobus'),
                  (38, u'Autocar'),
                  (39, u'Train'),
                  (40, u'Tramway'),
                  (99, u'Autre véhicule')):
    session.create_entity('CategorieVehicule', nom=nom, code=code)

for code, nom in ((0, u'Non renseigné'),
                  (1, u'Conducteur'),
                  (2, u'Véhicule volé'),
                  (3, u'Propriétaire consentant'),
                  (4, u'Administration'),
                  (5, u'Entreprise')):
    session.create_entity('AppartenanceVehicule', nom=nom, code=code)

for code, nom in ((0, u'Non renseigné'),
                  (1, u'Taxi'),
                  (2, u'Ambulance'),
                  (3, u'Pompier'),
                  (4, u'Police - Gendarmerie'),
                  (5, u'Transport scolaire'),
                  (6, u'Matières dangereuses'),
                  (7, u'Autre')):
    session.create_entity('AffectationVehicule', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Gendarmerie'),
                  (2, u'Préfecture de Police de Paris'),
                  (3, u'C.R.S.'),
                  (4, u'P.A.F.'),
                  (5, u'Sécurité publique')):
    session.create_entity('Organisme', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Plein jour'),
                  (2, u'Crépuscule ou aube'),
                  (3, u'Nuit sans éclairage public'),
                  (4, u'Nuit avec éclairage public non allumé'),
                  (5, u'Nuit avec éclairage public allumé')):
   session.create_entity('Luminosite', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Hors agglomération'),
                  (2, u'Agglomération de moins de 2 000 habitants'),
                  (3, u'Agglomération entre 2 000 habitants et 5 000 habitants'),
                  (4, u'Agglomération entre 5 000 habitants et 10 000 habitants'),
                  (5, u'Agglomération entre 10 000 habitants et 20 000 habitants'),
                  (6, u'Agglomération entre 20 000 habitants et 50 000 habitants'),
                  (7, u'Agglomération entre 50 000 habitants et 100 000 habitants'),
                  (8, u'Agglomération entre 100 000 habitants et 300 000 habitants'),
                  (9, u'Agglomération de plus de 300 000 habitants')):
   session.create_entity('Agglomeration', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Hors intersection'),
                  (2, u'Intersection en X'),
                  (3, u'Intersection en T'),
                  (4, u'Intersection en Y'),
                  (5, u'Intersection à plus de 4 branches'),
                  (6, u'Giratoire'),
                  (7, u'Place'),
                  (8, u'Passage à niveau'),
                  (9, u'Autre intersection')):
   session.create_entity('Intersection', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Normale'),
                  (2, u'Pluie légère'),
                  (3, u'Pluie forte'),
                  (4, u'Neige - grêle'),
                  (5, u'Brouillard - fumée'),
                  (6, u'Vent fort - tempête'),
                  (7, u'Temps éblouissant'),
                  (8, u'Temps couvert'),
                  (9, u'Autre')):
   session.create_entity('Meteo', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Deux véhicules - frontale'),
                  (2, u'Deux véhicules – par l’arrière'),
                  (3, u'Deux véhicules – par le coté'),
                  (4, u'Trois véhicules et plus – en chaîne'),
                  (5, u'Trois véhicules et plus - collisions multiples'),
                  (6, u'Autre collision'),
                  (7, u'Sans collision')):
    session.create_entity('Collision', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Autoroute'),
                  (2, u'Route Nationale'),
                  (3, u'Route Départementale'),
                  (4, u'Voie Communale'),
                  (5, u'Hors réseau public'),
                  (6, u'Parc de stationnement ouvert à la circulation publique'),
                  (9, u'autre')):
    session.create_entity('Route', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Souterrain - tunnel'),
                  (2, u'Pont - autopont'),
                  (3, u'Bretelle d’échangeur ou de raccordement'),
                  (4, u'Voie ferrée'),
                  (5, u'Carrefour aménagé'),
                  (6, u'Zone piétonne'),
                  (7, u'Zone de péage')):
    session.create_entity('Infrastructure', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Sur chaussée'),
                  (2, u'Sur bande d’arrêt d’urgence'),
                  (3, u'Sur accotement'),
                  (4, u'Sur trottoir'),
                  (5, u'Sur piste cyclable')):
    session.create_entity('Situation', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'A sens unique'),
                  (2, u'Bidirectionnelle'),
                  (3, u'A chaussées séparées'),
                  (4, u'Avec voies d’affectation variable')):
    session.create_entity('Circulation', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Piste cyclable'),
                  (2, u'Bande cyclable'),
                  (3, u'Voie réservée')):
    session.create_entity('VoieSpeciale', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Plat'),
                  (2, u'Pente'),
                  (3, u'Sommet de côte'),
                  (4, u'Bas de côte')):
    session.create_entity('Profil', nom=nom, code=code)


for code, nom in ((0, u'Non renseigné'),
                  (1, u'Partie rectiligne'),
                  (2, u'En courbe à gauche'),
                  (3, u'En courbe à'),
                  (4, u'En « S »')):
    session.create_entity('TracePlan', nom=nom, code=code)



# Card
content = u"""Ce protoype est issue de l'opendata camp du 16 avril.
Les données des fichiers des accidents routiers de data.gouv.fr ont été modèlisées,
et importées dans une base CubicWeb.

Il est ainsi possible d'interroger finement les données et de pouvoir extraire de statistiques
et des cohortes d'études intéressantes.
<br>
<br>
Merci aux organisateurs et à l'équipe du projet.
<br>
<br>
Informations supplémentaires:
<ul>
<li>Le <a href='http://www.cubicweb.org/'>cadriciel CubicWeb</a></li>
<li>Les deux fichiers sont disponibles sur <a href='http://www.data.gouv.fr/fr/dataset/base-de-donnees-accidents-corporels-de-la-circulation-sur-6-annees'>data.gouv.fr</a></li>
<li>Le code est disponible <a href='http://hg.logilab.org/users/vmichel/cubes/accidents/'>ici</a></li>
<li>Le <a href='http://demo.cubicweb.org/accidents/schema'>schéma</a> de l'application et un tutoriel
sur le language <a href='https://demo.cubicweb.org/accidents/doc/tut_rql>RQL</a></li>
</ul>
"""

session.create_entity('Card', content_format=u'text/html', wikiid=u'index', title=u'index', content=content)


content = u"""Quelques exemples de requêtes:
<ul>
<li>Nombre de véhicules impliqués dans un accident par année de mise en circulation
<blockquote>
<a href='https://demo.cubicweb.org/accidents/?rql=Any A, COUNT(X) GROUPBY A WHERE X annee_mise_circulation A'>Any A, COUNT(X) GROUPBY A WHERE X annee_mise_circulation A</a>
</blockquote>
</li>
<li>Accidents triés par nombre de véhicules impliqués
<blockquote>
<a href='https://demo.cubicweb.org/accidents/?rql=Any X,COUNT(V) GROUPBY X ORDERBY 2 DESC WHERE X implique V'>Any X,COUNT(V) GROUPBY X ORDERBY 2 DESC WHERE X implique V</a>
</blockquote>
</li>
<li>Accidents triés par nombre de véhicules impliqués, luminosité et conditions météos
<blockquote>
<a href='https://demo.cubicweb.org/accidents/?rql=Any L,M,COUNT(V) GROUPBY L,M,X ORDERBY 3 DESC WHERE X implique V, X luminosite L, X meteo M'>Any L,M,COUNT(V) GROUPBY L,M,X ORDERBY 3 DESC WHERE X implique V, X luminosite L, X meteo M</a>
</blockquote>
</li>
<li>Nombre d'accidents par commune/département dans des conditions 'Neige - grêle', et export en CSV
<blockquote>
<a href='https://demo.cubicweb.org/accidents/?rql=Any C,D,COUNT(X) GROUPBY C,D WHERE X meteo M, M code 4, X commune C, X departement D&vid=csvexport'>Any C,D,COUNT(X) GROUPBY C,D WHERE X meteo M, M code 4, X commune C, X departement D</a> et 'vid=csvexport' dans l'url
</blockquote>
</li>
</ul>
"""
session.create_entity('Card', content_format=u'text/html', wikiid=u'examples', title=u'examples', content=content)

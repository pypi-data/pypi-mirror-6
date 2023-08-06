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

"""cubicweb-accidents views/forms/actions/components for web ui"""
from cubicweb.web import facet
from cubicweb.selectors import is_instance, match_user_groups
from cubicweb.web.views import uicfg
from cubicweb.web.views.boxes import EditBox
from cubicweb.web.views.bookmark import BookmarksBox
from cubicweb.web.views.startup import IndexView

from cubes.bootstrap.views.basecomponents import BSRQLInputForm


# Always make RQL input form visible for the main page
BSRQLInputForm.visible = True
# Avoid empty left column for anon
BookmarksBox.__select__ = BookmarksBox.__select__ & match_user_groups('users', 'managers')
EditBox.__select__ = EditBox.__select__ & match_user_groups('users', 'managers')


_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl
_pvs.tag_subject_of(('Accident', 'implique', '*'), 'relations')
_pvdc.tag_subject_of(('Accident', 'implique', '*'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'implique', 'Vehicule'), 'attributes')
_pvs.tag_object_of(('*', 'organisme', 'Organisme'), 'relations')
_pvdc.tag_object_of(('*', 'organisme', 'Organisme'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'luminosite', 'Luminosite'), 'relations')
_pvdc.tag_object_of(('*', 'luminosite', 'Luminosite'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'agglomeration', 'Agglomeration'), 'relations')
_pvdc.tag_object_of(('*', 'agglomeration', 'Agglomeration'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'intersection', 'Intersection'), 'relations')
_pvdc.tag_object_of(('*', 'intersection', 'Intersection'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'meteo', 'Meteo'), 'relations')
_pvdc.tag_object_of(('*', 'meteo', 'Meteo'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'collision', 'Collision'), 'relations')
_pvdc.tag_object_of(('*', 'collision', 'Collision'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'route', 'Route'), 'relations')
_pvdc.tag_object_of(('*', 'route', 'Route'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'situation', 'Situation'), 'relations')
_pvdc.tag_object_of(('*', 'situation', 'Situation'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'infrastructure', 'Infrastructure'), 'relations')
_pvdc.tag_object_of(('*', 'infrastructure', 'Infrastructure'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'voie_speciale', 'VoieSpeciale'), 'relations')
_pvdc.tag_object_of(('*', 'voie_speciale', 'VoieSpeciale'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'profil', 'Profil'), 'relations')
_pvdc.tag_object_of(('*', 'profil', 'Profil'), {'limit': None, 'vid': 'table'})
_pvs.tag_object_of(('*', 'trace_plan', 'TracePlan'), 'relations')
_pvdc.tag_object_of(('*', 'trace_plan', 'TracePlan'), {'limit': None, 'vid': 'table'})


class AccidentsIndexView(IndexView):

    def call(self, **kwargs):
        w = self.w
        # Presentation
        w(u'<h2>%s</h2>' % self._cw.property_value('ui.site-title'))
        rset = self._cw.execute('Any X WHERE X is Card, X wikiid %(t)s', {'t': 'index'})
        if rset:
            w(u'<p>%s</p>' % rset.get_entity(0, 0).printable_value('content'))
        # Browse
        self.w(u'<div class="row">')
        for etype in ('Accident', 'Vehicule'):
            self.w(u'<div class="col-md-offset-1 col-md-4">')
            self.w(u'<div class="panel panel-primary">')
            self.w(u'<div class="panel-heading"><h3 class="panel-title">%s</h3></div>'
                   % self._cw._(etype))
            content = self._cw._('Voir les %(t)s disponibles en base' % {'t': self._cw._(etype)})
            url = self._cw.build_url(rql='Any X WHERE X is %s' % etype)
            content = u'<a href="%s">%s</a>' % (url, content)
            self.w(u'<div class="panel-body">%s</div>' % content)
            self.w(u'</div>')
            self.w(u'</div>')
        self.w(u'</div>')
        # Search
        self.w(u'<div class="row">')
        # RQL
        self.w(u'<div class="col-md-offset-1 col-md-9">')
        self.w(u'<div class="panel panel-info">')
        self.w(u'<div class="panel-heading"><h3 class="panel-title">%s</h3></div>'
               % self._cw._('Explorez en RQL'))
        self.w(u'<div class="panel-body">')
        self.w(self._cw._("RQL est un language de requete semantic permettant une recherche en profondeur des donnees avec une reelle simplicite d'utilisation. Vous pouvez consulter la <a href='%(doc)s'>documentation</a> ou voir le <a href='%(schema)s'>modele de donnees</a>")
               % {'doc': self._cw.build_url('doc/tut_rql'),
                  'schema': self._cw.build_url('schema')})
        rset = self._cw.execute('Any X WHERE X is Card, X wikiid %(t)s', {'t': 'examples'})
        if rset:
            w(u'<p>%s</p>' % rset.get_entity(0, 0).printable_value('content'))
        self.w(u'</div></div></div>')
        self.w(u'</div>')# Row


# Facets - Vehicules
class VehiculeMiseCirculationFacet(facet.DateRangeFacet):
    __regid__ = 'vehicules.misecirculation'
    __select__ = is_instance('Vehicule')
    rtype = 'mise_circulation'

class VehiculeAssuranceFacet(facet.AttributeFacet):
    __regid__ = 'vehicules.assurance'
    __select__ = is_instance('Vehicule')
    rtype = 'assurance'

class VehiculePresentationAssuranceFacet(facet.AttributeFacet):
    __regid__ = 'vehicules.presentationassurance'
    __select__ = is_instance('Vehicule')
    rtype = 'presentation_assurance'

class VehiculeTuesFacet(facet.RangeFacet):
    __regid__ = 'vehicules.tues'
    __select__ = is_instance('Vehicule')
    rtype = 'nb_tues'

class VehiculeHospitalisesFacet(facet.RangeFacet):
    __regid__ = 'vehicules.hospitalises'
    __select__ = is_instance('Vehicule')
    rtype = 'nb_hospitalises'

class VehiculeBlessesFacet(facet.RangeFacet):
    __regid__ = 'vehicules.blesses'
    __select__ = is_instance('Vehicule')
    rtype = 'nb_blesses'

class VehiculeIndemnesFacet(facet.RangeFacet):
    __regid__ = 'vehicules.indemnes'
    __select__ = is_instance('Vehicule')
    rtype = 'nb_indemnes'


# Facets - Accident
class AccidentTuesFacet(facet.RangeFacet):
    __regid__ = 'accidents.tues'
    __select__ = is_instance('Accident')
    rtype = 'nb_tues'

class AccidentHospitalisesFacet(facet.RangeFacet):
    __regid__ = 'accidents.hospitalises'
    __select__ = is_instance('Accident')
    rtype = 'nb_hospitalises'

class AccidentBlessesFacet(facet.RangeFacet):
    __regid__ = 'accidents.blesses'
    __select__ = is_instance('Accident')
    rtype = 'nb_blesses'

class AccidentIndemnesFacet(facet.RangeFacet):
    __regid__ = 'accidents.indemnes'
    __select__ = is_instance('Accident')
    rtype = 'nb_indemnes'

class AccidentDistanceFacet(facet.RangeFacet):
    __regid__ = 'accidents.distance'
    __select__ = is_instance('Accident')
    rtype = 'distance'

class AccidentGraviteFacet(facet.RangeFacet):
    __regid__ = 'accidents.gravite'
    __select__ = is_instance('Accident')
    rtype = 'gravite'

class AccidentOrganismeFacet(facet.RelationFacet):
    __regid__ = 'accidents.organisme'
    __select__ = is_instance('Accident')
    rtype = 'organisme'
    target_attr = 'nom'

class AccidentMeteoFacet(facet.RelationFacet):
    __regid__ = 'accidents.meteo'
    __select__ = is_instance('Accident')
    rtype = 'meteo'
    target_attr = 'nom'

class AccidentAppartenanceFacet(facet.RQLPathFacet):
    __regid__ = 'accidents.appartenance'
    __select__ = is_instance('Accident')
    path = ['X implique A', 'A appartenance AP', 'AP nom N']
    filter_variable = 'AP'
    label_variable = 'N'
    title = 'Appartenance'

class AccidentAffectationFacet(facet.RQLPathFacet):
    __regid__ = 'accidents.affectation'
    __select__ = is_instance('Accident')
    path = ['X implique A', 'A affectation AP', 'AP nom N']
    filter_variable = 'AP'
    label_variable = 'N'
    title = 'Affectation'


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (AccidentsIndexView,))
    vreg.register_and_replace(AccidentsIndexView, IndexView)

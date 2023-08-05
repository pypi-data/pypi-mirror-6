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
"""cubicweb-leaflet views/forms/actions/components for web ui"""
import json

from cubicweb.utils import js_dumps, make_uid
from cubicweb.predicates import multi_columns_rset, non_final_entity, adaptable
from cubicweb.view import AnyRsetView

###############################################################################
### LEAFLET OBJECT ############################################################
###############################################################################
class LeafletMap(object):
    """widget class to render leaflet map

    Typical usage is::

        leaflet_map = LeafletMap()
        self.w(leaflet_map.render(self._cw, my_list_of_markers))

    The list of markers can either a python list or a url to a json file
    """
    default_settings = {
        'divid': 'map-geo',
        'width': '940px',
        'height': '400px',
        'minZoom': 1,
        'maxZoom': 18,
        'initialZoom': 2,
        'provider': 'osm',
        }

    providers = {
        'osm': {
            'url': 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'attribution': ('&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, '
                            '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'),
        },
        'esri-topomap': {
            'url': 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
            'attribution': ('{attribution.Esri} &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, '
                            'NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, '
                            'Esri China (Hong Kong), and the GIS User Community')
        },
        'esri-imagery': {
            'url': 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            'attribution': ('{attribution.Esri} &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, '
                            'Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community')
        }
    }

    def __init__(self, custom_settings={}):
        settings = self.default_settings.copy()
        settings.update(custom_settings)
        if isinstance(settings['provider'], basestring):
            settings['provider'] = self.providers[settings['provider']]
        self.settings = settings

    def render(self, req, datasource,  use_cdn=True):
        req.add_js('cubes.leaflet.js')
        if use_cdn:
            req.add_js('http://cdn.leafletjs.com/leaflet-0.4.5/leaflet.js',
                       localfile=False)
            req.add_css('http://cdn.leafletjs.com/leaflet-0.4.5/leaflet.css',
                        localfile=False)
            req.add_css('http://cdn.leafletjs.com/leaflet-0.4.5/leaflet.ie.css',
                        localfile=False, ieonly=True)
        else:
            req.add_js('leaflet.js')
            req.add_css('leaflet.css')
            req.add_css('leaflet.ie.css', ieonly=True)
        if self.settings.get('cluster'):
            req.add_js('leafletcluster/leaflet.markercluster.js')
            req.add_css( ('leafletcluster/MarkerCluster.css',
                          'leafletcluster/MarkerCluster.Default.css') )
        self._call_js_onload(req, datasource)
        return self.div_holder()

    def _call_js_onload(self, req, datasource):
        """ Call the JS function """
        req.add_onload("""
function initMap() {
    // this should check if your leaflet is available or wait if not.
    if (typeof L === "undefined") {
        window.setTimeout(initMap, 100);
        return;
    }
    cw.cubes.leaflet.renderLeafLetMap(%s, %s);
};
initMap();""" % (js_dumps(datasource), js_dumps(self.settings)))

    def div_holder(self):
        style = u''
        width = self.settings.get('width', 940)
        if width:
            if isinstance(width, int):
                width = '%spx' % width
            style += 'width: %s;' % width
        height = self.settings.get('height', 400)
        if height:
            if isinstance(height, int):
                height = '%spx' % height
            style += 'height: %s;' % height
        return u'<div id="%s" style="%s"></div>' % (self.settings['divid'], style)


class LeafletMultiPolygon(LeafletMap):
    """ LeafletMap class for plotting multipolygon.
    Should be used in a view.
    """

    def _call_js_onload(self, req, datasource):
        req.add_onload('mapData = [%s]' % datasource)
        req.add_onload('cw.cubes.leaflet.initMap(%s)' % js_dumps(self.settings))
        req.add_onload('cw.cubes.leaflet.plotMap(mapData, %s)' % js_dumps(self.settings))


class LeafletMultiPolygonValues(LeafletMap):
    """ LeafletMap class for plotting multipolygon with associated values.
    Should be used in a view.
    """

    def _call_js_onload(self, req, datasource):
        req.add_onload('mapData = [%s]' % datasource)
        req.add_onload('cw.cubes.leaflet.initMap(%s)' % js_dumps(self.settings))
        req.add_onload('cw.cubes.leaflet.plotMapValues(mapData, %s)' % js_dumps(self.settings))




###############################################################################
### LEAFLET VIEWS #############################################################
###############################################################################

class AbstractLeafletView(AnyRsetView):
    __abstract__ = True
    __regid__ = 'leaflet'
    title = _('Leaflet')
    paginable = False

    def call(self, custom_settings={}, use_cdn=True):
        """ View call """
        geomap = LeafletMap(self._update_settings(custom_settings))
        markers = self.build_markers(self.cw_rset)
        self.w(geomap.render(self._cw, datasource=markers, use_cdn=use_cdn))

    def _update_settings(self, custom_settings):
        """ Update the default settings with custom settings """
        settings = LeafletMap.default_settings
        settings.update(custom_settings)
        for attr, value in self._cw.form.iteritems():
            if attr in settings:
                settings[attr] = value
        if 'cluster' in self._cw.form:
            settings['cluster'] = True
        return settings

    def build_markers(self, rset):
        """ Build the markers from an rset """
        markers = []
        for rownum, row in enumerate(self.cw_rset.rows):
            marker = self._build_markers_from_row(rset, rownum, row)
            if marker:
                markers.append(marker)
        return markers

    def _build_markers_from_row(self, rset, rownum, row):
        """ Build the markers from a row of the rset """
        raise NotImplementedError


class IGeocodableLeafletView(AbstractLeafletView):
    """ Simple leaflet view for IGeocodable entities.
    """
    __select__ = AbstractLeafletView.__select__ & adaptable('IGeocodable')

    def _build_markers_from_row(self, rset, rownum, row):
        """ Build a marker from an igeocodable entity """
        entity = rset.get_entity(rownum, 0)
        igeocodable = entity.cw_adapt_to('IGeocodable')
        if not igeocodable.latitude or not igeocodable.longitude:
            return
        marker = {}
        marker['eid'] = entity.eid
        marker['latitude'] = igeocodable.latitude
        marker['longitude'] = igeocodable.longitude
        marker['title'] = entity.dc_title()
        marker['url'] = entity.absolute_url()
        marker['description'] = entity.dc_description(format='text/html') or ''
        marker['icon'] = self.marker_icon(entity)
        marker['popup'] = '<h3><a href="{url}">{title}</a></h3>{description}'
        return marker

    def marker_icon(self, entity):
        return entity.cw_adapt_to('IGeocodable').marker_icon

class RowLeafletView(AbstractLeafletView):
    """ Simple leaflet view that try to convert the first column to latitude
    and the second column to longitude.
    """
    __select__ = AbstractLeafletView.__select__ & multi_columns_rset(2)

    def _build_markers_from_row(self, rset, rownum, row):
        """ Build a marker from a row of an rset, probably floats """
        marker = {}
        marker['eid'] = make_uid('marker')
        if not len(row)>=2 or not row[0] or not row[1]:
            return
        try:
            marker['latitude'] = float(row[0])
            marker['longitude'] = float(row[1])
        except TypeError, ValueError:
            return
        data = []
        for i in range(2, len(row)):
            if rset.description[rownum][i] == 'String' and row[i]:
                data.append(xml_escape(row[i]))
        if data:
            marker['title'] = data[0]
            marker['notes'] = data[1:]
            _d = [d for d in data if d.startswith('http://')]
            if _d:
                marker['url'] = _d[0]
        return marker


###############################################################################
### LEAFLET POLYGON VIEW ######################################################
###############################################################################
class GeoJsonView(AbstractLeafletView):
    """ Leaflet view that work on a single column rset.
    It expects GeoJson on the single column and will plot Multipolygon
    based on this GeoJson. This should be used with the postgis cube
    and the 'ASJSON' RQL function
    """
    title = _('GeoJson')
    __regid__ = 'leaflet-geojson'
    paginable = False
    __select__ = AbstractLeafletView.__select__ & multi_columns_rset(1)
    plotclass = LeafletMultiPolygon

    def call(self, custom_settings={}):
        """ View call """
        rset = self.cw_rset
        markers = self.build_markers(rset)
        settings = self._update_settings(custom_settings)
        geomap = self.plotclass(settings)
        self.w(geomap.render(self._cw, datasource=markers))

    def build_markers(self, rset):
        """ Build the markers from an rset """
        geometries = []
        for row in self.cw_rset.rows:
            geometries.append(row[0])
        return ', '.join(geometries)


class GeoJsonValuesView(AbstractLeafletView):
    """ Leaflet view that work on a two columns rset.
    It expects GeoJson on the first column, and the values associated
    with the json and the second one. It will plot Multipolygon
    based on this GeoJson. This should be used with the postgis cube
    and the 'ASJSON' RQL function
    """
    title = _('GeoJson')
    __regid__ = 'leaflet-geojson'
    paginable = False
    __select__ = AbstractLeafletView.__select__ & multi_columns_rset(2)
    plotclass = LeafletMultiPolygonValues

    def call(self, custom_settings={}):
        """ View call """
        rset = self.cw_rset
        markers = self.build_markers(rset)
        settings = self._update_settings(custom_settings)
        geomap = self.plotclass(settings)
        self.w(geomap.render(self._cw, datasource=markers))

    def build_markers(self, rset):
        """ Build the markers from an rset """
        geometries = []
        for row in self.cw_rset.rows:
            geometries.append('[%s, %s]' % (row[0], row[1]))
        return ', '.join(geometries)


$.format = function(str, sub) { // found on stackoverflow, use http://archive.plugins.jquery.com/node/14683/release ? or http://code.google.com/p/jquery-utils/wiki/StringFormat#Formatting
    return str.replace(/\{(.+?)\}/g, function($0, $1) {
        return $1 in sub ? sub[$1] : $0;
    });
};

var geojson, map;


cw.cubes.leaflet = new Namespace('cw.cubes.leaflet');

$.extend(cw.cubes.leaflet, {
    /**
     * @param datasource either a list or leaflet markers or an url deferencing json markers
     * @param settings leaflet settings
     **/
    renderLeafLetMap: function(datasource, settings) {
        function _renderMarkers(markers, settings) {
	    L.Icon.Default.imagePath = 'http://cdn.leafletjs.com/leaflet-0.4.5/images';
            // center on first marker if no center is specified
	    if (markers.length > 0) {
		var center = settings.center || [markers[0].latitude, markers[0].longitude];
	    } else {
		var center = [0, 0];
	    }
            var map = L.map(settings.divid).setView(center, settings.initialZoom);
            var osm = new L.TileLayer(settings.provider.url, {
                minZoom: settings.minZoom,
                maxZoom: settings.maxZoom,
                attribution: settings.provider.attribution});
            map.addLayer(osm);
            if (settings.cluster) {
                var cluster = new L.MarkerClusterGroup();
            }
            $.each(markers, function(_, marker) {
                var _marker = L.marker([marker.latitude, marker.longitude], {'iconUrl': L.icon(marker.icon)}, marker).bindPopup($.format(marker.popup, marker));
                if (settings.cluster) {
                    cluster.addLayer(_marker);
                } else {
                    _marker.addTo(map);
                }
            });
        }

        if ($.isArray(datasource)) {
            _renderMarkers(datasource, settings);
	} else {
            $.getJSON(datasource, function(markers) {
                _renderMarkers(markers, settings);
            });
        }
    },

    initMap: function(settings) {
    map = L.map(settings.divid);
    L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
        attribution: '{attribution.Esri} &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community',
        maxZoom: 18
    }).addTo(map);
    },


    defaultPolygoneStyle: function(data) {
    return {
        fillColor: '#800026',
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
		};
    },


    defaultLineStyle: function(data) {
    return {
        weight: 2,
        color: 'red'
	};
    },

    valuePolyStyle: function(data, min, delta) {
    return {
        fillColor: cw.cubes.leaflet._getColor(data, min, delta),
        weight: 0.5,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
		};
    },

    _getColor: function(val, min, delta) {
    return val > (min+0.9*delta) ? '#800026' :
           val > (min+0.75*delta) ? '#BD0026' :
           val > (min+0.6*delta)  ? '#E31A1C' :
           val > (min+0.5*delta)  ? '#FC4E2A' :
           val > (min+0.4*delta)  ? '#FD8D3C' :
           val > (min+0.25*delta)  ? '#FEB24C' :
           val > (min+0.1*delta)  ? '#FED976' :
		   '#FFEDA0';
    },

    plotMap: function(data, settings) {
	geojson = L.geoJson(data).addTo(map);
	map.setView([45, 2], 6);
	if (data[0].type == 'LineString')
	    {geojson.setStyle(cw.cubes.leaflet.defaultLineStyle);}
	else{
	    geojson.setStyle(cw.cubes.leaflet.defaultPolygoneStyle);}
    },

    plotMapValues: function(data, settings) {
	/* Compute min/max/delta */
	var min = data[0][1];
	var max = data[0][1];
	$.each(data, function(_, d) {
		   if (d[1]<min){min = d[1];};
		   if (d[1]>max){max = d[1];};
		   });
	var delta = max - min;
	$.each(data, function(_, d) {
		   geojson = L.geoJson(d[0], {style: cw.cubes.leaflet.valuePolyStyle(d[1], min, delta)}).addTo(map);
	       });
        map.setView([45, 2], 6);
}

});

/*
 * Initialize Map.
 */
function initializeMap(lat, lng, requestLocation){

    var latitude = lat;
    var longitude = lng;

    // Request user's current location.
    if(requestLocation && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            latitude = position.coords.latitude;
            longitude = position.coords.longitude;
            loadMap();
        });
    } else {
        loadMap();    
    }

    // Initialize map.
    function loadMap() {

        // Load map.
        var latlng = new google.maps.LatLng(latitude, longitude);
        var myOptions = {
            zoom: 15,
            center: latlng,
            navigationControl: true,
            scrollwheel: false,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
        };
        map = new google.maps.Map(document.getElementById('map'), myOptions);
        marker = new google.maps.Marker({ position: latlng, map: map, draggable: true });

        // When map finishes loading, fetch nearby places.
        google.maps.event.addListenerOnce(map, 'idle', function(){
            searchNearby(latitude, longitude, 3);
            $('.map-container .overlay').show();
        });

        // When map zoom changes, request nearby places taking the new radius into consideration.
        /*google.maps.event.addListener(map, 'zoom_changed', function() {
            searchNearby(latitude, longitude, getViewableRadius());
        });*/

        // When the user finishes dragging the marker, update lat/long and search nearby places.
        google.maps.event.addListener(marker, 'dragend', function() {
            latitude = marker.getPosition().lat();
            longitude = marker.getPosition().lng();
            searchNearby(latitude, longitude, 3);
        });
        
        // When the user clicks in the map, place the marker there, update lat/lon and search nearby places.
        google.maps.event.addListener(map, 'click', function(evt) {
            marker.setPosition(evt.latLng);
            latitude = marker.getPosition().lat();
            longitude = marker.getPosition().lng();
            searchNearby(latitude, longitude, 3);
        }); 
    }
}

/*
 * Fetch nearby places.
 */
function searchNearby(latitude, longitude, radius) {

    // Hide results and clear list.
    $('.map-container .overlay .content .results').hide();        
    $('.map-container .overlay .content .results table tbody').html('');

    // Hide 'no results' message.
    $('.map-container .overlay .content .no-results').hide();

    // Show loader.
    $('.map-container .overlay .content .loading').show();

    // Request data.
    var data = {
        latLng: latitude + ',' + longitude,
        radius: radius,
        pagination: false
    }

    // Submit API request.
    $.getJSON(places_api_url, data, function(data, status, xhr) {

        // Clear previous Place markers.
        for(var i=0; i<places.length; i++) { places[i].marker.setMap(null); }

        // a) There are no places for given query.
        if(data.length == 0) {

            // Hide loader.
            $('.map-container .overlay .content .loading').hide();

            // Show 'no results' message.
            $('.map-container .overlay .content .no-results').show();
            
        }
        // b) WE HAZ PLACES! Process places.
        else {

            // For each Place.
            for(var i=0; i<data.length; i++) {

                var place = data[i];
                
                places.push(new PlaceMarker(place));
                
                // Show in results list.
                var html = '<tr place-id="' + place.id + '">';
                html += '<td>';
                html += '<a href="' + place_href.replace('1', place.id).replace('place-slug', place.slug) + '">' + place.name + '</a>';
                if(place.active == false) {
                    html += ' <span class="label label-warning"><i class="fa fa-exclamation-triangle"></i> ' + gettext('Inactive') + '</span>';
                }
                html += '<div class="star-rating-sm"><div style="width:' + (place.rating.average*100/5) + '%"></div></div>';
                //html += '<br>';
                html += place.address + ', ' + place.postal_code + ' ' + place.city;
                html += '</td>';
                html += '</tr>';
                $('.map-container .overlay .content .results table tbody').prepend(html);
            }

            // When a place is hovered from the list, show it on the map.
            $('.map-container .overlay .content .results table tbody tr').on('click', function() {
                showPlace($(this).attr('place-id'));
            });

            // Hide loader.
            $('.map-container .overlay .content .loading').hide();

            // Show results.
            $('.map-container .overlay .content .results').show();
        }
    });
}

/*
 * Place's marker.
 */
function PlaceMarker(place){

    // Place.
    this.place = place;

    // Create map marker on Place's location.
    this.marker = new google.maps.Marker({
        position: new google.maps.LatLng(this.place.latitude, this.place.longitude),
        map: map,
        draggable: false,
        icon: this.place.marker_image_url
    });

    // Marker's infowindow.
    google.maps.event.addListener(this.marker, 'click', function() {
        if (infowindow && infowindow.place != this.place) {
            infowindow.close();
        }
        if(!infowindow || (infowindow && infowindow.place != this.place) || infowindow.getMap() == null) {
            var html = '<div style="text-align: left;">';
            html += '<a href="' + place_href.replace('1', place.id).replace('place-slug', place.slug) + '">' + this.place.name + '</a>';
            html += '<div class="star-rating-sm"><div style="width:' + (place.rating.average*100/5) + '%"></div></div>';
            html += place.address + ', ' + place.postal_code + ' ' + place.city;
            html += '</div>';
            infowindow = new google.maps.InfoWindow({ content: html, place: this.place });
            infowindow.open(map, this.marker);    
        }
    }.bind(this));
}

/*
 * Show Place's marker on map and center around its location.
 */
function showPlace(id) {
    for(var i=0; i<places.length; i++) {
        if(places[i].place.id == id) {
            map.setCenter(new google.maps.LatLng(places[i].place.latitude, places[i].place.longitude));
            google.maps.event.trigger(places[i].marker, 'click');
            break;
        }
    }
}

/*
 * Return the map's viewable area radius.
 */
function getViewableRadius() {
    
    var bounds = map.getBounds();
    var center = bounds.getCenter();
    var ne = bounds.getNorthEast();

    // r = radius of the earth in statute kilometers.
    var r = 6371;  

    // Convert lat or lng from decimal degrees into radians (divide by 57.2958).
    var lat1 = center.lat() / 57.2958; 
    var lon1 = center.lng() / 57.2958;
    var lat2 = ne.lat() / 57.2958;
    var lon2 = ne.lng() / 57.2958;

    // distance = circle radius from center to Northeast corner of bounds.
    var dis = r * Math.acos(Math.sin(lat1) * Math.sin(lat2) + Math.cos(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1));

    // Return.
    return dis;
}
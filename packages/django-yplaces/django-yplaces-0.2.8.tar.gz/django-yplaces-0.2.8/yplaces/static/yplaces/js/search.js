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

        // Load the map with the restaurant's coordinates
        var latlng = new google.maps.LatLng(latitude, longitude);
        var myOptions = {
            zoom: 15,
            center: latlng,
            navigationControl: true,
            scrollwheel: false,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
        };
        map = new google.maps.Map(document.getElementById('map'), myOptions);

        // Place a marker
        var marker = new google.maps.Marker({
            position: latlng,
            map: map,
        });

        // When map finishes loading, draw search results markers.
        google.maps.event.addListenerOnce(map, 'idle', function(){
            if(search_results.length > 0) {
                var bounds = new google.maps.LatLngBounds();
                for(var i=0; i<search_results.length; i++) {
                    var place = new PlaceMarker(search_results[i]);
                    places.push(place);
                    bounds.extend(place.marker.position);
                }
                map.fitBounds(bounds);    
            }
        });
    }
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
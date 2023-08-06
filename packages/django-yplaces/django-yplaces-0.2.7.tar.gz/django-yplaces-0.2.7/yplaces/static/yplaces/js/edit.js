/*
 * Initialize Form.
 */
function initializeForm() {

    // Initialize form validator.
    $('form').salsa();

    // Search address button.
    $('#search-address').on('click', function(){
        var address = $('#address').val() + ' ' + $('#postal_code').val() + ' ' + $('#city').val() + ' ' + $('#state').val() + ' ' + $('#country').val();
        searchAddress(address);
    });

    // If address changes, perform search.
    $('#address, #postal_code, #city, #state, #country').on('change', function(){
        if(action != 'PUT') {
            var address = $('#address').val() + ' ' + $('#postal_code').val() + ' ' + $('#city').val() + ' ' + $('#state').val() + ' ' + $('#country').val();
            searchAddress(address);
        }
    });

    // Listen to submit.
    $('#submit').on('click', function() {

        // Validate form.
        if(!$('form').salsa('validate')) { return; }

        // Disable submit button.
        $('#submit').attr('disabled', true);

        // Request data.
        var data = {
            active: $('#active').prop('checked'),
            name: $('#name').val(),
            address: $('#address').val(),
            postal_code: $('#postal_code').val(),
            city: $('#city').val(),
            state: $('#state').val(),
            country: $('#country').val(),
            latitude: $('#latitude').val(),
            longitude: $('#longitude').val(),
            phone_number: $('#phone_number').val(),
            email: $('#email').val(),
            website: $('#website').val()
        }

        // Submit request.
        $.ajax({
            url: api_url,
            type: action,
            data: JSON.stringify(data),
            dataType: 'JSON',
            success: function(data, status, xhr) {
                alert(gettext('Changes saved'));
                $('#submit').attr('disabled', false);
                if(next != '') { window.location = next; }
            },
            error: function(xhr, status, err) {
                $('form').salsa('processResponse', xhr.status, xhr.responseText);
                $('#submit').attr('disabled', false);
            }
        });
    });
}

/*
 * Initialize Map.
 */
function initializeMap(latitude, longitude, requestLocation){

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

        // Set form fields containing location information.
        $('form #latitude').val(latitude);
        $('form #longitude').val(longitude);

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
            
        // When the user finished dragging the marker, update lat/long
        google.maps.event.addListener(marker, 'dragend', function() {
            $('form #latitude').val(marker.getPosition().lat());
            $('form #longitude').val(marker.getPosition().lng());
        });
        
        // When the user clicks in the map, place the marker there
        google.maps.event.addListener(map, 'click', function(evt){
            marker.setPosition(evt.latLng);
            $('form #latitude').val(marker.getPosition().lat());
            $('form #longitude').val(marker.getPosition().lng());
        }); 
    }
}

/*
 * Search address.
 */
function searchAddress(address) {
    if(map && address){
        geocoder.geocode({ 'address': address }, function(results, status) {
            if(status == google.maps.GeocoderStatus.OK) {
                map.setCenter(results[0].geometry.location);
                map.setZoom(18);
                marker.setPosition(results[0].geometry.location);
                $('form #latitude').val(marker.getPosition().lat());
                $('form #longitude').val(marker.getPosition().lng());
                $('form #map-messages').html('');
            } else {
                $('form #map-messages').html('<div class="alert alert-warning">' + gettext('Address not found! Please place the marker in the correct location.') + '</div>');
            }
        }); 
    }
}
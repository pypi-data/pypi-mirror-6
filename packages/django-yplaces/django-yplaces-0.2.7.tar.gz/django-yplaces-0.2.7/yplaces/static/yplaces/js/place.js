/*
 * Initialize Map.
 */
function initializeMap(){

    // Load the map with the restaurant's coordinates
    var latlng = new google.maps.LatLng(place.latitude, place.longitude);
    var myOptions = {
        zoom: 15,
        center: latlng,
        navigationControl: true,
        scrollwheel: false,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
    };
    var map = new google.maps.Map(document.getElementById('map'), myOptions);

    // Place a marker
    var marker = new google.maps.Marker({
        position: latlng,
        map: map,
        title: place.name
    });
}


/*
 * Initialize Review Modal.
 */
function initializeReviewModal() {

    // Initialize form validator.
    $('#addReview form').salsa();

    // Clear form when modal is closed.
    $('#addReview').on('hidden.bs.modal', function(e) {
        $('#addReview form').salsa('clearErrors');
        $('#addReview #messages').html('');
        $('#addReview #rating').val('');
        $('#addReview #comment').val('');
        $('#addReview .star-rating-dynamic').find('span').each(function() { $(this).removeClass('star-rating-dynamic-active'); });
        $('#addReview input').val('');
        $('#addReview #preview').html('');
        $($('#addReview #preview').parent()).hide();
        $('#addReview #submit').button('reset');
    });

    // Set number of stars.
    $('#addReview .star-rating-dynamic span').on('click', function() {
        $('#addReview #rating').val($(this).attr('value'));
    });

    // Hovering out, displays current selection.
    $('#addReview .star-rating-dynamic').mouseleave(function() {
        var stars = $('#addReview #rating').val();
        for(var i=0; i<stars; i++) {
            $($('#addReview .star-rating-dynamic').find('span')[4-i]).addClass('star-rating-dynamic-active');  
        }
    });

    // Hovering in, hides current selection.
    $('#addReview .star-rating-dynamic').mouseenter(function() {
        $('#addReview .star-rating-dynamic').find('span').each(function() { $(this).removeClass('star-rating-dynamic-active'); });
    });

    // Listen to file selection.
    $('#addReview input').on('change', function() {
        var input = this;
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#addReview #preview').html('<img src="' + e.target.result + '" class="img-thumbnail">');
                $($('#addReview #preview').parent()).show();
            }
            reader.readAsDataURL(input.files[0]);
        }  
    });

    // Listen to submit.
    $('#addReview #submit').on('click', function() {

        // Disable submit button.
        $(this).button('loading');

        // Clear messages & errors.
        $('#addReview #messages').html('');
        $('#addReview form').salsa('clearErrors');

        // Validate mandatory parameters.
        var rating = parseInt($('#addReview #rating').val()); 
        var comment = $('#addReview #comment').val();
        if(rating == '' || isNaN(rating) || comment == '') {
            var html = '<div class="alert alert-warning">';
            html += '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>';
            html += gettext('Please provide a rating and a comment');
            html += '</div>';
            $('#addReview #messages').prepend(html);
            $(this).button('reset');
            return;
        }

        // Submit review, according to whether a photo was provided or not.
        var file = $('#addReview input').get(0).files[0];
        if(file == undefined) {
            submitReview(rating, comment);
        } else {
            submitReviewWithPhoto(rating, comment, file);
        }
    });

    function submitReview(rating, comment) {
        $.ajax({
            url: reviews_api_url,
            type: 'POST',
            data: JSON.stringify({ rating: rating, comment: comment }),
            dataType: 'JSON',
            success: function(data, status, xhr) {
                processResponse(data, status, xhr);
            },
            error: function(xhr, status, err) {
                $('#addReview form').salsa('processResponse', xhr.status, xhr.responseText);
                $('#addReview #submit').button('reset');
            }
        });
    }

    function submitReviewWithPhoto(rating, comment, file) {
        // Build formdata.
        var formData = new FormData($('#addReview form').get(0));
        formData.append('rating', rating);
        formData.append('comment', comment);
        formData.append('file', file);

        // Submit.
        $.ajax({
            url: reviews_api_url,
            type: 'POST',
            data: formData,
            // Options to tell JQuery not to process data or worry about content-type.
            cache: false,
            contentType: false,
            processData: false,
            success: function(data, status, xhr) {
                processResponse(data, status, xhr);
            },
            error: function(xhr, status, err) {
                $('#addReview form').salsa('processResponse', xhr.status, xhr.responseText);
                $('#addReview #submit').button('reset');
            }
        });
    }

    function processResponse(data, status, xhr) {
        // Message.
        alert(gettext('Thank you for your review'));

        // Render comment.
        var html = '<li><div class="avatar">';
        html += '<img src="' + data.user.photo_url + '" class="img-rounded"></div>';
        html += '<div class="comment"><div class="star-rating-sm"><div style="width:' + (data.rating*100/5) + '%"></div></div>';
        html += '<div class="message">' + data.comment + '<br>';
        if(data.photo) {
            html += '<img src="' + data.photo.image_url + '" style="width: 50%; margin: 10px 0 10px 0;" class="img-thumbnail">';
            html += '<br>';
        }
        html += '<span>' + data.user.name + ' // ' + data.date + '</span></div></div>';
        html += '<div class="clear"></div></li>';
        $('.place .left-container .reviews ul').prepend(html);
        $('.place .left-container .reviews ul').show();

        // Update Place's average rating.
        var placeAverageRating = data.place.rating.average*100/5;
        $('.place .rating .star-rating div').css('width', placeAverageRating+'%');

        // Close modal.
        $('#addReview').modal('hide');

        // Re-enable submit button.
        $('#addReview #submit').button('reset');
    }
}
/*
 * Initialize Add Photo Modal.
 */
function initializePhotoModal() {

    // Initialize form validator.
    $('#addPhoto form').salsa();

    // Listen to file selection.
    $('#addPhoto input').on('change', function() {
        var input = this;
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#addPhoto #preview').html('<img src="' + e.target.result + '" class="img-thumbnail">');
                $($('#addPhoto #preview').parent()).show();
            }
            reader.readAsDataURL(input.files[0]);
        }  
    });

    //Listen to click on upload button.
    $('#addPhoto #submit').on('click', function() {

        // Validate form.
        if(!$('#addPhoto form').salsa('validate')) { return; }

        // Disable submit button.
        $(this).button('loading');
        
        // Build formdata.
        var formData = new FormData($('#addPhoto form').get(0));
        formData.append('file', $('#addPhoto input').get(0).files[0]);

        // Upload picture.
        $.ajax({
            url: photos_api_url,
            type: 'POST',
            data: formData,
            // Options to tell JQuery not to process data or worry about content-type.
            cache: false,
            contentType: false,
            processData: false,
            success: function(data, status, xhr) {
                alert(gettext('Picture uploaded'));
                $(this).button('reset');
                window.location = request_path;
            }.bind(this),
            error: function(xhr, status, err) {
                $('#addPhoto form').salsa('processResponse', xhr.status, xhr.responseText);
                $(this).button('reset');
            }.bind(this)
        });
    });
}

/*
 * Deletes photo with given ID.
 */
function deletePhoto(el, id) {
    if(confirm('DELETE: Are you sure?')) {
        $(el).attr('disabled', true);
        $.ajax({
            url: photos_api_url + '/' + id,
            type: 'DELETE',
            success: function(data, status, xhr) {
                alert(gettext('Picture deleted'));
                $(this).attr('disabled', false);
                window.location.reload();
            }.bind(el),
            error: function(xhr, status, err) {
                alert(gettext('Error deleting photo'));
                $(this).attr('disabled', false);
            }.bind(el)
        });
    }
}
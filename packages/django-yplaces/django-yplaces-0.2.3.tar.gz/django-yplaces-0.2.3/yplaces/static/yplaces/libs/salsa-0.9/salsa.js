(function($) {

    // Settings.
    var defaults = {
        inputs: ['input', 'select', 'textarea']
    };
    var settings;

    /*
     * Methods available.
     */ 
    var methods = {


        /*
         * Constructor.
         */
        init : function(options){

            var that = this;

            // We can use the extend method to merge options/settings as usual:
            // But with the added first parameter of TRUE to signify a DEEP COPY:
            settings = $.extend(true, {}, defaults, options);

            // Debug stuff.
            if(settings.debug == true) { console.log('Salsa Form Validation Loaded'); }

            // Add error messages container to all form controls.
            var errContainerHtml = '<ul class="salsa-error-list" style="display: block;"></ul>';
            for(var i=0; i<settings.inputs.length; i++) {
                $.each(this.find(settings.inputs[i]), function(key, value) {
                    // Check if either the entire form is to be validated or this specific element.
                    if($(that).attr('data-validate') == 'salsa' || $(value).attr('data-validate') == 'salsa') {
                        $(value).parent().append(errContainerHtml);
                    }
                });
            }

            // Return.
            return this;
        },


        /*
         * Validate form.
         */
        validate: function() {
            
            // Debug stuff.
            if(settings.debug == true) { console.log('[Salsa] Validate'); }

            // Clear any error messages.
            methods.clearErrors.apply(this);

            // Flags that no errors were found.
            var isValid = true;

            //
            // Perform validations coded in the form's HTML.
            //
            for(var i=0; i<settings.inputs.length; i++) {
                
                // For each of the controls being 'watched'.                
                $.each(this.find(settings.inputs[i]), function(key, value) {
                
                    var el = $(value);
                    
                    // If required, check if value provided.
                    if(el.attr('data-required') == 'true') {
                        if(el.val() == '') {
                            if(settings.debug == true) { console.log('[Salsa] Validation Error! ID: ' + $(value).attr('id')); }
                            isValid = false;
                            el.addClass('salsa-error');
                            el.parent().find('ul[class="salsa-error-list"]').prepend('<li class="required" style="display: list-item;">This value is required.</li>');
                        }
                    }

                });
            }

            // Return whether form is valid or not.
            return isValid;
        },


        /*
         * Parse server error (bad request).
         */
        processResponse: function() {

            // Clear any error messages.
            methods.clearErrors.apply(this);
            
            // Response text is required, should be passed as argument.
            if(arguments.length != 2) {
                this.find('#messages').prepend('<div class="alert alert-danger">Client error.</div>')
                return;
            }

            // Fetch arguments.
            var status = arguments[0];
            var responseText = arguments[1];

            // Parse JSON response.
            try {
                var response = JSON.parse(responseText);
            } catch(err) {
                this.find('#messages').prepend('<div class="alert alert-danger">Response error.</div>')
                return;
            }

            // If 'Bad Request', then check if information regarding what is wrong with the parameters is provided.
            if(status == 400 && response.parameters) {

                // Check for a message for "all".
                if(response.parameters.__all__) {
                    var messages = response.parameters.__all__;
                    for(var i=0; i<messages.length; i++) {
                        var errorMessage = '<div class="alert alert-danger">' + messages[i] + '</div>';
                        this.find('#messages').prepend(errorMessage);
                    }
                }

                // Process each parameter's message.
                for(param in response.parameters) {
                    $.each(this.find('#' + param), function(key, value) {
                        var el = $(value);
                        var messages = response.parameters[param];
                        el.addClass('salsa-error');
                        for(var i=0; i<messages.length; i++) {
                            el.parent().find('ul[class="salsa-error-list"]').prepend('<li class="required" style="display: list-item;">' + messages[i] + '</li>');
                        }
                    });
                }    
            }

            // If no details on why the request failed, then show generic message (either provided by server or default one).
            else {
                var errorMessage = '<div class="alert alert-danger">' + ((response.message) ? response.message : 'Bad request.') + '</div>';
                this.find('#messages').prepend(errorMessage);
            }
        },


        /*
         * Clear errors.
         */
        clearErrors: function() {
            if(settings.debug == true) { console.log('[Salsa] Clearing errors'); }

            // Messages.
            this.find('#messages').empty();

            // Form controls.
            for(var i=0; i<settings.inputs.length; i++) {
                $.each(this.find(settings.inputs[i]), function(key, value) {
                    var el = $(value);
                    el.removeClass('salsa-error');
                    el.parent().find('ul[class="salsa-error-list"]').empty();
                });
            }
        }
    };

    /*
     * Attach the plugin to jQuery's namespace.
     */
    $.fn.salsa = function(method) {

        // Check if method invoked exists.
        if(methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        }

        // If method is an hash, then we assume the constructor is being called.
        else if(typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        }

        // Invalid method.
        else {
            $.error('Method ' +  method + ' does not exist on jQuery.salsa');
        }
    };

}(jQuery));
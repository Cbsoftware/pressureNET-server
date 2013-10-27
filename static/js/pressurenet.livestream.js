(function () {

    var global = this;

    var PressureNET = (global.PressureNET || (global.PressureNET = {}));

    PressureNET.livestream = function (showErrors) {
        var success = window.location.search;
        if ( success == '?success=1' ) {
            $( '#signup-form' ).hide();
            $( '#success' ).fadeIn( 'slow' );
        }

        if (showErrors) {
            $( '.error-log, .error-label' ).show();
        }

        $( '#legal-title a' ).click(function(e) {
            $( '#legal-notes' ).slideToggle( 'fast' );
            e.preventDefault();
        });

        function showDescription() {
            var selected = $('input[type="radio"]:checked');
            selected.each(function () {
                var description = $(this).data('desc');
                $(this).parent().parent().find('.descriptions p').text(description);
            });
        };

        showDescription();

        $( '.choices input[type="radio"]' ).click(function() {
            showDescription();
            showPlans();
        });


    };
}).call(this);

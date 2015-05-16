define(['jquery'],
    function($) {
        var Keyboard = {
            // event.type must be keypress
            getChar: function(event) {
                if (event.which == null) {
                  return String.fromCharCode(event.keyCode); // IE
                } else if (event.which!=0 && event.charCode!=0) {
                  return String.fromCharCode(event.which);   // the rest
                } else {
                  return null; // special key
                }
            }

        };

        return Keyboard;
    }
);
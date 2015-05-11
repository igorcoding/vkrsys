define(['jquery'],
    function($) {
        var Util = {
            inverseObject: function(obj) {
                var invertedObj = {};
                for (var k in obj) {
                    if (obj.hasOwnProperty(k)) {
                        var v = obj[k];
                        invertedObj[v] = k;
                    }
                }
                return invertedObj;
            }

        };

        return Util;
    }
);
/* global angular:false */
'use strict';

angular.module('polaris.services')
  .factory('cache', function() {
    var cache = {};
    var temp = {
      set: function(key, value) {
        cache[key] = value;
      },
      get: function(key) {
        return cache[key];
      },
      keys: function() {
        return Object.keys(cache);
      }
    };

    return {
      temp: temp,
    };
  });

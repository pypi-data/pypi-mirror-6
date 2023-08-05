/* global angular:false */
'use strict';

angular.module('polaris.directives', []);
angular.module('polaris.services', []);
angular.module('polaris.controllers', []);
angular.module('polaris', [
  'polaris.utils',
  'polaris.services',
  'polaris.directives',
  'polaris.controllers',
])
.run(function($http) {
  var csrfToken = $('meta[name=csrf-token]').attr('content');
  $http.defaults.headers.common["X-CSRF-Token"] = csrfToken;
  $http.defaults.headers.post["X-CSRF-Token"] = csrfToken;
  $http.defaults.headers.put["X-CSRF-Token"] = csrfToken;
});

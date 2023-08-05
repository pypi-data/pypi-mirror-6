/* global angular:false */
'use strict';

angular.module('polaris.directives')
  .directive('flatSwitch', function() {
    function link(scope, element, attrs) {
      element.bootstrapSwitch();

      scope.$watch('public', function() {
        element.bootstrapSwitch('setState', scope.public);
      });

      if (attrs.flatSwitch === 'on') {
        scope.public = true;
      } else {
        scope.public = false;
      }
      element.on('switch-change', function(e, data) {
        if (data.value === scope.public) {
          return;
        }
        scope.$apply(function () {
          scope.public = data.value;
        });
      });
    }

    return {
      restrict: 'A',
      link: link
    };
  });

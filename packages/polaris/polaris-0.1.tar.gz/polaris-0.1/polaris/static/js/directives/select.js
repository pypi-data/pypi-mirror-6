/* global angular:false */
'use strict';

angular.module('polaris.directives')
  .directive('flatSelect', function() {
    function link(scope, element) {
      element.selectpicker({
        style: 'btn-info',
        menuStyle: 'dropdown-inverse'
      });

      scope.source = element.val();
    }

    return {
      restrict: 'A',
      link: link
    };
  });

/* global angular:false */
'use strict';

angular.module('polaris.directives')
  .directive('validJson', function(utils) {
    function link(scope, el, attrs, ctrl) {
      el.on('blur', function() {
        scope.$apply(function() {
          ctrl.$setValidity('validJson', utils.validateJson(scope.json));
        });
      });

      el.on('focus', function() {
        scope.$apply(function() {
          ctrl.$setValidity('validJson', true);
        });
      });
    }

    return {
      require: 'ngModel',
      link: link,
    };
  })
  .directive('validName', function() {
    function link(scope, el, attrs, ctrl) {
      el.on('blur', function() {
        scope.$apply(function() {
          ctrl.$setValidity('validName', scope.name);
        });
      });

      el.on('focus', function() {
        scope.$apply(function() {
          ctrl.$setValidity('validName', true);
        });
      });
    }

    return {
      require: 'ngModel',
      link: link,
    };
  });

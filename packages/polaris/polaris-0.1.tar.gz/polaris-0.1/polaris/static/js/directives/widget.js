/* global angular:false */
'use strict';

angular.module('polaris.directives')
  .directive('addToGridster', function() {
    function link(scope, element, attrs, gridsterCtrl) {
      var chart = scope.chart;
      gridsterCtrl.add(element, {row: chart.row, col: chart.col}, chart.x, chart.y);

      scope.$on('parser-created', function(evt, parser) {
        element.data('parser', parser);
      });

      scope.hideEditable = true;
      element.hover(function() {
        scope.$apply(function() {
          scope.hideEditable = false;
        });
      }, function() {
        scope.$apply(function() {
          scope.hideEditable = true;
        });
      });

      element.bind('$destroy', function() {
        gridsterCtrl.remove(element);
      });

      element.data('chart', chart);
    }
    return {
      require: '^gridster',
      link: link,
    };
  });

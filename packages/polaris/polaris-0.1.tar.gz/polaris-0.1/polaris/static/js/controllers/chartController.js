/* global angular:false */
'use strict';

angular.module('polaris.controllers')
  .controller('ChartCtrl', function($scope, $http, $window) {
    $scope.items = [{
      name: 'table',
      icon: 'fa fa-table',
    }, {
      name: 'scatter',
      icon: 'fa fa-ellipsis-h',
    }, {
      name: 'line',
      icon: 'fa fa-minus',
    }, {
      name: 'area',
      icon: 'fa fa-picture-o',
    }, {
      name: 'bar',
      icon: 'fa fa-bar-chart-o',
    }, {
      name: 'pie',
      icon: 'fa fa-adjust',
    }, {
      name: 'word',
      icon: 'fa fa-font',
    }];

    $scope.type = $window.location.hash.substring(1) || 'table';
    $scope.baseUrl = ($scope.type === 'table') ? '/api/data' : '/api/vega';
    if ($scope.currentChart) {
      $scope.type = $scope.currentChart.type;
      $scope.baseUrl = $scope.currentChart.baseUrl;
      $scope.currentChart = null;
    }
    for (var i = 0; i < $scope.items.length; ++i) {
      if ($scope.items[i].name === $scope.type) {
        $scope.items[i].active = 'active';
      }
    }

    $scope.changeChart = function($event) {
      if (!$scope.parser) {
        return;
      }
      var el = $($event.target),
          type = el.attr('href').substring(1);

      el.parent().find('.active').removeClass('active');
      el.addClass('active');

      $scope.baseUrl = (type === 'table') ? '/api/data' : '/api/vega';
      $scope.type = type;

      $scope.chartScope.baseUrl = $scope.baseUrl;
      $scope.chartScope.type = $scope.type;
    };
  });

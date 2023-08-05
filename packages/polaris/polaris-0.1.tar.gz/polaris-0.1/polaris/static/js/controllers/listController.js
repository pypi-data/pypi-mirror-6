/* global angular:false */
'use strict';

function listLib(name, $scope, $http) {
  $scope.selected = 'All';
  $http.get('/api/' + name)
    .success(function(data) {
      $scope.items = data[name];
    });
}

angular.module('polaris.controllers')
  .controller('ChartListCtrl', function($scope, $http) {
    listLib('charts', $scope, $http);
  })
  .controller('DashboardListCtrl', function($scope, $http) {
    listLib('dashboards', $scope, $http);
  });

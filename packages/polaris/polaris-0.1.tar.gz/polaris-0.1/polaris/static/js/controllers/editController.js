/* global angular:false */
'use strict';

angular.module('polaris.controllers')
  .controller('EditCtrl', function($scope, $http, $window, utils) {
    var jsonValues = $('#json-value').text().trim();

    if (jsonValues) {
      $scope.json = JSON.stringify(JSON.parse(jsonValues), null, 4);
    }

    $scope.actionType = null;

    $scope.submit = function() {
      if ($scope.actionType === 'delete') {
        $http.delete('/api/' + $scope.page + '/' + $scope.uuid)
          .success(function() {
            $window.open('/' + $scope.page, '_self');
          });
      }

      if (!utils.validateJson($scope.json) || !$scope.name) {
        return;
      }

      var url,
          method,
          data;

      data = {
        'name': $scope.name,
        'slug': $scope.slug,
        'is_public': $scope.public,
      };

      if ($scope.page === 'chart') {
        data.source = $scope.source;
        data.options = JSON.parse($scope.json);
      } else {
        data.description = JSON.parse($scope.json);
      }

      if ($scope.type === 'update') {
        url = '/api/' + $scope.page + '/' + $scope.uuid;
        method = 'PUT';
      } else {
        url = '/api/' + $scope.page + 's';
        method = 'POST';
      }

      $http({method: method, url: url, data: data})
        .success(function(response) {
          $window.open('/' + $scope.page + '/' + response[$scope.page].id, '_self');
        });
    };
  });

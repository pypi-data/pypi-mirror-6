/* global angular:false */
'use strict';

angular.module('polaris.controllers')
  .controller('IndexCtrl', function($scope) {
    function showSign(type) {
      $scope.hideSocialSign = (type === 'email');
      $scope.hideEmailSign = !$scope.hideSocialSign;
    }

    var sign1 = 'social',
        sign2 = 'social';

    $scope.sign = ['email', 'email'];

    showSign(sign1);

    $scope.logIn = function() {
      $scope.sign[0] = sign1;
      if (sign1 === 'email' && $scope.sign[1] === 'social') {
        $scope.sign[1] = 'email';
        sign2 = 'social';
      }
      sign1 = (sign1 === 'social') ? 'email' : 'social';
      $scope.signMsg = 'Log in';
      showSign(sign1);
    };

    $scope.signUp = function() {
      $scope.sign[1] = sign2;
      if (sign2 === 'email' && $scope.sign[0] === 'social') {
        $scope.sign[0] = 'email';
        sign1 = 'social';
      }
      sign2 = (sign2 === 'social') ? 'email' : 'social';
      $scope.signMsg = 'Sign up';
      showSign(sign2);
    };

    $scope.submit = function($event) {
      if ($scope.signMsg === 'Log in') {
        $scope.url = '/login/';
      } else {
        $scope.url = '/signup/';
      }
      $event.target.submit();
    };
  });

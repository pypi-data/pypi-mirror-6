/* global angular:false */
'use strict';

angular.module('polaris.controllers')
  .controller('DashboardCtrl', function($scope, $compile, $templateCache, $window,
                                        $document, $http, boxSize, utils) {
    boxSize.setUp({
      baseDimention: [150, 150]
    });

    var uuid = $('#uuid').data('uuid');

    $http.get('/api/dashboard/' + uuid)
      .success(function(data) {
        var dashboard = data.dashboard,
            description = dashboard.description;

        $scope.dashboard = dashboard;
        $scope.dashboardName = dashboard.name;
        $scope.crossfilter = description.crossfilter;
        if ('charts' in description) {
          $scope.charts = description.charts;
        } else {
          $scope.charts = [];
          $scope.$emit('dashboard-updated');
        }

        $scope.$broadcast('dashboard-data-loaded', description.crossfilter);
      });

    $scope.$on('dashboard-updated', function() {
      var desc = {
        charts: $scope.charts
      };
      if ($scope.crossfilter) {
        desc.crossfilter = $scope.crossfilter;
      }
      $http.put('/api/dashboard/' + uuid, {
        description: desc,
        slug: $scope.dashboard.slug,
        is_public: $scope.dashboard.is_public,
        name: $scope.dashboard.name
      }, {
        'content-type': 'application/json'
      }).success(function(res) {
        console.log(res);
      });
    });

    $scope.getClass = function(idx) {
      var className = 'chart';

      className += ' col-md-' + $scope.charts[idx].sizex;
      return className;
    };

    $scope.showAddButton = function(ok) {
      $scope.hideAdd = !(ok);
      $scope.hideUpdate = !!(ok);
    };

    $scope.addChart = function() {
      delete $scope.currentChart;
      $scope.cfColumn = '';

      $('.chart-pane > .pane-container').empty();
      $('.chart-list').show();
      $('.chart-pane').hide();

      $('#chart-add').modal('show');
    };

    $scope.deleteChart = function(evt, idx) {
      $scope.charts.splice(idx, 1);
      $scope.$emit('dashboard-updated');
    };

    $scope.saveChart = function(chartId, chartType, baseUrl) {
      var pos = $scope.grid.nextPosition(6, 2),
          top = $('.charts')[0].getBoundingClientRect().top,
          data;

      if (!pos) {
        pos = {col: 1, row: 1};
      }
      data = {
        baseUrl: baseUrl,
        x: 6,
        y: 2,
        col: pos.col,
        row: pos.row,
        type: chartType,
        id: chartId
      };
      if ($scope.cfColumn) {
        data.cf_column = $scope.cfColumn;
      }

      $scope.charts.push(data);

      $scope.$emit('dashboard-updated');

      $('.chart-list').show();
      $('.chart-pane').hide();
      $('#chart-add').modal('hide');

      $('body,html').animate({
        scrollTop: top + (pos.row - 1) * $scope.grid.minHeight
      });
    };

    $scope.showChart = function($event, id, isAdd, chartFilter) {
      $event.preventDefault();
      $scope.showAddButton(isAdd);

      var chartWidget = $templateCache.get('chart_widget.html');

      $scope.chartId = id;
      if (arguments.length <= 3) {
        $scope.chartFilter = null;
      } else {
        $scope.chartFilter = chartFilter;
      }

      $('.chart-list').hide();
      $('.chart-pane').show();

      $('.chart-pane > .pane-container').html(chartWidget);
      $compile($('.chart-pane').contents())($scope);
    };

    $scope.viewChart = function($event, chart, idx) {
      var filter = null;

      $scope.showAddButton(false);

      $('.chart-pane > .pane-container').empty();
      $('#chart-add').modal('show');
      $('#chart-add').css('display', 'block');

      $scope.currentChart = chart;
      $scope.currentIndex = idx;

      $scope.cfColumn = chart.cf_column;

      if ($scope.brushFrom) {
        filter = [$scope.brushFrom, $scope.brushTo];
      }

      $scope.showChart($event, chart.id, false, filter);
    };

    $scope.updateChart = function(uuid, type, baseUrl) {
      $scope.charts[$scope.currentIndex].type = type;
      $scope.charts[$scope.currentIndex].baseUrl = baseUrl;
      $scope.charts[$scope.currentIndex].cf_column = $scope.cfColumn;

      $scope.$emit('dashboard-updated');

      $('.chart-list').show();
      $('.chart-pane').hide();
      $('#chart-add').modal('hide');
      $('#chart-add').css('display', 'none');

      $scope.cfColumn = '';
      delete $scope.currentChart;
    };
  });

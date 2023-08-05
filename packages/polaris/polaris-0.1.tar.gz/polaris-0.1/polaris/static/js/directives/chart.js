/* global angular:false, URI:false */
'use strict';

angular.module('polaris.directives')
  .directive('chart', function($http, vegaService, tooltipService, utils, cache) {
    var uri = URI(document.URL);

    function link(scope, el, attrs) {

      function cfCondition(dateRange) {
        return scope.cf + '|' + utils.format(dateRange[0]) +
          '|' + utils.format(dateRange[1]);
      }

      var pScope = scope.parentScope();

      if (pScope) {
        pScope.uuid = attrs.uuid;
      }

      function loadData(url) {
        scope.hideLoading = false;

        return $http.get(url);
      }

      function successHandler(data) {
        var key = scope.type + ':' + attrs.uuid,
            box,
            parser;

        scope.name = data.name;
        scope.hideLoading = true;

        if (!('parser' in scope)) {
          box = utils.offset(el);
          scope.parser = new vegaService.Parser(el);
          scope.parser.height = box.height - 32;
          scope.parser.width = box.width;
          scope.parser.tooltip = new tooltipService.Tooltip(scope.parser);
          if (pScope) {
            pScope.parser = scope.parser;
            pScope.chartScope = scope;
          }

          scope.$emit('parser-created', scope.parser);
        }

        if (scope.type === 'table') {
          scope.parser.tableData = data;

          scope.isTable(false);

          scope.parser.renderTable(scope);
        } else if (!scope.parser.inited) {
          scope.isTable(true);

          parser = scope.parser;
          parser.init(data);
          parser.parse();

        } else {
          scope.parser.update(data);
        }
        cache.temp.set(key, angular.copy(data));
      }

      scope.request = function(url) {
        var key = scope.type + ':' + attrs.uuid,
            data = cache.temp.get(key);
        if (data && !uri.hasSearch('cf')) {
          successHandler(data);
        } else {
          loadData(url).success(successHandler);
        }
      };

      scope.isTable = function(hide) {
        scope.hideTable = !!(hide);
        scope.hideCanvas = !(hide);
      };

      scope.isTable(false);
      scope.hideLoading = false;

      if (scope.filter && scope.cf) {
        uri.setSearch('cf', cfCondition(scope.filter));
      }

      scope.$watchCollection('[type, baseUrl, brushFrom, brushTo]', function() {
        if (scope.cf && scope.brushFrom && scope.brushTo) {
          uri.setSearch('cf', cfCondition([scope.brushFrom, scope.brushTo]));
        }
        if (scope.type && scope.baseUrl) {
          var url = scope.baseUrl + '/' + scope.type + '/' + attrs.uuid + uri.search();
          scope.request(url);
        }
      });
    }

    return {
      restrict: 'E',
      templateUrl: 'chart.html',
      replace: true,
      scope: {
        brush: '=',
        brushFrom: '=',
        brushTo: '=',
        filter: '=',
        parentScope: '&',
        type: '@',
        cf: '@',
        baseUrl: '@',
      },
      link: link
    };
  });

/* global angular:false */
'use strict';

angular.module('polaris.directives', []);
angular.module('polaris.services', []);
angular.module('polaris.controllers', []);
angular.module('polaris', [
  'polaris.utils',
  'polaris.services',
  'polaris.directives',
  'polaris.controllers',
])
.run(function($http) {
  var csrfToken = $('meta[name=csrf-token]').attr('content');
  $http.defaults.headers.common["X-CSRF-Token"] = csrfToken;
  $http.defaults.headers.post["X-CSRF-Token"] = csrfToken;
  $http.defaults.headers.put["X-CSRF-Token"] = csrfToken;
});
/* global angular:false, d3:false */
'use strict';

angular.module('polaris.utils', [])
  .factory('utils', function() {
    function formatDate(date) {
      var format = d3.time.format('%Y-%m-%d');

      return angular.isDate(date) ? format(date) :
        angular.isNumber(date) ? format(new Date(date)) : date;
    }

    function offset(elm) {
      var rawDom = elm[0],
          x = 0,
          y = 0,
          body = document.documentElement || document.body,
          scrollX = window.pageXOffset || body.scrollLeft,
          scrollY = window.pageYOffset || body.scrollTop,
          dimension = rawDom.getBoundingClientRect();


      x = dimension.left + scrollX;
      y = dimension.top + scrollY;
      return {left: x, top: y, width: dimension.width, height: dimension.height};
    }

    function cmp(a, b) {
      if (a.idx > b.idx) {
        return 1;
      } else if (a.idx < b.idx) {
        return -1;
      } else {
        if (a.col > b.col) {
          return 1;
        } else if (a.col < b.col) {
          return -1;
        } else {
          return 0;
        }
      }
    }

    function formatTable(data) {
      var columns = Object.keys(data.table[0]),
          chartData = [],
          idx,
          index;

      idx  = columns.indexOf('idx');
      if (idx !== -1 && idx !== 0) {
        columns.splice(idx, 1);
        columns.unshift('idx');
      }
      index  = columns.indexOf('index');
      if (index !== -1 && index !== 0) {
        columns.splice(index, 1);
        columns.unshift('index');
      }
      angular.forEach(data.table, function(v) {
        var col = [];
        angular.forEach(columns, function(c) {
          col.push(v[c]);
        });
        chartData.push(col);
      });

      return {
        chartData: chartData,
        columns: columns
      };
    }

    function validateJson(data) {
      var valid = false;
      try {
        JSON.parse(data);
        valid = true;
      } catch (e) {
        valid = false;
      }

      return valid;
    }

    return {
      format: formatDate,
      cmp: cmp,
      offset: offset,
      formatTable: formatTable,
      validateJson: validateJson,
    };
  });
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
/* global angular:false, d3:false */
'use strict';

angular.module('polaris.directives')
  .directive('crossfilter', function($http, utils) {
    function link(scope, el) {
      scope.hideLoading = false;
      scope.$on('dashboard-data-loaded', function(evt, crossfilter) {
        if (!crossfilter) {
          el.parent().hide();
          return;
        }
        var cf = new Crossfilter(crossfilter);
        cf.create();
      });

      function Crossfilter(opts) {
        this.id = opts.id;
        this.height = 30;
        this.width = utils.offset(el.parent()).width - 38;
        this.lock = ('lock' in opts) ? opts.lock : false;
      }

      Crossfilter.prototype.setValueLabel = function(start, end) {
        scope.startValueLabel = start.toDateString();
        scope.endValueLabel = end.toDateString();
        scope.labelTop = this.height + 8;
        scope.startLabelLeft = this.x(start);
        scope.endLabelLeft = this.x(end);
      };

      Crossfilter.prototype.setRange = function(data) {
        this.to = d3.max(data, function(d){ return new Date(d['']); });
        this.from = d3.min(data, function(d){ return new Date(d['']); });

        this.end = new Date(this.to);
        this.start = new Date(this.to);
        this.start = new Date(this.start.setDate(this.end.getDate() - 30));
      };

      Crossfilter.prototype.init = function() {
        var timeRange = [new Date(this.from), new Date(this.to)],
            padding = {left: 0, right: 0, top: 0, bottom: 0},
            width = this.width,
            height = this.height,
            _this = this;

        this.x = d3.time.scale()
          .domain(timeRange)
          .range([0, width]);

        this.y = d3.scale.linear()
          .range([height, 0]);

        this.brush = d3.svg.brush().x(this.x);
        this.brush.on('brushend', function(){
          scope.$apply(function() {
            var extent;
            extent = _this.brush.extent();
            scope.brushFrom = extent[0];
            scope.brushTo = extent[1];
          });
        });

        this.svg = d3.select(el[0].querySelector('.filter-brush'))
          .append('svg')
          .attr('height', height + 24)
          .attr('width', width)
          .append('g')
          .attr('transform', 'translate(' + padding.left +
                ',' + padding.top + ')');

        this.svg.append('rect')
          .attr('class', 'crossfilter-background')
          .attr('width', width)
          .attr('height', height);

        this.svg.append('g')
          .attr('class', 'x axis')
          .attr('transform', 'translate(0,' + height + ')')
          .call(d3.svg.axis()
               .scale(this.x)
               .orient('bottom')
               .ticks(5)
               .tickPadding(7))
          .selectAll('text')
          .attr('x', 6)
          .style('text-anchor', 'middle');
      };

      Crossfilter.prototype.create = function() {
        var _this = this;

        $http.get('/api/data/csv/' + this.id)
          .success(function(data) {
            scope.hideLoading = true;

            var csv = d3.csv.parse(data),
                gBrush,
                barWidth,
                range,
                bar,
                col,
                keys,
                i;

            keys = Object.keys(csv[0]);
            for (i = 0; i < keys.length; ++i) {
              if (keys[i] !== '') {
                col = keys[i];
                break;
              }
            }

            _this.setRange(csv);
            _this.init();

            _this.y.domain([d3.min(csv, function(d){ return Number(d[col]); }),
                            d3.max(csv, function(d){ return Number(d[col]); })]);
            barWidth = _this.width / csv.length;

            function round(date) {
              return _this.x.invert(Math.round(_this.x(date) / barWidth) * barWidth);
            }

            if (!_this.lock) {
              _this.setValueLabel(round(_this.start), round(_this.end));
              el.find('.value-label').show();
            }

            _this.brush.extent([round(_this.start), round(_this.end)]);
            _this.brush.on('brush', function() {
              var ext0 = _this.brush.extent(),
                  ext1;

              ext1 = ext0.map(round);

              d3.select(this).call(_this.brush.extent(ext1));

              scope.$apply(function() {
                var extent = _this.brush.extent();
                _this.setValueLabel(extent[0], extent[1]);
              });
            });

            bar = _this.svg.append('g').selectAll('g')
              .data(csv)
              .enter().append('g')
              .attr('class', 'brush-rect')
              .attr('transform', function(d, i) {return  'translate(' + i * barWidth + ',0)'; });

            bar.append('rect')
              .attr('y', function(d) {return _this.y(Number(d[col])); })
              .attr('height', function(d) {return _this.height - _this.y(Number(d[col])); })
              .attr('width', barWidth - 1);

            if (!_this.lock) {
              gBrush = _this.svg.append('g')
                .attr('class', 'brush')
                .call(_this.brush);
              gBrush.selectAll('rect').attr('height', _this.height);
              range = _this.brush.extent();
              scope.brush = _this.brush;
              scope.brushFrom = range[0];
              // auto add 1 more day to brushTo
              scope.brushTo = range[1].setDate(range[1].getDate() + 1);
            } else {
              scope.brush = null;
              scope.brushFrom = new Date(_this.from);
              scope.brushTo = new Date(_this.to);
            }
          });
      };
    }

    return {
      restrict: 'E',
      replace: true,
      templateUrl: 'crossfilter.html',
      link: link
    };
  });
/* global angular:false */
'use strict';

if (jQuery && $.Gridster) {
  $.Gridster.add_widget = function(html, size_x, size_y, col, row, max_size) {
    var pos;
    size_x || (size_x = 1);
    size_y || (size_y = 1);

    if (!col & !row) {
      pos = this.next_position(size_x, size_y);
    }else{
      pos = {
        col: col,
        row: row
      };

      this.empty_cells(col, row, size_x, size_y);
    }

    var $w = $(html).attr({
      'data-col': pos.col,
      'data-row': pos.row,
      'data-sizex' : size_x,
      'data-sizey' : size_y
    }).addClass('gs-w').hide();

    this.$widgets = this.$widgets.add($w);

    this.register_widget($w);

    this.add_faux_rows(pos.size_y);

    if (max_size) {
      this.set_widget_max_size($w, max_size);
    }

    this.set_dom_grid_height();

    return $w.fadeIn();
  };
}

angular.module('polaris.directives')
  .directive('gridster', function() {
    var gap = 20,
        minHeight,
        gridster,
        minWidth;

    minWidth = Math.floor($('.col12').width() / 12);
    minHeight = 150;

    function resizeHolder($widget) {
      var holder = $('.preview-holder'),
          width = Number($widget[0].dataset.sizex) * minWidth,
          height = Number($widget[0].dataset.sizey) * minHeight;
      holder.css('height', height - 20)
        .css('width', width - 20);
    }

    function onLayoutChange() {
      var layouts = gridster.serialize_changed(),
          changed = false;

      angular.forEach(layouts, function(layout) {
        var chart = layout.chart;
        chart.col = layout.col;
        chart.row = layout.row;

        changed = true;
      });

      return changed;
    }

    function controller($scope, $element) {
      var options;

      options = {
        widget_margins: [0, 0],
        widget_base_dimensions: [minWidth, 150],
        serialize_params: function($w, wgd) {
          var extra = {chart: $w.data('chart')};
          return $.extend(extra, wgd);
        },
        draggable: {
          start: function() {
            var holder = $('.preview-holder'),
                width = parseInt(holder.css('width')),
                height = parseInt(holder.css('height'));
            holder.css('height', height - 20)
              .css('width', width - 20);
          },
          stop: function() {
            var changed = onLayoutChange();
            if (changed) {
              $scope.$emit('dashboard-updated');
            }
          }
        },
        resize: {
          enabled: true,
          handle_append_to: '.resizer',
          start: function(evt, ui, $widget) {
            $widget.data('parser').hide();
            resizeHolder($widget);
          },
          resize: function(evt, ui, $widget) {
            resizeHolder($widget);
          },
          stop: function(evt, ui, $widget) {
            var chart = $widget.data('chart'),
                extra = 58,
                sizex = Number($widget[0].dataset.sizex),
                sizey = Number($widget[0].dataset.sizey);

            $widget.data('parser')
              .resize({width: sizex * minWidth - extra, height: sizey * minHeight - extra - 32})
              .show();

            chart.x = sizex;
            chart.y = sizey;

            onLayoutChange();

            $scope.$emit('dashboard-updated');
          }
        }
      };

      return {
        minWidth: minWidth,
        minHeight: minHeight,
        gap: gap,
        init: function() {
          var ul = $element.find('#for-gridster');
          gridster = ul.gridster(options).data('gridster');
          $scope.grid = {
            minHeight: minHeight,
            nextPosition: function(x, y) {
              return gridster.next_position(x, y);
            }
          };
        },
        add: function(el, pos, sizeX, sizeY) {
          gridster.add_widget(el, sizeX, sizeY, pos.col, pos.row);
        },
        remove: function(el) {
          gridster.remove_widget(el, function() {
            if (onLayoutChange()) {
              $scope.$emit('dashboard-updated');
            }
          });
        }
      };
    }

    return {
      restrict: 'E',
      transclude: true,
      replace: true,
      template: '<div class="gridster"><div ng-transclude></div></div>',
      controller: controller,
      link: function(scope, el, attrs, controller) {
        controller.init();
      }
    };
  });
/* global angular:false */
'use strict';

angular.module('polaris.directives')
  .directive('resizer', function($document, utils){
    function link(scope, el) {
      var resizer = angular.element($document[0].createElement('div')),
          startX = 0,
          startY = 0,
          width = 0,
          height = 0,
          oWidth,
          oHeight,
          dimension,
          oldHideTable,
          oldHideCanvas,
          minWidth;

      resizer.addClass('resizer');
      el.append(resizer);

      resizer.on('mousedown', function(evt) {
        evt.preventDefault();

        minWidth = $('.content > .container')[0].getBoundingClientRect().width / 12 - 15;

        oldHideTable = scope.hideTable;
        oldHideCanvas = scope.hideCanvas;

        if (scope.hideChart) {
          return;
        }

        dimension = utils.offset(el);
        width = oWidth = dimension.width;
        height = oHeight =  dimension.height;

        startX = evt.pageX;
        startY = evt.pageY;

        $document.on('mousemove', mousemove);
        $document.on('mouseup', mouseup);
      });

      function mousemove(evt) {
        scope.$apply(function(){
          scope.hideCanvas = true;
          scope.hideTable = true;
        });

        height += evt.pageY - startY;
        width += evt.pageX - startX;

        startY = evt.pageY;
        startX = evt.pageX;

        el.css({
          width: width + 'px',
          height: height + 'px'
        });
      }

      function mouseup() {
        $document.unbind('mouseup', mouseup);
        $document.unbind('mousemove', mousemove);

        var r = Math.round((width - oWidth) / minWidth),
            resizer = scope.resizer(),
            chart = resizer.scope.charts[resizer.index],
            ox = chart.sizex;

        el.css({
          width: oWidth + 'px',
          height: oHeight + 'px'
        });
        if (Math.abs(r) !== 0) {
          el.attr('style', '');
          chart.sizex += r;
          if (chart.sizex <= 0) {
            chart.sizex = ox;
          }
        }

        scope.$apply(function() {
          scope.hideTable = oldHideTable;
          scope.hideCanvas = oldHideCanvas;
        });
      }
    }

    return {
      link: link,
      scope: {
        resizer: '&'
      }
    };
  });
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
/* global angular:false */
'use strict';

angular.module('polaris.services')
  .factory('boxSize', function($document) {
    return {
      setUp: function(opts) {
        var rules;

        this.baseDimention = opts.baseDimention;
        rules = this.buildRules();
        this.installRules(rules);
      },
      buildRules: function() {
        var baseWidth = this.baseDimention[0],
            baseHeight = this.baseDimention[1],
            map = {},
            rules = [],
            i;

        for (i = 1; i < 10; i++) {
          map[i] = [baseWidth * i, baseHeight * i];
        }

        angular.forEach(map, function(v, k) {
          var sizeY = '[data-y="' + k + '"]',
              yRule = '{height:' + v[1] + 'px;}';
          rules.push(sizeY + yRule);
        });

        return rules;
      },
      installRules: function(rules) {
        var head = $document[0].querySelector('head'),
            style = $document[0].createElement('style');
        if (style.styleSheet) {
          style.styleSheet.cssText = rules.join('');
        }else{
          style.appendChild(document.createTextNode(rules.join('')));
        }
        head.appendChild(style);
      }
    };
  });
/* global angular:false */
'use strict';

angular.module('polaris.services')
  .factory('cache', function() {
    var cache = {};
    var temp = {
      set: function(key, value) {
        cache[key] = value;
      },
      get: function(key) {
        return cache[key];
      },
      keys: function() {
        return Object.keys(cache);
      }
    };

    return {
      temp: temp,
    };
  });
/* global angular: false, d3:false */
'use strict';

angular.module('polaris.services')
  .factory('tooltipService', function() {
    function Tooltip(parser) {
      this.parser = parser;
    }

    Tooltip.prototype.set = function() {
      setTooltip(this.parser);
    };

    Tooltip.prototype.reset = function() {
      setTooltip(this.parser);
    };

    function setTooltip(parser) {
      if (parser.type === 'rect') {
        rect(parser);
      } else if (parser.type === 'line') {
        line(parser);
      } else if (parser.type === 'arc') {
        arc(parser);
      }
    }

    function config() {
      return {
        placement: 'e',
        smartPlacement: true,
        closeDelay: 0,
        fadeInTime: 0,
        fadeOutTime: 0,
      };
    }

    function rect(parser) {
      var el = parser.el,
          target = el.find('.marks > g > g > g > g:nth-child(3)'),
          rects = target.find('rect[class!="background"]'),
          msg;

      angular.forEach(rects, function(rect) {
        var item = d3.select(rect).datum(),
            val = item.datum.data.val,
            conf = config();

        msg = '<ul class="tooltip-text"><li><span>' + val + '</span></li></ul>';
        $(rect).data('powertip', msg)
          .powerTip(conf);
      });
    }

    function arc(parser) {
      var el = parser.el,
          targets = el.find('.marks > g > g > g > g:nth-child(2) path'),
          msg;

      targets.css('pointer-events', 'visible');

      angular.forEach(targets, function(target) {
        var item = d3.select(target).datum(),
            val = item.datum.data.val,
            angle = item.endAngle - item.startAngle,
            conf = config();

        msg = '<ul class="tooltip-text"><li><span>' + val +
          '(' + parseFloat((angle / (2 * Math.PI) * 100).toFixed(2)) + '%)' +
          '</span></li></ul>';

        conf.followMouse = true;
        $(target).data('powertip', msg)
          .powerTip(conf);
      });
    }

    function line(parser) {
      var el = parser.el,
          g = $('.marks > g > g > g > .background', el),
          conf = config(),
          msg,
          indicator;

      indicator = $('<div class="indicator"></div>');
      el.find('.vega').append(indicator);

      conf.manual = true;
      indicator.css('height', parser.view.height()).powerTip(conf);

      function move(evt) {
        var vegaPos = $('.vega', el).offset(),
            chartPos = g.offset(),
            scales = parser.view.model().scene().items[0].scales,
            x = evt.clientX - chartPos.left,
            xidx = scales.x.invert(x).getTime(),
            data = parser.view.data().table,
            hit = null,
            pos = {},
            values;

        $.powerTip.hide();

        pos.top = chartPos.top - vegaPos.top;
        pos.left = chartPos.left - vegaPos.left;

        indicator.css('top', pos.top);

        $.each(data, function(i, d){
          if (hit == null ||
              Math.abs(d.data.idx - xidx) < Math.abs(hit.data.idx - xidx)) {
            hit = d;
          }
        });
        values = data.reduce(function(prev, d){
          if (d.data.idx === hit.data.idx) {
            prev.push(d);
          }
          return prev;
        }, []);

        msg = message(values, scales,
                      parser.view.model().scene().items[0].legends[0]);
        indicator.css('left', scales.x(hit.data.idx) + pos.left)
          .show()
          .data('powertip', msg);
        $.powerTip.show(indicator);
      }

      g.mousemove(move);
      g.mouseout(function() {
        $.powerTip.hide();
        indicator.hide();
      });
    }

    function message(values, scales, legend) {
      var color = 'hsl(205, 71%, 41%)',
          title = '',
          msg = '<ul class="tooltip-text">';
      $.each(values, function(i, v){
        if (legend) {
          color = scales.color(v.data.col);
          title = v.data.col;
        }

        msg += '<li style="color:' + color + ';"><span>' +
          title + ' ' + parseFloat(v.data.val.toFixed(2)) + '</span></li>';
      });
      return msg + '</ul>';
    }

    return {
      Tooltip: Tooltip
    };
  });
/* global angular:false, vg:false */
'use strict';

angular.module('polaris.services')
  .factory('vegaService', function(utils){
    function calcPadding(view) {
      var bounds = view.model().scene().bounds,
          inset = vg.config.autopadInset,
          left = bounds.x1 < 0 ? Math.ceil(-bounds.x1) + inset : 0,
          top = bounds.y1 < 0 ? Math.ceil(-bounds.y1) + inset : 0,
          right = bounds.x2 > view._width  ? Math.ceil(+bounds.x2 - view._width) + inset : 0,
          bottom = bounds.y2 > view._height ? Math.ceil(+bounds.y2 - view._height) + inset : 0;

      return {left: left, top: top, right: right, bottom: bottom};
    }

    function Parser(el, spec) {
      this.el = el;
      if (arguments.length === 2) {
        this.init(spec);
        this.inited = true;
      } else {
        this.inited = false;
      }
    }

    Parser.prototype.init = function(data) {
      this.spec = data;
      this.rawData = angular.copy(data);
      this.type = _getType(data);
    };

    Parser.prototype.canvasDim = function(padding) {
      return {
        height: this.height - padding.top - padding.bottom - 10,
        width: this.width - padding.left - padding.right - 10
      };
    };

    Parser.prototype.parse = function() {
      var _this = this;
      vg.parse.spec(this.spec, function(chart){
        var view = chart({el: _this.el[0].querySelector('.canvas'), renderer: 'svg'}),
            arc,
            dimension,
            height,
            width;

        _this.view = view;

        view._model.build();
        view._model.encode();

        dimension = _this.canvasDim(calcPadding(view));
        height = dimension.height;
        width = dimension.width;
        if (height < 0) {
          height = _this.height;
        }
        if (width < 0) {
          width = _this.width;
        }

        view.model().scene(null);
        if (_this.type === 'arc') {
          arc = _findType(_this.spec);
          arc.properties.enter.outerRadius.value = ((height > width) ? width : height) / 2;
          view.model().defs().marks = vg.parse.marks(_this.spec, height, width);
        }
        view.height(height);
        view.width(width);

        view.update();

        _this.tooltip.set();
      });
    };

    Parser.prototype.renderTable = function(scope) {
      if (!this.tableData) {
        return;
      }
      var table = utils.formatTable(this.tableData);
      scope.chartData = table.chartData;
      scope.chartColumns = table.columns;

      return table;
    };

    Parser.prototype.resize = function(size) {
      if (!this.view) {
        return this;
      }
      this.height = size.height;
      this.width = size.width;

      var spec = angular.copy(this.rawData),
          dimension = this.canvasDim(this.view.padding()),
          height = dimension.height,
          width = dimension.width;

      if (this.type === 'arc') {
        this.spec = spec;
        this.parse();
      } else {
        this.view.height(height);
        this.view.width(width);
        this.update();
      }
      return this;
    };

    Parser.prototype.hide = function() {
      this.el.css('visibility', 'hidden');
      return this;
    };

    Parser.prototype.show = function() {
      this.el.css('visibility', 'visible');
      return this;
    };

    Parser.prototype.update = function(data) {
      if (data) {
        this.rawData = angular.copy(data);
        var rawData = vg.parse.data(data.data, ''),
            ingest;
        ingest = vg.keys(rawData.load).reduce(function(d, k) {
          return (d[k] = vg.data.ingestAll(rawData.load[k]), d);
        }, {});
        this.view.data().table = ingest.table;
      }
      this.view.model().scene({});
      this.view._build = false;
      this.view.update();
      this.tooltip.reset();
      return this;
    };

    Parser.prototype.setType = function(type) {
      var data = type || this.rawData;
      this.type = _getType(data);
    };

    function _getType(data) {
      var type;

      if (angular.isString(data)) {
        type = data;
      } else {
        type = _findType(data).type;
      }

      if (type === 'line' || type === 'area' || type === 'symbol') {
        return 'line';
      }
      return type;
    }

    function _findType(spec) {
      function recurse(marks) {
        for (var i = 0; i < marks.length; ++i) {
          if (marks[i].type !== 'group') {
            return marks[i];
          }
          if (marks[i].marks) {
            return recurse(marks[i].marks);
          }
        }
      }
      return recurse(spec.marks);
    }

    return {
      Parser: Parser,
    };
  });

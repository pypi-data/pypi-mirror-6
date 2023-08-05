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

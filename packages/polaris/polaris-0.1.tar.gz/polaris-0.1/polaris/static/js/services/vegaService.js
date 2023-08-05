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

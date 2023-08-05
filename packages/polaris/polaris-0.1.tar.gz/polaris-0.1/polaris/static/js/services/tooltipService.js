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

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

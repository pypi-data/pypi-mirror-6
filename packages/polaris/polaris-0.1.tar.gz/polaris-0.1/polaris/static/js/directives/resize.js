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

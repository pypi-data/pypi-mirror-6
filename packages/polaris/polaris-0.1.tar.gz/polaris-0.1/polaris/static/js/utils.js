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

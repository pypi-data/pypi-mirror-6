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

/* jshint -W098:true, -W117:true */
define([
  'jquery',
  'underscore',
  'backbone'
], function($, _, Backbone) {
  'use strict';
  var initialize = function() {
    var _ajax = Backbone.ajax;
    Backbone.ajax = function(options) {
      var _complete = options.complete;
      options.complete = function(response) {
        if (this.url.substring(0, 6) !== '/event') {
          var execTime = response.getResponseHeader('Execution-Time');
          var color;
          if (execTime > 400) {
            color = '#ff0000';
          }
          else if (execTime > 200) {
            color = '#ff6b0d';
          }
          else {
            color = '#0066ff';
          }
          console.log('%c' + execTime + 'ms ' + this.url, 'color: ' + color);
        }
        _complete(response);
      };
      return _ajax.call(Backbone.$, options);
    };
  };

  return initialize;
});

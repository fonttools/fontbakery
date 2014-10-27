/**
 * @license HTTP Throttler Module for AngularJS
 * (c) 2013 Mike Pugh
 * License: MIT
 */


(function() {
  "use strict";  angular.module('http-throttler', ['http-interceptor-buffer']).factory("httpThrottler", [
    '$q', '$log', 'httpBuffer', function($q, $log, httpBuffer) {
      var reqCount, service;

      reqCount = 0;
      service = {
        request: function(config) {
          var deferred;
          if (reqCount >= 30) {
            $log.warn("Too many requests");
            deferred = $q.defer();
            httpBuffer.append(config, deferred);
            return deferred.promise;
          } else {
            reqCount++;
            return config || $q.when(config);
          }
        },
        // optional method
        requestError: function(rejection) {
            reqCount++;
            return $q.reject(rejection);
        },
        responseError: function(rejection) {
            reqCount--;
            httpBuffer.retryOne();
            return $q.reject(rejection);
        },
        response: function(response) {
          reqCount--;
          httpBuffer.retryOne();
          return response || $q.when(response);
        }
      };
      return service;
    }
  ]);

  angular.module('http-interceptor-buffer', []).factory('httpBuffer', [
    '$log', function($log) {
      var buffer, retryHttpRequest, service;

      buffer = [];
      retryHttpRequest = function(config, deferred) {
        if (config != null) {
          return deferred.resolve(config);
        }
      };
      service = {
        append: function(config, deferred) {
          return buffer.push({
            config: config,
            deferred: deferred
          });
        },
        retryOne: function() {
          var req;

          if (buffer.length > 0) {
            req = buffer.pop();
            return retryHttpRequest(req.config, req.deferred);
          }
        }
      };
      return service;
    }
  ]);

}).call(this);

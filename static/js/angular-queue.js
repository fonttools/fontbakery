/**
 * Angular Queue
 * @version v0.0.1
 * @author James Seppi
 * @license MIT License, http://jseppi.mit-license.org
 */
(function(window, angular, undefined) {
'use strict';

angular.module('ngQueue', []).factory('$queue',
    ['$timeout',
    function($timeout) {

        var defaults = {
            delay: 100,
            complete: null,
            paused: false
        };

        /**
         * Implementation of the Queue class
         *
         */
        function Queue(callback, options) {
            options = angular.extend({}, defaults, options);

            if (!angular.isFunction(callback)) {
                throw new Error('callback must be a function');
            }

            //-- Private variables
            var cleared = false,
                timeoutProm = null;

            //-- Public variables
            this.queue = [];
            this.delay = options.delay;
            this.callback = callback;
            this.complete = options.complete;
            this.paused = options.paused;

            //-- Private methods
            /**
             * stop() stops processing of the queue
             *
             */
            var stop = function() {
                if (timeoutProm) {
                    $timeout.cancel(timeoutProm);
                }

                timeoutProm = null;
            };

            //-- Privileged/Public methods

            /**
             * size() returns the size of the queue
             *
             * @return<Number> queue size
             */
            this.size = function() {
                return this.queue.length;
            };

            /**
             * add() adds an item to the back of the queue
             *
             * @param<Object> item
             * @return<Number> queue size
             */
            this.add = function(item) {
                return this.addEach([item]);
            };

            /**
             * addEach() adds an array of items to the back of the queue
             *
             * @param<Array> items
             * @return<Number> queue size
             */
            this.addEach = function(items) {
                if (items) {
                    cleared = false;
                    this.queue = this.queue.concat(items);
                }

                if (!this.paused) { this.start(); }

                return this.size();
            };

            /**
             * clear() clears all items from the queue
             * and stops processing
             *
             * @return<Array> the original queue
             */
            this.clear = function() {
                var orig = this.queue;
                stop();
                this.queue = [];
                cleared = true;
                return orig;
            };

            /**
             * pause() pauses processing of the queue
             *
             */
            this.pause = function() {
                stop();
                this.paused = true;
            };


            /**
             * start() starts processing of the queue.
             * start() may be called after pause()
             *
             */
            this.start = function() {
                var _this = this;
                this.paused = false;
                if (this.size() && !timeoutProm) {
                    (function loopy() {
                        var item;

                        stop();
                        
                        if(_this.paused)
                            return;

                        if (!_this.size()) {
                            cleared = true;
                            if (angular.isFunction(_this.complete)) {
                                _this.complete.call(_this);
                            }
                            return;
                        }

                        item = _this.queue.shift();
                        _this.callback.call(_this, item);

                        timeoutProm = $timeout(loopy,
                            _this.delay);

                        return;
                    })();
                }
            };

            /**
             * indexOf() returns the first index of the item in the queue
             *
             * @param<Object> item
             * @return<Number> index of the item if found, or -1 if not
             */
            this.indexOf = function(item) {
                if (this.queue.indexOf) return this.queue.indexOf(item);

                for (var i = 0; i < this.queue.length; i++) {
                    if (item === this.queue[i]) return i;
                }
                return -1;
            };

            this.unset = function(value) {
                if(this.indexOf(value) != -1) { // Make sure the value exists
                    this.queue.splice(this.indexOf(value), 1);
                }
            }
        }

        /**
         * queue() is a convenience function to return a new Queue
         *
         * Usage: var queue = $queue.queue(someOptions);
         * 
         * @param<Function> callback - *Required* - Function called for 
         *          each item in the queue after each delay. Passed
         *          item and called with the context of Queue.
         * @param<Object> options
         *      delay<Number> - *Optional* - Number of milliseconds between each
         *          processing step of the queue. Defaults to 100.
         *      complete<Function> - *Optional* - Function called upon
         *          completion of processing all items in the queue.
         *      paused<Boolean> - *Optional* - Flag to indicate if the queue
         *          starts paused. If false, queue will start processing
         *          items immediately after the first add or addEach.
         * @return<Queue> a new Queue
         */
        Queue.queue = function(callback, options) {
            return new Queue(callback, options);
        };

        return Queue;
    }]);

})(window, window.angular);

/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import Ember from 'ember';

export default Ember.Component.extend({
  didInsertElement: function () {
    var self = this;
    var numberRange = this.get('numberRange');

    if (!numberRange.get('from') && !numberRange.get('to')) {
      numberRange.set('from', numberRange.get('min'));
      numberRange.set('to', numberRange.get('max'));
    }

    this.$('.slider').slider({
      range: true,
      min: numberRange.get('min'),
      max: numberRange.get('max'),
      units: numberRange.get('units'),
      values: [numberRange.get('from'), numberRange.get('to')],

      slide: function (event, ui) {
        numberRange.set('from', ui.values[0]);
        numberRange.set('to', ui.values[1]);
      },

      change: function () {
        self.sendAction('rangeChanged', numberRange);
      }
    });

    this.set('rendered', true);
  },

  updateMin: function () {
    if (this.get('rendered')) {
      this.$('.slider').slider('values', 0, this.get('numberRange.from'));
    }
  }.observes('numberRange.from'),

  updateMax: function () {
    if (this.get('rendered')) {
      this.$('.slider').slider('values', 1, this.get('numberRange.to'));
    }
  }.observes('numberRange.to')
});

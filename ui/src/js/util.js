/*Copyright (c) 2016 Intel, Inc.
 *
 *   Licensed under the Apache License, Version 2.0 (the "License"); you may
 *   not use this file except in compliance with the License. You may obtain
 *   a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 *   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 *   License for the specific language governing permissions and limitations
 *   under the License.
 */

var config = require('./config.js');
var util = require('./util.js');

exports.getPods = function(callback) {
  var url = config.url + '/Chassis';
  $.ajax({
    url: url,
    type: 'GET',
    success: function(resp) {
      var chassis = this.listItems(resp['Members']);
      var pods = this.filterChassis(chassis, 'Pod');
      callback(pods);
    }.bind(this),
    error: function(xhr, status, err) {
      console.error(url, status, err.toString());
    }.bind(this)
  });
};

exports.getRacks = function(callback) {
  var url = config.url + '/Chassis';
  $.ajax({
    url: url,
    type: 'GET',
    success: function(resp) {
      var chassis = this.listItems(resp['Members']);
      var racks = this.filterChassis(chassis, 'Rack');
      callback(racks);
    }.bind(this),
    error: function(xhr, status, err) {
      console.error(url, status, err.toString());
    }.bind(this)
  });
};

exports.getSystems = function(callback) {
  var url = config.url + '/v1/systems';
  $.ajax({
    url: url,
    type: 'GET',
    success: function(resp) {
      callback(resp);
    }.bind(this),
    error: function(xhr, status, err) {
      console.error(url, status, err.toString());
    }.bind(this)
  });
};

exports.getNodes = function(callback) {
  var url = config.url + '/Nodes';
  $.ajax({
    url: url,
    type: 'GET',
    success: function(resp) {
      var nodes = this.listItems(resp['Members']);
      callback(nodes);
    }.bind(this),
    error: function(xhr, status, err) {
      console.error(url, status, err.toString());
    }.bind(this)
  });
};

exports.getStorage = function(callback) {
  var url = config.url + '/Services';
  $.ajax({
    url: url,
    type: 'GET',
    dataType: 'json',
    cache: false,
    success: function(resp) {
      var services = this.listItems(resp['Members']);
      util.getLogicalDrives(services, callback);
    }.bind(this),
    error: function(xhr, status, err) {
      console.error(url, status, err.toString());
    }.bind(this)
  });
};

exports.getLogicalDrives = function(services, callback) {
  var logicalDrives = [];
  var logicalDrivesId;
  var serviceLogicalDrives;
  for (var i = 0; i < services.length; i++) {
    logicalDrivesId = util.readAndReturn(services[i]['LogicalDrives']['@odata.id']);
    serviceLogicalDrives = util.listItems(JSON.parse(logicalDrivesId)['Members']);
    for (var j = 0; j < serviceLogicalDrives.length; j++) {
      logicalDrives.push(serviceLogicalDrives[j]);
    }
  }
  callback(logicalDrives);
};

exports.listItems = function(items) {
  var returnItems = [];
  var count = items.length;
  var resource;
  var itemJson;
  var itemJsonObj;
  for (var i=0; i<count; i++) {
    resource = items[i]['@odata.id'];
    itemJson = this.readAndReturn(resource);
    itemJsonObj = JSON.parse(itemJson);
    returnItems.push(itemJsonObj);
  }
  return returnItems;
};

exports.filterChassis = function(memberList, filter) {
  var returnMembers = [];
  var chassisType;
  var memberCount = memberList.length;
  for (var i=0; i<memberCount; i++) {
    chassisType = memberList[i]["ChassisType"];
    if (chassisType == filter) {
      returnMembers.push(memberList[i]);
    }
  }
  return returnMembers;
};

exports.readAndReturn = function(resource) {
  // remove redfish from URL for passthrough
  resource = resource.replace("/redfish/v1", "");
  var url = config.url + resource;
  return $.ajax({
    url: url,
    type: 'GET',
    dataType: 'json',
    cache: false,
    async: false,
  }).responseText;
};

exports.showErrorModal = function(title, message) {
  $("#errorModal .modal-title").html(title);
  $("#errorModal .modal-body p:first").html(message);
  $("#errorModal").modal('show');
};


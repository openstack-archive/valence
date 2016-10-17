var config = require('./config.js');
var util = require('./util.js');

// Base64 username:password on client-side, and append into request header
$.ajaxSetup({
  beforeSend: function(xhr) {
    xhr.setRequestHeader('Authorization',
                         'Basic ' + btoa(config.username + ':' + config.password));
  }
});

exports.getPods = function(callback) {
  var url = config.url + '/redfish/v1/Chassis';
  $.ajax({
    url: url,
    type: 'GET',
    dataType: 'json',
    cache: false,
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
  var url = config.url + '/redfish/v1/Chassis';
  $.ajax({
    url: url,
    type: 'GET',
    dataType: 'json',
    cache: false,
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
  var url = config.url + '/redfish/v1/Systems';
  $.ajax({
    url: url,
    type: 'GET',
    dataType: 'json',
    cache: false,
    success: function(resp) {
      var systems = this.listItems(resp['Members']);
      callback(systems);
    }.bind(this),
    error: function(xhr, status, err) {
      console.error(url, status, err.toString());
    }.bind(this)
  });
};

exports.getNodes = function(callback) {
  var url = config.url + '/redfish/v1/Nodes';
  $.ajax({
    url: url,
    type: 'GET',
    dataType: 'json',
    cache: false,
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
  var url = config.url + '/redfish/v1/Services';
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


var config = require('./config.js');
var util = require('./util.js');

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
  var url = config.url + '/redfish/v1/Services/1/LogicalDrives';
  $.ajax({
    url: url,
    type: 'GET',
    dataType: 'json',
    cache: false,
    success: function(resp) {
      var drives = this.listItems(resp['Members']);
      callback(drives);
    }.bind(this),
    error: function(xhr, status, err) {
      console.error(url, status, err.toString());
    }.bind(this)
  });
};

exports.getProcessors = function(systems, callback) {
  var processors = [];
  var systemProcessorIds;
  var systemProcessors;
  for (var i = 0; i < systems.length; i++) {
    systemProcessorIds = util.readAndReturn(systems[i]['Processors']['@odata.id']);
    systemProcessorIds = JSON.parse(systemProcessorIds);
    systemProcessors = util.listItems(systemProcessorIds['Members']);
    for (var j = 0; j < systemProcessors.length; j++) {
      processors.push(systemProcessors[j]);
    }
  }
  callback(processors);
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

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

import React from "react";

var config = require('../../config.js');
var util = require('../../util.js');
var style = require("../../../css/components/home/ComposeDisplay.css");

const VlanItem = React.createClass({

  render: function() {
    return (
      <div>
        <input type="text" value={this.props.vlan[0]} readOnly/>
        <div class="btn-group" data-toggle="buttons">
          <label class={(this.props.vlan[1] == 'Untagged') ? "btn btn-primary active" : "btn btn-primary"} disabled>
            <input type="radio" name="options" readOnly/>Untagged
          </label>
          <label class={(this.props.vlan[1] == 'Tagged') ? "btn btn-primary active" : "btn btn-primary"} disabled>
            <input type="radio" name="options" readOnly/>Tagged
          </label>
        </div>
        <button class="btn remove-vlan" type="button" onClick={() => this.props.remove(this.props.vlan)}>-</button>
      </div>
    );
  }
});

const ComposeDisplay = React.createClass({

  getInitialState: function() {
    return {
      vlans: []
    };
  },

  compose: function() {
    var data = this.prepareRequest();
    var url = config.url + '/Nodes/Actions/Allocate';
    $.ajax({
      url: url,
      type: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      data: data,
      dataType: 'text',
      success: function(resp) {
        console.log(resp);
        this.clearInputs();
        this.props.onUpdateNodes();
        this.props.onHideCompose();
      }.bind(this),
      error: function (xhr, status, error) {
        var response = JSON.parse(xhr.responseText)['error'];
        var errorTitle = 'Compose Node Error: ' + response['message'];
        var errorDetail = '';
        for (var i = 0; i < response['@Message.ExtendedInfo'].length; i++)
        {
          errorDetail += response['@Message.ExtendedInfo'][i]['Message'] + ' ';
        }
        util.showErrorModal(errorTitle, errorDetail);
      }.bind(this)
    });
  },

  prepareRequest: function() {
    var name = document.getElementById('name').value;
    var description = document.getElementById('description').value;
    var totalMem = document.getElementById('totalMem').value;
    var storageCapacity = document.getElementById('storageCapacity').value;
    var iqn = document.getElementById('iqn').value;
    var masterDrive = document.getElementById('remoteDrives').value;
    var processorModel = document.getElementById('processorModels').value;
    var vlans = this.state.vlans.map(function(obj) {
                  return {"VLANId": obj[0],
                          "Tagged": (obj[1] == "Untagged") ? "false": "true"}
                })
    var data = {
      "Name": name,
      "Description": description,
      "Memory": [{
        "CapacityMiB": totalMem * 1000
      }]
    }
    if (processorModel != 'null') {
      data["Processors"] = [{"Model": processorModel}];
    }
    if (iqn != 'null' && masterDrive != 'null') {
      data["RemoteDrives"] = [{
        "CapacityGiB": storageCapacity,
        "iSCSIAddress": iqn,
        "Master": {
          "Type": "Snapshot",
          "Resource": {
            "@odata.id": masterDrive
          }
        }
      }];
    }
    if (vlans.length > 0) {
      data["EthernetInterfaces"] = [{"VLANs": vlans}];
    }
    return JSON.stringify(data);
  },

  clearInputs: function() {
    document.getElementById("inputForm").reset();
    this.setState({vlans: []});
  },

  addVlan: function() {
    var vlanId = document.getElementById('vlanId').value;
    var vlanTag = $(".btn-primary.vlan.active input:first").val();
    document.getElementById('vlanId').value = '';
    this.setState({
      vlans: this.state.vlans.concat([[vlanId, vlanTag]])
    });
  },

  removeVlan: function(vlan) {
    var index = -1;
    for (var i = 0; i < this.state.vlans.length; i++) {
      if (vlan[0] == this.state.vlans[i][0] &&
          vlan[1] == this.state.vlans[i][1]) {
        index = i;
        break;
      }
    }
    var newData = this.state.vlans.slice();
    newData.splice(index, 1);
    this.setState({vlans: newData});
  },

  render: function() {
    var displayStyle;
    if (this.props.display) {
      displayStyle = "inline-block";
    } else {
      displayStyle = "none";
    }
    return (
      <div class="compose-node-details" style={{display: displayStyle}}>
        <form id="inputForm">
          <table>
            <tbody>
              <tr>
                <td>Name:</td>
                <td><input type="text" id="name" /></td>
              </tr>
              <tr>
                <td>Description:</td>
                <td><input type="text" id="description" /></td>
              </tr>
              <tr>
                <td>System Memory GB:</td>
                <td><input type="number" min="0" id="totalMem" /></td>
              </tr>
              <tr>
                <td>Processor Model:</td>
                <td><select id="processorModels" /></td>
              </tr>
              <tr>
                <td>Remote Storage Capacity GB:</td>
                <td><input type="number" min="0" id="storageCapacity" /></td>
              </tr>
              <tr>
                <td>Remote storage IQN:</td>
                <td><input type="text" id="iqn" /></td>
              </tr>
              <tr>
                <td>Remote storage master drive:</td>
                <td><select id="remoteDrives" /></td>
              </tr>
              <tr>
                <td>Ethernet interface:</td>
                <td>
                  {this.state.vlans.map(function(obj) {
                    return <VlanItem vlan={obj} remove={this.removeVlan} />
                  }.bind(this))}

                  <div class="control-group" id="fields">
                    <div class="controls" id="profs">
                      <form class="input-append">
                        <div id="field">
                          <input class="input" id="vlanId" type="number" min="0" placeholder="VLAN ID"/>
                          <div class="btn-group" data-toggle="buttons">
                            <label class="btn btn-primary vlan active">
                              <input type="radio" name="options" id="vlanUntagged" value="Untagged" checked/>Untagged
                            </label>
                            <label class="btn btn-primary vlan">
                              <input type="radio" name="options" id="vlanTagged" value="Tagged"/>Tagged
                            </label>
                          </div>
                          <button id="btn-add-vlan" class="btn add-vlan" type="button" onClick={() => this.addVlan()}>+</button>
                        </div>
                      </form>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </form>
        <input type="button"
         class="compose-button"
         onClick={() => this.compose()} value="Compose" />
        <input type="button"
         class="detail-button"
         onClick={() => this.props.onHideCompose()} value="Return" />
      </div>
    );
  }

});

export default ComposeDisplay

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

const ComposeDisplay = React.createClass({

  compose: function() {
    var data = this.prepareRequest();
    var url = config.url + '/v1/nodes';
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
    return JSON.stringify(data);
  },

  clearInputs: function() {
    document.getElementById("inputForm").reset();
  },

  render: function() {
    var displayStyle;
    if (this.props.display) {
      displayStyle = "inline-block";
    } else {
      displayStyle = "none";
    }
    return (
      <div class="details" style={{display: displayStyle}}>
        <form id="inputForm">
          <table>
            <tbody>
              <tr>
                <td align="right">Name:</td>
                <td align="left"><input type="text" id="name" /></td>
              </tr>
              <tr>
                <td align="right">Description:</td>
                <td align="left"><input type="text" id="description" /></td>
              </tr>
              <tr>
                <td align="right">System Memory GB:</td>
                <td align="left"><input type="number" min="0" id="totalMem" /></td>
              </tr>
              <tr>
                <td align="right">Processor Model:</td>
                <td align="left"><select id="processorModels" /></td>
              </tr>
              <tr>
                <td align="right">Remote Storage Capacity GB:</td>
                <td align="left"><input type="number" min="0" id="storageCapacity" /></td>
              </tr>
              <tr>
                <td align="right">Remote storage IQN:</td>
                <td align="left"><input type="text" id="iqn" /></td>
              </tr>
              <tr>
                <td align="right">Remote storage master drive:</td>
                <td align="left"><select id="remoteDrives" /></td>
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

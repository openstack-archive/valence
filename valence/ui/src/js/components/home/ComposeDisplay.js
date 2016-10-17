import React from "react";

var config = require('../../config.js');
var util = require('../../util.js');

const ComposeDisplay = React.createClass({

  compose: function() {
    var data = this.prepareRequest();
    var url = config.url + '/redfish/v1/Nodes/Actions/Allocate';
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
    if (procModel != 'null') {
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
    return (
        <div class="details" style={{display: this.props.display}}>
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
                <tr>
                  <td align="right">Processor Model:</td>
                  <td align="left"><select id="processorModels" /></td>
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

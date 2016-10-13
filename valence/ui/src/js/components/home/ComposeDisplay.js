import React from "react";

var config = require('../../config.js');
var util = require('../../util.js');

const ComposeDisplay = React.createClass({

  getInitialState: function() {
    return {
      processors: [],
      errorTitle: '',
      errorMsg: ''
    };
  },

  componentDidMount() {
    this.getProcessors();
  },

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
        var errorDetail = '';
        for (var i = 0; i < response['@Message.ExtendedInfo'].length; i++)
        {
          errorDetail += response['@Message.ExtendedInfo'][i]['Message'] + ' ';
        }
        this.setState({errorTitle: response['message']});
        this.setState({errorMsg: errorDetail});

        $("#composeError").modal('show');
      }.bind(this)
    });
  },

  getProcessors: function() {
    util.getProcessors(this.props.systemList, this.setProcessors);
  },

  setProcessors: function(processors) {
    this.setState({processors: processors});
    this.fillForms();
  },

  fillForms: function() {
    var sel = document.getElementById('procModels');
    sel.innerHTML = "";
    for (var i = 0; i < this.state.processors.length; i++) {
      if (this.state.processors[i]['Model']) {
        var opt = document.createElement('option');
        opt.innerHTML = this.state.processors[i]['Model'];
        opt.value = this.state.processors[i]['Model'];
        sel.appendChild(opt);
      }
    }
  },

  prepareRequest: function() {
    var name = document.getElementById('name').value;
    var description = document.getElementById('description').value;
    var totalMem = document.getElementById('totalMem').value;
    var procModel = document.getElementById('procModels').value;
    if (procModel == "") {
      procModel = null;
    }
    var data = {
      "Name": name,
      "Description": description,
      "Memory": [{
        "CapacityMiB": totalMem * 1000
      }],
      "Processors": [{
        "Model": procModel
      }]
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
                  <td align="right">Processor Model:</td>
                  <td align="left"><select id="procModels" /></td>
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

          <div class="modal fade" id="composeError" role="dialog">
            <div class="modal-dialog modal-lg">
              <div class="modal-content">
                <div class="modal-header">
                  <button type="button" class="close" data-dismiss="modal">&times;</button>
                  <h4 class="modal-title">Compose Node Error: {this.state.errorTitle}</h4>
                </div>
                <div class="modal-body">
                  <p>{this.state.errorMsg}</p>
                </div>
                <div class="modal-footer">
                  <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                </div>
              </div>
            </div>
          </div>
        </div>
    );
  }

});

export default ComposeDisplay

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
var style = require("../../../css/components/home/NodeList.css");

const NodeList = React.createClass({

  delete: function(nodeId) {
    var url = config.url + '/Nodes/' + nodeId;
    $.ajax({
      url: url,
      type: 'DELETE',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      success: function(resp) {
        this.props.onUpdateNodes();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });
  },

  setBoot: function(nodeId) {
    var url = config.url + '/Nodes/' + nodeId;
    $.ajax({
      url: url,
      type: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify({
        "Boot": {
          "BootSourceOverrideEnabled": "Continuous",
          "BootSourceOverrideTarget": "Pxe"
        }
      }),
      success: function(resp) {
        this.props.onUpdateNodes();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });
  },

  assemble: function(nodeId) {
    var url = config.url + '/Nodes/' + nodeId + '/Actions/ComposedNode.Assemble';
    $.ajax({
      url: url,
      type: 'POST',
      success: function(resp) {
        this.props.onUpdateNodes();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });
  },

  powerOn: function(nodeId) {
    var url = config.url + '/Nodes/' + nodeId + '/Actions/ComposedNode.Reset';
    $.ajax({
      url: url,
      type: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify({"ResetType": "On"}),
      success: function(resp) {
        this.props.onUpdateNodes();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });
  },

  renderList: function() {
    return this.props.nodes.map((node, i) =>
      <div class="resource" key={i}>
        {node.Name}
        <input type="button" class="node-detail-button" onClick={() => this.props.onShowDetail(node, this.props.header)} value="Show" />
        <input type="button" class="node-detail-button" onClick={() => this.delete(node.Id)} value="Delete" />
        <input type="button" class="node-detail-button" onClick={() => this.setBoot(node.Id)} value="Set Boot Source" />
        <input type="button" class="node-detail-button" onClick={() => this.assemble(node.Id)} value="Assemble" />
        <input type="button" class="node-detail-button" onClick={() => this.powerOn(node.Id)} value="Power On" />
        <br />
        {node.Description}
      </div>
    );
  },

  render: function() {
    return (
      <div>
        {this.renderList()}
      </div>
    );
  },
});

NodeList.defaultProps = { nodes: [], header: ""};

export default NodeList;

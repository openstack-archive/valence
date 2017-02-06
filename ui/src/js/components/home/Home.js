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
import ResourceList from "./ResourceList";
import NodeList from "./NodeList";

var config = require('../../config.js');
var util = require('../../util.js');
var style = require("../../../css/components/home/Home.css");

const Home = React.createClass({

  configCompose: function() {
    /* This is a temporary function that will compose a node based on the JSON value
     * of the nodeConfig variable in config.js.
     *
     * TODO(ntpttr): Remove this once the compose menu is fully flushed out.
     */
    var url = config.url + '/Nodes/Actions/Allocate';
    $.ajax({
      url: url,
      type: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      data: JSON.stringify(config.nodeConfig),
      dataType: 'text',
      success: function(resp) {
        this.props.onUpdateNodes();
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

  renderHome: function() {
    return (
      <div>
        <div class="jumbotron">
          <h2>Welcome to RSD Details</h2>
          <p>This is a brief overview of all kinds of resources in this environment. See the <a href="#">User Guide</a> for more information on how to configure them.</p>
          <p>
            <input type="button" class="btn btn-lg btn-primary compose-node-button" onClick={() => this.props.onShowCompose()} value="Compose Node" />
            <input type="button" class="btn btn-lg btn-primary" onClick={() => this.configCompose()} value="Compose From Config File" />
          </p>
        </div>

        <div class="dashboard">
          <div class="row">
            <div class="col-sm-3 col-md-2 sidebar">
              <ul class="nav nav-sidebar">
                <li class="active"><a href="#pods" data-toggle="tab" onClick={() => this.props.onUpdatePods()}>PODS</a></li>
                <li><a href="#racks" data-toggle="tab" onClick={() => this.props.onUpdateRacks()}>RACKS</a></li>
                <li><a href="#systems" data-toggle="tab" onClick={() => this.props.onUpdateSystems()}>SYSTEMS</a></li>
                <li><a href="#storage" data-toggle="tab" onClick={() => this.props.onUpdateStorage()}>STORAGE</a></li>
                <li><a href="#composednodes" data-toggle="tab" onClick={() => this.props.onUpdateNodes()}>COMPOSED NODES</a></li>
              </ul>
            </div>
            <div class="col-sm-9 col-md-10 main">
              <div class="tab-content">
                <div role="tabpanel" class="tab-pane active" id="pods">
                  <ResourceList
                    onShowDetail={this.props.onShowDetail}
                    resources={this.props.podList}
                    header="PODS"
                  />
                </div>
                <div role="tabpanel" class="tab-pane" id="racks">
                  <ResourceList
                    onShowDetail={this.props.onShowDetail}
                    resources={this.props.rackList}
                    header="RACKS"
                  />
                </div>
                <div role="tabpanel" class="tab-pane" id="systems">
                  <ResourceList
                    onShowDetail={this.props.onShowDetail}
                    resources={this.props.systemList}
                    inUseResources={this.props.usedSystemList}
                    header="SYSTEMS"
                  />
                </div>
                <div role="tabpanel" class="tab-pane" id="storage">
                  <ResourceList
                    onShowDetail={this.props.onShowDetail}
                    resources={this.props.storageList}
                    header="STORAGE"
                  />
                </div>
                <div role="tabpanel" class="tab-pane" id="composednodes">
                  <NodeList
                    onShowDetail={this.props.onShowDetail}
                    onUpdateNodes={this.props.onUpdateNodes}
                    nodes={this.props.nodeList}
                    header="COMPOSED NODES"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  },

  render: function() {
    if (this.props.display) {
      return this.renderHome();
    } else {
      return (<div styles="none" />);
    }
  }

});

export default Home

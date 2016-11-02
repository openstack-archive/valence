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
import ComposeDisplay from "./home/ComposeDisplay";
import DetailDisplay from "./home/DetailDisplay";
import Home from "./home/Home";

var util = require('../util.js');

const Layout = React.createClass({

  getInitialState: function() {
    return {
      displayHome: true,
      displayDetail: false,
      displayCompose: false,
      detailData: "",
      detailType: "",
      pods: [],
      racks: [],
      systems: [],
      systemsInUse: [],
      storage: [],
      nodes: []
    };
  },

  componentWillMount: function() {
    this.getPods();
    this.getRacks();
    this.getSystems();
    this.getStorage();
    this.getNodes();
  },

  displayHome: function() {
    this.setState({
      displayHome: true,
      displayDetail: false,
      displayCompose: false
    });
  },

  displayDetail: function(item, itemType) {
    this.setState({
      displayHome: false,
      displayDetail: true,
      displayCompose: false,
      detailData: item,
      detailType: itemType
    });
  },

  displayCompose: function() {
    this.getStorage();
    this.fillComposeForms();
    this.setState({
      displayHome: false,
      displayDetail: false,
      displayCompose: true
    });
  },

  fillDropdownMenu: function(menu, itemNames, itemValues) {
    var sel = document.getElementById(menu);
    sel.innerHTML = '';
    var opt = document.createElement('option');
    opt.innerHTML = 'None';
    opt.value = null;
    sel.appendChild(opt);
    for (var i = 0; i < itemNames.length; i++) {
      opt = document.createElement('option');
      opt.innerHTML = itemNames[i];
      opt.value = itemValues[i];
      sel.appendChild(opt);
    }
  },

  fillComposeForms: function() {
    // Fill processor dropdown menu
    var processorModels = [];
    var model;
    for (var i = 0; i < this.state.systems.length; i++) {
      model = this.state.systems[i]['ProcessorSummary']['Model'];
      if (model && processorModels.indexOf(model) < 0) {
        processorModels.push(model);
      }
    }
    this.fillDropdownMenu('processorModels', processorModels, processorModels);
    // Fill storage dropdown menu
    var driveNames = [];
    var driveValues = [];
    for (var i = 0; i < this.state.storage.length; i++) {
      if (this.state.storage[i]['Mode'] == 'LV') {
        driveNames.push(this.state.storage[i]['Name']);
        driveValues.push(this.state.storage[i]['@odata.id']);
      }
    }
    this.fillDropdownMenu('remoteDrives', driveNames, driveValues);
  },

  getPods: function() {
    util.getPods(this.setPods);
  },

  setPods: function(pods) {
    this.setState({pods: pods});
  },

  getRacks: function() {
    util.getRacks(this.setRacks);
  },

  setRacks: function(racks) {
    this.setState({racks: racks});
  },

  getSystems: function() {
    util.getSystems(this.setSystems);
  },

  setSystems: function(systems) {
    this.setState({systems: systems});
  },

  getStorage: function() {
    util.getStorage(this.setStorage);
  },

  setStorage: function(storage) {
    this.setState({storage: storage});
  },

  getNodes: function() {
    util.getNodes(this.setNodes);
  },

  setNodes: function(nodes) {
    // Update systems in use
    var usedSystems = [];
    for (var i = 0; i < nodes.length; i++) {
      usedSystems.push(nodes[i]["Links"]["ComputerSystem"]["@odata.id"]);
    }
    this.setState({systemsInUse: usedSystems});
    this.setState({nodes: nodes});
  },

  render: function() {
    return (
      <div class="container">
        <nav class="navbar navbar-default">
          <div class="container-fluid">
            <div class="navbar-header">
              <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
              </button>
              <a class="navbar-brand" href="#">Rack Scale Design</a>
            </div>
            <div id="navbar" class="navbar-collapse collapse">
              <ul class="nav navbar-nav">
                <li class="active"><a href="#">Home</a></li>
                <li class="dropdown">
                  <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Configure <span class="caret"></span></a>
                  <ul class="dropdown-menu">
                    <li><a href="#">Action</a></li>
                    <li><a href="#">Another action</a></li>
                    <li><a href="#">Something else here</a></li>
                    <li role="separator" class="divider"></li>
                    <li class="dropdown-header">Nav header</li>
                    <li><a href="#">Separated link</a></li>
                    <li><a href="#">One more separated link</a></li>
                  </ul>
                </li>
                <li><a href="#">Support</a></li>
                <li><a href="#">About</a></li>
              </ul>
              <ul class="nav navbar-nav navbar-right">
                <li class="active"><a href="./">Login<span class="sr-only">(current)</span></a></li>
              </ul>
            </div>
          </div>
        </nav>

        <Home
          display={this.state.displayHome}
          podList={this.state.pods}
          rackList={this.state.racks}
          systemList={this.state.systems}
          usedSystemList={this.state.systemsInUse}
          storageList={this.state.storage}
          nodeList={this.state.nodes}
          onShowDetail={this.displayDetail}
          onShowCompose={this.displayCompose}
          onUpdatePods={this.getPods}
          onUpdateRacks={this.getRacks}
          onUpdateSystems={this.getSystems}
          onUpdateStorage={this.getStorage}
          onUpdateNodes={this.getNodes}
        />
        <DetailDisplay
          display={this.state.displayDetail}
          data={this.state.detailData}
          type={this.state.detailType}
          onHideDetail={this.displayHome}
        />
        <ComposeDisplay
          display={this.state.displayCompose}
          systemList={this.state.systems}
          onHideCompose={this.displayHome}
          onUpdateNodes={this.getNodes}
        />

        <footer class="footer navbar-fixed-bottom">
          <div class="container">
            <p class="text-muted">Version: 0.1</p>
          </div>
        </footer>

        <div class="modal fade" id="errorModal" role="dialog">
          <div class="modal-dialog modal-lg">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal">&times;</button>
                <h4 class="modal-title">Error:</h4>
              </div>
              <div class="modal-body">
                <p></p>
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

export default Layout;

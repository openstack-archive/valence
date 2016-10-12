import React from "react";
import ComposeDisplay from "./home/ComposeDisplay";
import DetailDisplay from "./home/DetailDisplay";
import Home from "./home/Home";

var util = require('../util.js');

const Layout = React.createClass({

  getInitialState: function() {
    return {
      homeDisplay: "inline-block",
      detailDisplay: "none",
      composeDisplay: "none",
      detailData: "",
      pods: [],
      racks: [],
      systems: [],
      storage: [],
      processors: [],
      nodes: []
    };
  },

  componentWillMount: function() {
    this.getPods();
    this.getRacks();
    this.getSystems();
    this.getProcessors();
    this.getStorage();
    this.getNodes();
  },

  displayHome: function() {
    this.setState({
      homeDisplay: "inline-block",
      detailDisplay: "none",
      composeDisplay: "none",
      detailData: ""
    });
  },

  displayDetail: function(item) {
    this.setState({
      homeDisplay: "none",
      detailDisplay: "inline-block",
      composeDisplay: "none",
      detailData: JSON.stringify(item, null, "\t")
    });
  },

  displayCompose: function() {
    this.getProcessors();
    this.getStorage();
    this.fillComposeForms();
    this.setState({
      homeDisplay: "none",
      detailDisplay: "none",
      composeDisplay: "inline-block",
      detailData: ""
    });
  },

  fillComposeForms: function() {
    var sel = document.getElementById('procModels');
    sel.innerHTML = "";
    var opt = document.createElement('option');
    opt.innerHTML = 'None';
    opt.value = null;
    sel.appendChild(opt);
    for (var i = 0; i < this.state.processors.length; i++) {
      if (this.state.processors[i]['Model']) {
        opt = document.createElement('option');
        opt.innerHTML = this.state.processors[i]['Model'];
        opt.value = this.state.processors[i]['Model'];
        sel.appendChild(opt);
      }
    }
    sel = document.getElementById('remoteDrives');
    sel.innerHTML = "";
    opt = document.createElement('option');
    opt.innerHTML = 'None';
    opt.value = null;
    sel.appendChild(opt);
    for (var i = 0; i < this.state.storage.length; i++) {
      if (this.state.storage[i]['Mode'] == 'LV') {
        opt = document.createElement('option');
        opt.innerHTML = this.state.storage[i]['Name'];
        opt.value = this.state.storage[i]['@odata.id'];
        sel.appendChild(opt);
      }
    }
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

  getProcessors: function() {
    util.getProcessors(this.state.systems, this.setProcessors);
  },

  setProcessors: function(processors) {
    this.setState({processors: processors});
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
          display={this.state.homeDisplay}
          podList={this.state.pods}
          rackList={this.state.racks}
          systemList={this.state.systems}
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
          display={this.state.detailDisplay}
          data={this.state.detailData}
          onHideDetail={this.displayHome}
        />
        <ComposeDisplay
          display={this.state.composeDisplay}
          systemList={this.state.systems}
          onHideCompose={this.displayHome}
          onUpdateNodes={this.getNodes}
        />

        <footer class="footer navbar-fixed-bottom">
          <div class="container">
            <p class="text-muted">Version: 0.1</p>
          </div>
        </footer>
      </div>
    );
  }
});

export default Layout;

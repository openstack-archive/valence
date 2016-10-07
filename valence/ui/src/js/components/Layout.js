import React from "react";
import ComposeDisplay from "./home/ComposeDisplay";
import DetailDisplay from "./home/DetailDisplay";
import Home from "./home/Home";

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
      nodes: []
    };
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
    this.setState({
      homeDisplay: "none",
      detailDisplay: "none",
      composeDisplay: "inline-block",
      detailData: ""
    });
  },

  updatePods: function(pods) {
    this.setState({pods: pods});
  },

  updateRacks: function(racks) {
    this.setState({racks: racks});
  },

  updateSystems: function(systems) {
    this.setState({systems: systems});
  },

  updateStorage: function(storage) {
    this.setState({storage: storage});
  },

  updateNodes: function(nodes) {
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
          onUpdatePods={this.updatePods}
          onUpdateRacks={this.updateRacks}
          onUpdateSystems={this.updateSystems}
          onUpdateStorage={this.updateStorage}
          onUpdateNodes={this.updateNodes}
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

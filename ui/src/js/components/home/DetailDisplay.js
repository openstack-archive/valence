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

var style = require("../../../css/components/home/DetailDisplay.css");

const DetailDisplay = React.createClass({

  renderPod: function(data) {
    return (
      <div class="details" styles="inline-block">
        <h2>Pod</h2>
        <hr class="separator" />
        <p>Name: {data.Name}</p>
        <p>Description: {data.Description}</p>
        <p>State: {data.Status.State}</p>
        <p>Health: {data.Status.Health}</p>
        <input type="button"
         class="detail-button"
         onClick={() => this.props.onHideDetail()} value="Return" />
      </div>
    );
  },

  renderRack: function(data) {
    return (
      <div class="details" styles="inline-block">
        <h2>Rack</h2>
        <hr class="separator" />
        <p>Name: {data.Name}</p>
        <p>Description: {data.Description}</p>
        <p>Manufacturer: {data.Manufacturer}</p>
        <input type="button"
         class="detail-button"
         onClick={() => this.props.onHideDetail()} value="Return" />
      </div>
    );
  },

  renderSystem: function(data) {
    return (
      <div class="details" styles="inline-block">
        <h2>System</h2>
        <hr class="separator" />
        <p>Name: {data.Name}</p>
        <p>Description: {data.Description}</p>
        <p>ID: {data.id}</p>
        <p>Health: {data.health}</p>
        <p>System Storage: {data.storage}</p>
        <p>Processor Count: {data.cpu.cores}</p>
        <p>Processor Model: {data.cpu.model}</p>
        <p>Total Memory: {data.ram} GiB</p>
        <p>Network Interfaces: {data.network}</p>
        <p>System Location: {data.location}</p>
        <input type="button"
         class="detail-button"
         onClick={() => this.props.onHideDetail()} value="Return" />
      </div>
    );
  },

  renderStorage: function(data) {
    var bootable;
    if (data.Bootable) {
      bootable = "True";
    } else {
      bootable = "False";
    }
    return (
      <div class="details" styles="inline-block">
        <h2>Storage</h2>
        <hr class="separator" />
        <p>Name: {data.Name}</p>
        <p>Description: {data.Description}</p>
        <p>State: {data.Status.State}</p>
        <p>Health: {data.Status.Health}</p>
        <p>Type: {data.Type}</p>
        <p>Mode: {data.Mode}</p>
        <p>Capacity: {data.CapacityGiB} GiB</p>
        <p>Bootable: {bootable}</p>
        <input type="button"
         class="detail-button"
         onClick={() => this.props.onHideDetail()} value="Return" />
      </div>
    );
  },

  renderNode: function(data) {
    return (
      <div class="details" styles="inline-block">
        <h2>Composed Node</h2>
        <hr class="separator" />
        <p>Name: {data.Name}</p>
        <p>Description: {data.Description}</p>
        <p>State: {data.Status.State}</p>
        <p>Health: {data.Status.Health}</p>
        <p>Processor Count: {data.Processors.Count}</p>
        <p>Total Memory: {data.Memory.TotalSystemMemoryGiB} GiB</p>
        <p>Composed State: {data.ComposedNodeState}</p>
        <p>Boot Source Target: {data.Boot.BootSourceOverrideTarget}</p>
        <input type="button"
         class="detail-button"
         onClick={() => this.props.onHideDetail()} value="Return" />
      </div>
    );
  },

  render: function() {
    if (this.props.display) {
      if (this.props.type == "PODS") {
        return this.renderPod(this.props.data);
      }
      if (this.props.type == "RACKS") {
        return this.renderRack(this.props.data);
      }
      if (this.props.type == "SYSTEMS") {
        return this.renderSystem(this.props.data);
      }
      if (this.props.type == "STORAGE") {
        return this.renderStorage(this.props.data);
      }
      if (this.props.type == "COMPOSED NODES") {
        return this.renderNode(this.props.data);
      }
      return (
        <div class="details" style={{display: "inline-block"}}>
          <h2>Nothing to display!</h2>
          <input type="button"
           class="detail-button"
           onClick={() => this.props.onHideDetail()} value="Return" />
        </div>
      );
    } else {
      return (<div styles="none" />);
    }
  }
});

export default DetailDisplay

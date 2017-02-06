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

var util = require('../../util.js');
var style = require("../../../css/components/home/ResourceList.css");

const ResourceList = React.createClass({

  render: function() {
    var inUseResources = this.props.inUseResources;
    var onShowDetail = this.props.onShowDetail;
    var resourceType = this.props.header;
    var resourceList = this.props.resources.map(function(resource) {
      if (resource.Status != null) {
        if (resource.Status.Health == "Warning") {
          return (
            <div class="warning-resource" key={resource.Id}>
              {resource.Name} | Health Warning
              <input type="button" class="detail-button" onClick={() => onShowDetail(resource, resourceType)} value="Show" />
              <br />
              {resource.Description}
            </div>
          );
        } else if (resource.Status.Health == "Critical") {
          return (
            <div class="critical-resource" key={resource.Id}>
              {resource.Name} | Health Critical
              <input type="button" class="detail-button" onClick={() => onShowDetail(resource, resourceType)} value="Show" />
              <br />
              {resource.Description}
            </div>
          );
        }
      }
      if (inUseResources.indexOf(resource["@odata.id"]) < 0) {
        return (
          <div class="resource" key={resource.Id}>
            {resource.Name}
            <input type="button" class="detail-button" onClick={() => onShowDetail(resource, resourceType)} value="Show" />
            <br />
            {resource.Description}
          </div>
        );
      } else {
        return (
          <div class="in-use-resource" key={resource.Id}>
            {resource.Name} | In Use
            <input type="button" class="detail-button" onClick={() => onShowDetail(resource, resourceType)} value="Show" />
            <br />
            {resource.Description}
          </div>
        );
      }
    });
    return (
      <div class="resourceList">
        {resourceList}
      </div>
    );
  }

});

ResourceList.defaultProps = { resources: [], inUseResources: [], header: ""};

export default ResourceList;

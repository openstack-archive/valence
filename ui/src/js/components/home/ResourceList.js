import React from "react";

var util = require('../../util.js');

const ResourceList = React.createClass({

  render: function() {
    var inUseResources = this.props.inUseResources;
    var onShowDetail = this.props.onShowDetail;
    var resourceList = this.props.resources.map(function(resource) {
      if (resource.Status != null) {
        if (resource.Status.Health == "Warning") {
          return (
            <div class="warning-resource" key={resource.Id}>
              {resource.Name} | Health Warning
              <input type="button" class="detail-button" onClick={() => onShowDetail(resource)} value="Show" />
              <br />
              {resource.Description}
            </div>
          );
        } else if (resource.Status.Health == "Critical") {
          return (
            <div class="critical-resource" key={resource.Id}>
              {resource.Name} | Health Critical
              <input type="button" class="detail-button" onClick={() => onShowDetail(resource)} value="Show" />
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
            <input type="button" class="detail-button" onClick={() => onShowDetail(resource)} value="Show" />
            <br />
            {resource.Description}
          </div>
        );
      } else {
        return (
          <div class="in-use-resource" key={resource.Id}>
            {resource.Name} | In Use
            <input type="button" class="detail-button" onClick={() => onShowDetail(resource)} value="Show" />
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

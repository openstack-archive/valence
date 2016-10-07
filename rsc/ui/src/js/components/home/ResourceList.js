import React from "react";

var util = require('../../util.js');

const ResourceList = React.createClass({

  renderList: function() {
    return this.props.resources.map((resource, i) =>
      <div class="resource" key={i}>
        {resource.Name}
        <input type="button" class="detail-button" onClick={() => this.props.onShowDetail(resource)} value="Show" />
        <br />
        {resource.Description}
        <hr class="separator"/>
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

ResourceList.defaultProps = { resources: [], header: ""};

export default ResourceList;

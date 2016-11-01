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

const ResourceList = React.createClass({

  renderList: function() {
    return this.props.resources.map((resource, i) =>
      <div class="resource" key={i}>
        {resource.Name}
        <input type="button" class="detail-button" onClick={() => this.props.onShowDetail(resource, this.props.header)} value="Show" />
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

import React from "react";

const DetailDisplay = React.createClass({

  render: function() {
    return (
        <div class="details" style={{display: this.props.display}}>
          <pre>{this.props.data}</pre>
          <input type="button"
           class="detail-button"
           onClick={() => this.props.onHideDetail()} value="Return" />
        </div>
    );
  }
});

export default DetailDisplay

import React from 'react';

const Blockinfo = ({ label, value }) => {
  return (
    <div className="info-block">
      <span className="label"><strong>{label}:</strong> </span>
      <span className="value">{value || "N/A"}</span>
    </div>
  );
};

export default Blockinfo;
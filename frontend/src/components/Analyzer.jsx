import FileHandler from "./FileHandler";
import Result from "./Result";
import "../css/Analyzer.css";
import { useState } from "react";

function Analyzer() {
  const [summarizedData, setSummarizedData] = useState("");

  const handleDataFromServer = (data) => {
    setSummarizedData(data);
  };

  return (
    <>
      <div id="container">
        <FileHandler onData={handleDataFromServer} />
        <Result summary={summarizedData} />
      </div>
    </>
  );
}

export default Analyzer;

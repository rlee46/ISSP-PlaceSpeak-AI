import FileHandler from "./FileHandler";
import Result from "./Result";
import "../../css/Analyzer.css";
import { useState } from "react";

function Analyzer() {
  const [summarizedData, setSummarizedData] = useState("");

  //Loading status
  const [isLoading, setLoadingStatus] = useState(false);

  return (
    <>
      <div id="container">
        <FileHandler onData={setSummarizedData} onLoading={setLoadingStatus} />
        <Result summary={summarizedData} isLoading={isLoading} />
      </div>
    </>
  );
}

export default Analyzer;

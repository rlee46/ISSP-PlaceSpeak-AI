import FileHandler from "./FileHandler";
import Result from "./Result";
import "../../css/Analyzer.css";
import { useState } from "react";

function Analyzer() {
  //Summarized data
  const [summarizedData, setSummarizedData] = useState("");

  //Loading status
  const [isLoading, setLoadingStatus] = useState(false);

  //File type
  const [fileType, setFileType] = useState("discussion");

  return (
    <>
      <div id="container">
        <FileHandler
          onData={setSummarizedData}
          onLoading={setLoadingStatus}
          fileType={fileType}
          onFileType={setFileType}
        />
        <Result
          summary={summarizedData}
          isLoading={isLoading}
          fileType={fileType}
        />
      </div>
    </>
  );
}

export default Analyzer;

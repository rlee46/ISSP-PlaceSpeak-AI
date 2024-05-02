import locale from "../locale/en.json";
import { useState } from "react";

function FileHandler({ onData }) {
  const [data, setData] = useState("");

  //Handle upload button click event
  const handleUpload = () => {
    const formData = new FormData();
    const fileInput = document.getElementById("file-upload");
    if (fileInput.files.length === 0) {
      alert(locale.selectFileFirst);
      return;
    }
    formData.append("file", fileInput.files[0]);

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      upload(text);
    };
    reader.readAsText(fileInput.files[0]);
  };

  //Upload CSV data to server
  const upload = (text) => {
    const data = {
      csv_data: text,
    };
    fetch("http://localhost:8000/analyze/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        onData(data);
        setData(data);
      })
      .catch((error) => console.error("Error:", error));
  };

  //Convert the table to CSV
  const toCSV = () => {
    let array = [
      ...data.entries.map((entry) => {
        return {
          KeyPhrase: entry.KeyPhrases,
          Sentiment: entry.Sentiment,
          EmotionDetection: entry.ReactionEmotion,
          ConfidenceScore: entry.ConfidenceScore,
        };
      }),
    ];
    const ret = [Object.keys(array[0])].concat(array);
    return ret
      .map((it) => {
        return Object.values(it).toString();
      })
      .join("\n");
  };

  //Download CSV
  const downloadCSV = () => {
    const fileName = "report.csv";
    const dataToDownload = toCSV();
    const blob = new Blob([dataToDownload], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", fileName);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <h2>{locale.componentheader}</h2>
      <form className="d-flex flex-wrap mb-3">
        <div className="p-2 flex-grow-1">
          <input
            id="file-upload"
            type="file"
            name="fileUpload"
            accept=".csv"
            required
          />
        </div>
        <div className="p-2">
          <button
            type="button"
            className="btn btn-primary btn-sm text-nowrap"
            onClick={handleUpload}
          >
            {locale.uploadLabel}
          </button>
        </div>
        <div className="p-2">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={handleUpload}
          >
            {locale.regenerateLabel}
          </button>
        </div>
        <div className="p-2">
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={downloadCSV}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              fill="currentColor"
              className="bi bi-download"
              viewBox="0 0 16 16"
            >
              <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5" />
              <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708z" />
            </svg>
          </button>
        </div>
      </form>
    </>
  );
}

export default FileHandler;

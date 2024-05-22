/* eslint-disable jsx-a11y/anchor-is-valid */
import locale from "../../locale/en.json";
import { useState } from "react";
import "bootstrap";

function FileHandler({ onData, onLoading, fileType, onFileType }) {
  //For server response data
  const [data, setData] = useState("");

  //Handle upload button click event
  const handleUpload = () => {
    onData("");
    setData("");
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
      if (fileType === "discussion") {
        discussionAnalysis(text);
      } else if (fileType === "survey") {
        surveyAnalysis(text);
      } else {
        alert(locale.error);
      }
    };
    reader.readAsText(fileInput.files[0]);
  };

  const checkQuestionType = (response) => {
    const ret = [];
    Object.entries(response).forEach(([question, response]) => {
      if (typeof response === "object" && !Array.isArray(response)) {
        if (response.hasOwnProperty("Yes") && response.hasOwnProperty("No")) {
          //Yes or no questions
          const item = {
            type: "yesNo",
            question: question,
            response: response,
          };
          ret.push(item);
        } else {
          //Multiple choice questions
          const item = {
            type: "multipleChoice",
            question: question,
            response: response,
          };
          ret.push(item);
        }
      } else {
        //Long answer comment questions
        const item = {
          type: "comment",
          question: question,
          response: response,
        };
        ret.push(item);
      }
    });
    return ret;
  };

  //Upload survey CSV data to server
  const surveyAnalysis = (text) => {
    onLoading(true);
    const url = "http://localhost:8080/survey/";
    const params = new URLSearchParams();
    params.append("_content", JSON.stringify({ csv_data: text }));

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: params,
    })
      .then((response) => response.json())
      .then((data) => {
        const res = checkQuestionType(data);
        onLoading(false);
        onData(res);
        setData(res);
      })
      .catch((error) => console.error("Error:", error));
  };

  //Upload discussion CSV data to server
  const discussionAnalysis = (text) => {
    onLoading(true);
    const url = "http://localhost:8080/discussion/";
    const params = new URLSearchParams();
    params.append("_content", JSON.stringify({ csv_data: text }));

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: params,
    })
      .then((response) => response.json())
      .then((data) => {
        onLoading(false);
        onData(data);
        setData(data);
      })
      .catch((error) => {
        console.error("Error:", error);
        alert(locale.fileTypeError);
      });
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
          Location: entry.Location,
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
    if (fileType === "discussion") {
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
    }
  };

  return (
    <>
      <h2>
        {fileType.charAt(0).toUpperCase() +
          fileType.slice(1) +
          " " +
          locale.componentheader}
      </h2>
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
          <div className="btn-group">
            <button
              className="btn btn-secondary btn-sm dropdown-toggle"
              type="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              {fileType.charAt(0).toUpperCase() + fileType.slice(1)}
            </button>
            <ul className="dropdown-menu">
              <li>
                <a
                  className="dropdown-item"
                  onClick={() => {
                    onFileType("discussion");
                    onData("");
                  }}
                  href="#"
                >
                  {locale.discussion}
                </a>
              </li>
              <li>
                <a
                  className="dropdown-item"
                  onClick={() => {
                    onFileType("survey");
                    onData("");
                  }}
                  href="#"
                >
                  {locale.survey}
                </a>
              </li>
            </ul>
          </div>
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

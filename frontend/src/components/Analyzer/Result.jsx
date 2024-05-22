import locale from "../../locale/en.json";
import BarChart from "./BarChart";
import PieChart from "./PieChart";

function Result({ summary, isLoading, fileType }) {
  if (!summary && !isLoading) {
    return (
      <>
        <h2>{locale.summaryHeader}</h2>
        <p>{locale.noFileAnalyzed}</p>
      </>
    );
  }

  if (!summary && isLoading) {
    return (
      <>
        <h2>{locale.summaryHeader}</h2>
        <div className="loading-indicator">
          <p className="placeholder-wave">
            <span className="placeholder col-12"></span>
          </p>
          <p className="placeholder-wave">
            <span className="placeholder col-12"></span>
          </p>
          <p className="placeholder-wave">
            <span className="placeholder col-12"></span>
          </p>
        </div>
      </>
    );
  }

  const discussionResult = () => {
    //Confidence data
    const confidenceLabels = [
      "0-10%",
      "11-20%",
      "21-30%",
      "31-40%",
      "41-50%",
      "51-60%",
      "61-70%",
      "71-80%",
      "81-90%",
      "91-100%",
    ];

    //Sentiment data
    const sentimentData = [
      summary.sentiment_frequencies.Negative,
      summary.sentiment_frequencies.Neutral,
      summary.sentiment_frequencies.Positive,
    ];
    const sentimentLabels = [
      locale.sentimentChart.negative,
      locale.sentimentChart.neutral,
      locale.sentimentChart.positive,
    ];

    //Location data
    let locationLabels = [];
    let locationData = [];
    summary.entries.forEach((entry) => {
      const index = locationLabels.findIndex(
        (location) => location === entry.Location
      );
      if (index < 0) {
        locationLabels.push(entry.Location);
        locationData.push(1);
      } else {
        const freq = locationData[index];
        locationData.splice(index, 1, freq + 1);
      }
    });

    return (
      <>
        <h2>{locale.summaryHeader}</h2>
        <div className="">
          <p>{summary.summary}</p>
          <div className="d-flex flex-row">
            <div className="card">
              <div className="card-body">
                <BarChart
                  data={summary.confidence_frequencies}
                  labels={confidenceLabels}
                  datasetLabel={locale.confidenceChart.title}
                />
              </div>
            </div>
            <div className="card">
              <div className="card-body">
                <PieChart data={sentimentData} labels={sentimentLabels} />
              </div>
            </div>
            <div className="card">
              <div className="card-body">
                <PieChart data={locationData} labels={locationLabels} />
              </div>
            </div>
          </div>
          <div className="flex">
            <div className="card">
              <div className="card-body">
                <table className="table table-hover">
                  <thead>
                    <tr>
                      <th scope="col">#</th>
                      <th scope="col">{locale.table.keyPhrase}</th>
                      <th scope="col">{locale.table.sentiment}</th>
                      <th scope="col">{locale.table.emotionDetection}</th>
                      <th scope="col">{locale.table.confidenceScore}</th>
                      <th scope="col">{locale.table.location}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.entries.map((entry, index) => (
                      <tr key={index}>
                        <td>{index + 1}</td>
                        <td>{entry.KeyPhrases}</td>
                        <td>{entry.Sentiment}</td>
                        <td>{entry.ReactionEmotion}</td>
                        <td>{entry.ConfidenceScore}</td>
                        <td>{entry.Location}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  };

  //Dynamically show result based on question types
  const dynamicResult = (data) => {
    if (data.type === "yesNo") {
      const labels = ["Yes", "No"];
      const values = [
        parseInt(data.response.Yes.replace("%", ""), 10),
        parseInt(data.response.No.replace("%", ""), 10),
      ];
      return <PieChart data={values} labels={labels} />;
    } else if (data.type === "multipleChoice") {
      const labels = Object.keys(data.response);
      const values = Object.values(data.response).map((value) =>
        parseInt(value.replace("%", ""), 10)
      );
      return <BarChart data={values} labels={labels} />;
    } else if (data.type === "comment") {
      return (
        <table className="table table-hover">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">{locale.chartLabels.comments}</th>
            </tr>
          </thead>
          <tbody>
            {data.response.map((entry, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>{entry}</td>
              </tr>
            ))}
          </tbody>
        </table>
      );
    } else {
      return <p>{locale.error}</p>;
    }
  };

  const surveyResult = () => {
    return (
      <>
        <h2>{locale.summaryHeader}</h2>
        <div className="flex">
          {summary.map((entry, index) => {
            return (
              <div className="card" key={index}>
                <div className="card-body">
                  <p>{entry.question}</p>
                  {dynamicResult(entry)}
                </div>
              </div>
            );
          })}
        </div>
      </>
    );
  };

  if (fileType === "discussion") {
    return discussionResult();
  } else if (fileType === "survey") {
    return surveyResult();
  } else {
    return (
      <>
        <h2>{locale.summaryHeader}</h2>
        <p>{locale.error}</p>
      </>
    );
  }
}

export default Result;

import locale from "../../locale/en.json";
import BarChart from "./BarChart";
import PieChart from "./PieChart";

function Result({ summary, isLoading }) {
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
        <table className="table table-bordered table-hover">
          <thead>
            <tr>
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
    </>
  );
}

export default Result;

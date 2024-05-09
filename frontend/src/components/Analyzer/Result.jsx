import locale from "../../locale/en.json";
import ConfidenceBarChart from "./ConfidenceBarChart";
import PieChart from "./PieChart";

function Result({ summary }) {
  if (!summary) {
    return (
      <>
        <h2>{locale.summaryHeader}</h2>
        <p>{locale.noFileAnalyzed}</p>
      </>
    );
  }

  //Process sentiment data
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

  //Process location data
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
              <ConfidenceBarChart
                confidenceData={summary.confidence_frequencies}
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

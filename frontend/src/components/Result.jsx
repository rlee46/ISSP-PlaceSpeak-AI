import locale from "../locale/en.json";
import ConfidenceBarChart from "./ConfidenceBarChart";
import SentimentPieChart from "./SentimentPieChart";

function Result({ summary }) {
  if (!summary) {
    return (
      <>
        <h2>{locale.summaryHeader}</h2>
        <p>{locale.noFileAnalyzed}</p>
      </>
    );
  }

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
              <SentimentPieChart
                sentimentData={summary.sentiment_frequencies}
              />
            </div>
          </div>
        </div>
        <table className="table table-bordered">
          <thead>
            <tr>
              <th scope="col">{locale.table.keyPhrase}</th>
              <th scope="col">{locale.table.sentiment}</th>
              <th scope="col">{locale.table.emotionDetection}</th>
              <th scope="col">{locale.table.confidenceScore}</th>
            </tr>
          </thead>
          <tbody>
            {summary.entries.map((entry, index) => (
              <tr key={index}>
                <td>{entry.KeyPhrases}</td>
                <td>{entry.Sentiment}</td>
                <td>{entry.ReactionEmotion}</td>
                <td>{entry.ConfidenceScore}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default Result;

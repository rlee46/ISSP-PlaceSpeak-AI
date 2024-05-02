import React, { useRef, useEffect, useState } from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
} from "chart.js";
import locale from "../locale/en.json";

ChartJS.register(Tooltip, Legend, ArcElement, CategoryScale);

const SentimentPieChart = ({ sentimentData }) => {
  const chartRef = useRef(null);
  const [chartData, setChartData] = useState({
    labels: [
      locale.sentimentChart.neutral,
      locale.sentimentChart.positive,
      locale.sentimentChart.negative,
    ],
    datasets: [
      {
        label: locale.sentimentChart.title,
        data: [0, 0, 0], // Default values
        backgroundColor: [
          "rgba(99, 132, 255, 0.6)",
          "rgba(75, 192, 192, 0.6)",
          "rgba(255, 99, 132, 0.6)",
        ],
        borderColor: [
          "rgba(99, 132, 255, 1)",
          "rgba(75, 192, 192, 1)",
          "rgba(255, 99, 132, 1)",
        ],
        borderWidth: 1,
      },
    ],
  });

  useEffect(() => {
    const sentiments = { Neutral: 0, Positive: 0, Negative: 0 };
    Object.keys(sentiments).forEach((sentiment) => {
      if (sentimentData.hasOwnProperty(sentiment)) {
        sentiments[sentiment] = sentimentData[sentiment];
      }
    });
    setChartData({
      labels: [
        locale.sentimentChart.neutral,
        locale.sentimentChart.positive,
        locale.sentimentChart.negative,
      ],
      datasets: [
        {
          label: locale.sentimentChart.title,
          data: [sentiments.Neutral, sentiments.Positive, sentiments.Negative],
          backgroundColor: [
            "rgba(99, 132, 255, 0.6)",
            "rgba(75, 192, 192, 0.6)",
            "rgba(255, 99, 132, 0.6)",
          ],
          borderColor: [
            "rgba(99, 132, 255, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(255, 99, 132, 1)",
          ],
          borderWidth: 1,
        },
      ],
    });
  }, [sentimentData]);

  return (
    <div>
      <Pie
        ref={chartRef}
        data={chartData}
        options={{
          responsive: true,
          maintainAspectRatio: false,
        }}
      />
    </div>
  );
};

export default SentimentPieChart;

import { useRef, useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import locale from "../locale/en.json";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function ConfidenceBarChart({ confidenceData }) {
  const chartRef = useRef(null);
  const [chartData, setChartData] = useState({
    labels: [
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
    ],
    datasets: [
      {
        label: locale.confidenceChart.label,
        data: confidenceData,
        backgroundColor: "rgba(54, 162, 235, 0.5)",
        borderWidth: 1,
      },
    ],
  });

  useEffect(() => {
    setChartData((prevData) => ({
      ...prevData,
      datasets: [
        {
          ...prevData.datasets[0],
          data: confidenceData,
        },
      ],
    }));
  }, [confidenceData]);

  return (
    <div>
      <Bar
        ref={chartRef}
        data={chartData}
        options={{
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
              },
            },
          },
          maintainAspectRatio: false,
        }}
      />
    </div>
  );
}

export default ConfidenceBarChart;

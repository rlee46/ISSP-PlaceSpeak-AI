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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function BarChart({ labels, datasetLabel, data, backgroundColor }) {
  const chartRef = useRef(null);
  const [chartData, setChartData] = useState({
    labels: labels,
    datasets: [
      {
        label: datasetLabel,
        data: data,
        backgroundColor:
          backgroundColor ||
          `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${
            Math.random() * 255
          }, 0.5)`,
        borderWidth: 1,
      },
    ],
  });

  // Effect for updating chart data when data changes
  useEffect(() => {
    setChartData((prevData) => ({
      ...prevData,
      datasets: [
        {
          ...prevData.datasets[0],
          data: data,
          backgroundColor: prevData.datasets[0].backgroundColor, // Maintain color consistency on data update
        },
      ],
    }));
  }, [data]);

  // Chart options
  const options = {
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
    maintainAspectRatio: false,
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: datasetLabel,
      },
    },
  };

  return (
    <div>
      <Bar ref={chartRef} data={chartData} options={options} />
    </div>
  );
}

export default BarChart;

import React, { useRef } from "react";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
} from "chart.js";

ChartJS.register(Tooltip, Legend, ArcElement, CategoryScale);

const PieChart = ({ data, labels }) => {
  const chartRef = useRef(null);

  const generateColor = (opacity) => {
    const randomColor = () => Math.floor(Math.random() * 255);
    return `rgba(${randomColor()}, ${randomColor()}, ${randomColor()}, ${opacity})`;
  };

  const backgroundColors = data.map(() => generateColor(0.6));
  const borderColors = backgroundColors.map((color) =>
    color.replace("0.6", "1")
  );

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: "Dataset Label",
        data: data,
        backgroundColor: backgroundColors,
        borderColor: borderColors,
        borderWidth: 1,
      },
    ],
  };

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

export default PieChart;

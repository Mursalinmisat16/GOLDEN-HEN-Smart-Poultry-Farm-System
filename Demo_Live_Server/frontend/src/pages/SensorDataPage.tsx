import { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Title, Tooltip, Legend);

function SensorDataPage() {
  const [data, setData] = useState([]);
  const [predictedCrop, setPredictedCrop] = useState('');

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/data/read/1')
      .then(res => setData(res.data.reverse()))
      .catch(err => console.error('Error fetching data:', err));
  }, []);

  const handlePredict = () => {
    axios.get('http://127.0.0.1:8000/predict/1')
      .then(res => setPredictedCrop(res.data.predicted_crop))
      .catch(err => {
        console.error('Prediction error:', err);
        setPredictedCrop('Prediction failed');
      });
  };

  const labels = data.map(entry => new Date(entry.time).toLocaleTimeString());

  const getLineChartData = (label, key) => ({
    labels,
    datasets: [
      {
        label,
        data: data.map(entry => entry[key]),
        borderColor: 'rgb(59 130 246)', // Tailwind blue-500
        backgroundColor: 'rgba(59, 130, 246, 0.3)',
        tension: 0.3,
        fill: true,
      }
    ]
  });

  const sensorKeys = [
    { label: "Temperature (°C)", key: "temperature" },
    { label: "pH Level", key: "pH" },
    { label: "Rainfall (mm)", key: "rain" },
    { label: "Humidity (%)", key: "humidity" },
    { label: "Soil Moisture", key: "soil_moisture" },
    { label: "Nitrogen (N)", key: "N" },
    { label: "Phosphorus (P)", key: "P" },
    { label: "Potassium (K)", key: "K" }
  ];

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      {/* 🔷 Project Title */}
      <h1 className="text-4xl font-bold text-center text-green-600 mb-3">
        Smart Crop Recommendation System
      </h1>
      <p className="text-center text-gray-600 text-md mb-6">
        Based on real-time sensor data using FastAPI & React
      </p>

      {/* 🟢 Predict Button */}
      <div className="flex justify-center mb-6">
        <button
          onClick={handlePredict}
          className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-emerald-600 hover:to-green-500 text-white px-6 py-2 rounded-full shadow-md font-semibold transition duration-300 cursor-pointer"
        >
          PREDICT
        </button>
      </div>

      {/* 🌾 Predicted Crop Output */}
      {predictedCrop && (
        <div className="text-center mb-8">
          <p className="text-xl font-semibold text-gray-700">
            ✅ Recommended Crop: <span className="text-green-600">{predictedCrop}</span>
          </p>
        </div>
      )}
        <h2 className="text-3xl font-bold text-center mb-8 text-blue-600">Sensor Data Visualization</h2>
      {/* Table */}
      <div className="overflow-auto mb-10 shadow-lg rounded-lg bg-white">
        <table className="table-auto w-full text-sm text-left border border-gray-200">
          <thead className="bg-blue-500 text-white">
            <tr>
              <th className="p-2">Time</th>
              {sensorKeys.map((sensor) => (
                <th key={sensor.key} className="p-2">{sensor.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((entry, i) => (
              <tr key={i} className="border-t hover:bg-blue-50">
                <td className="p-2">{new Date(entry.time).toLocaleString()}</td>
                {sensorKeys.map(sensor => (
                  <td key={sensor.key} className="p-2">{entry[sensor.key]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Graphs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {sensorKeys.map(sensor => (
          <div key={sensor.key} className="bg-white p-4 rounded-xl shadow-md">
            <h3 className="text-lg font-semibold mb-2 text-gray-700">{sensor.label}</h3>
            <Line data={getLineChartData(sensor.label, sensor.key)} options={{
              responsive: true,
              plugins: {
                legend: { display: false }
              },
              scales: {
                x: {
                  ticks: {
                    maxRotation: 90,
                    minRotation: 45
                  }
                }
              }
            }} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default SensorDataPage;

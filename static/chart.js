const charts = {};

function createChart(ctxId, label, color, suggestedMin, suggestedMax) {
  const ctx = document.getElementById(ctxId).getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label,
        data: [],
        borderColor: color,
        borderWidth: 2,
        fill: false,
        tension: 0.3,
      }]
    },
    options: {
      animation: false,
      responsive: true,
      scales: {
        x: { display: false },
        y: {
          suggestedMin,
          suggestedMax,
          title: {
            display: true,
            text: label
          }
        }
      }
    }
  });
}

window.onload = () => {
  charts.accel = createChart('accelChart', '|A| (가속도)', 'red', 0.5, 1.5);
  charts.gyro = createChart('gyroChart', '|G| (자이로)', 'blue', 0, 20);
  charts.pitch = createChart('pitchChart', 'Pitch (°)', 'green', -90, 90);
  charts.roll = createChart('rollChart', 'Roll (°)', 'orange', -90, 90);
  charts.moisture = createChart('moistureChart', '수분 (%)', 'purple', 0, 1023);
  charts.temp = createChart('tempChart', '지온 (℃)', 'brown', -10, 50);

  setInterval(fetchAndUpdate, 1000);
};

function fetchAndUpdate() {
  fetch('/sensor')
    .then(res => res.json())
    .then(data => {
      const now = new Date().toLocaleTimeString();

      updateChart(charts.accel, now, data.A);
      updateChart(charts.gyro, now, data.G);
      updateChart(charts.pitch, now, data.N[0]);
      updateChart(charts.roll, now, data.N[1]);
      updateChart(charts.moisture, now, data.M);
      updateChart(charts.temp, now, data.T);
    });
}

function updateChart(chart, label, value) {
  chart.data.labels.push(label);
  chart.data.datasets[0].data.push(value);

  if (chart.data.labels.length > 30) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
  }

  chart.update();
}

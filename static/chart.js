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

document.addEventListener("DOMContentLoaded", () => {
  charts.accel = createChart('accelChart', '|A| (가속도)', 'red', 0.5, 1.5);
  charts.gyro = createChart('gyroChart', '|G| (자이로)', 'blue', 0, 20);
  charts.pitch = createChart('pitchChart', 'Pitch (°)', 'green', -90, 90);
  charts.roll = createChart('rollChart', 'Roll (°)', 'orange', -90, 90);
  charts.moisture = createChart('moistureChart', '수분 (%)', 'purple', 0, 1023);
  charts.temp = createChart('tempChart', '지온 (℃)', 'brown', -10, 50);

  setInterval(fetchAndUpdate, 1000);
});

function fetchAndUpdate() {
  console.log("✅ fetchAndUpdate 실행됨");
  fetch('/sensor')
    .then(res => res.json())
    .then(data => {
      if (!data || data.a === undefined || data.g === undefined || !Array.isArray(data.n)) {
        console.warn("❗ 데이터 형식 오류", data);
        return;
      }

      const sum = data.a + data.g + data.n[0] + data.n[1] + data.m + data.t;
      if (sum === 0) {
        console.warn("❗ 데이터가 모두 0임", data);
        return;
      }

      const now = new Date().toLocaleTimeString();

      updateChart(charts.accel, now, data.a);
      updateChart(charts.gyro, now, data.g);
      updateChart(charts.pitch, now, data.n[0]);
      updateChart(charts.roll, now, data.n[1]);
      updateChart(charts.moisture, now, data.m);
      updateChart(charts.temp, now, data.t);
    })
    .catch(err => {
      console.error("❌ /sensor fetch 실패", err);
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

let dangerCount = 0;

async function updateRisk() {
  console.log("📡 updateRisk 호출됨");  // 호출 확인

  try {
    const response = await fetch('/risk', { cache: "no-cache" });
    const data = await response.json();
    const level = parseInt(data.label);  // 혹시 문자열일 수도 있음
    const score = data.risk;

    console.log(`📊 level: ${level}, dangerCount (이전): ${dangerCount}`);

    let labelText = "알 수 없음";
    let color = "gray";

    if (level === 0) { labelText = "매우 낮음"; color = "blue"; }
    else if (level === 1) { labelText = "낮음"; color = "green"; }
    else if (level === 2) { labelText = "보통"; color = "goldenrod"; }
    else if (level === 3) { labelText = "높음"; color = "orange"; }
    else if (level === 4) { labelText = "매우 높음"; color = "red"; }

    if (level >= 3) dangerCount++;
    else dangerCount = 0;

    console.log(`⚠️ dangerCount (현재): ${dangerCount}`);

    document.getElementById("riskDisplay").innerHTML = `
      🌡️ 위험도 점수: <b>${score.toFixed(2)}</b><br>
      🛑 등급: <b style="color:${color};">${labelText}</b>
    `;

    const dangerEl = document.getElementById("riskStreak");
    if (dangerCount >= 3) {
      dangerEl.innerHTML = `⚠️ 위험 등급 ‘<b style="color:${color}">${labelText}</b>’ 이상 상태가 <b>${dangerCount}회 연속</b> 지속 중입니다.`;
    } else {
      dangerEl.innerHTML = "";
    }

  } catch (e) {
    console.error("❌ 위험도 fetch 오류:", e);
    document.getElementById("riskDisplay").textContent = "❌ 위험도 데이터 없음";
    document.getElementById("riskStreak").textContent = "";
  }
}

updateRisk();
setInterval(updateRisk, 2000);

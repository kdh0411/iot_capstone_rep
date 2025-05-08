function loadCCTV() {
    const lat = 35.3369444 ;     // 예시 GPS 위도
    const lon = 127.7305555;   // 예시 GPS 경도
  
    fetch(`/cctv?lat=${lat}&lon=${lon}`)
      .then(res => res.json())
      .then(data => {
        if (data.cctv_url) {
          document.getElementById("cctv_frame").src = data.cctv_url;
        } else {
          alert("CCTV 정보 없음: " + (data.error || "알 수 없음"));
        }
      });
  }
  
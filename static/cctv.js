let cctvList = [];
let currentIndex = 0;

// 30초마다 CCTV 리스트 요청
function loadCCTVList() {
  const lat = 37.63696;
  const lon = 128.49502;

  fetch(`/cctv?lat=${lat}&lon=${lon}`)
    .then(res => res.json())
    .then(data => {
      if (data.cctv_urls && data.cctv_urls.length > 0) {
        cctvList = data.cctv_urls;
        currentIndex = 0;
        updateCCTVFrame(); // 즉시 첫 화면 표시
      } else {
        console.warn("CCTV 리스트 없음", data);
      }
    })
    .catch(err => {
      console.error("CCTV 요청 실패", err);
    });
}

// 10초마다 영상 전환
function updateCCTVFrame() {
  if (cctvList.length === 0) return;

  const frame = document.getElementById("cctv_frame");
  frame.src = cctvList[currentIndex];
  currentIndex = (currentIndex + 1) % cctvList.length;
}

// 초기 실행
window.onload = function () {
  loadCCTVList();                          // 최초 요청
  setInterval(loadCCTVList, 30000);        // 30초마다 CCTV URL 갱신
  setInterval(updateCCTVFrame, 5000);  // 5초마다 전환
   // 10초마다 전환
};

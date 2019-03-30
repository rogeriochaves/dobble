const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");
const result = document.getElementById("result");
const debugInfo = document.getElementById("debug-info");
const clickArea = document.getElementById("click-area");
const autoShot = document.getElementById("auto-shot");
let auto = false;

navigator.mediaDevices
  .getUserMedia({ video: { facingMode: "environment" } })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(err => alert(err));

let start;
let loading = false;
const shoot = () => {
  start = performance.now();
  loading = true;
  debugInfo.textContent = "Loading...";

  canvas.width = video.videoWidth / 2;
  canvas.height = video.videoHeight / 2;
  canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
  // const img = canvas.toDataURL("image/png");
  const img = canvas.toDataURL("image/jpeg", 0.6).split(",")[1];

  uploadImage(img);
};

clickArea.addEventListener("click", shoot);

autoShot.addEventListener("change", function() {
  auto = !auto;
  if (auto && !loading) {
    shoot();
  }
});

const uploadImage = img => {
  let req = new XMLHttpRequest();
  let formData = new FormData();

  formData.append("photo", img);
  req.open("POST", "/predict");
  req.send(formData);

  req.onload = function() {
    loading = false;
    if (req.status >= 200 && req.status < 400) {
      const predictions = JSON.parse(req.responseText).predictions;
      const formatted = predictions
        .map(p => `${p.key}: ${p.chances}`)
        .join("<br />");

      const end = performance.now();
      const wallclock = Math.round((end - start) / 10) / 100;
      if (predictions[0] && predictions[0].chances.length > 1) {
        result.innerHTML = predictions[0].key;
      } else {
        result.innerHTML = "";
      }
      debugInfo.innerHTML = formatted + "<br/>time:" + wallclock + " seconds";
    } else {
      debugInfo.innerHTML = "Error";
    }
    if (auto) shoot();
  };

  req.onerror = function() {
    loading = false;
    debugInfo.innerHTML = "Error";
    if (auto) shoot();
  };
};

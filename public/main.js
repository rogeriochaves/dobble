const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");
const result = document.getElementById("result");

navigator.mediaDevices
  .getUserMedia({ video: { facingMode: "environment" } })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(err => alert(err));

let start;
video.addEventListener("click", function() {
  start = performance.now();
  result.textContent = "Loading...";

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
  // const img = canvas.toDataURL("image/png");
  const img = canvas.toDataURL("image/jpeg", 0.9).split(",")[1];

  uploadImage(img);
});

const uploadImage = img => {
  let req = new XMLHttpRequest();
  let formData = new FormData();

  formData.append("photo", img);
  req.open("POST", "/predict");
  req.send(formData);

  req.onload = function() {
    if (req.status >= 200 && req.status < 400) {
      const predictions = JSON.parse(req.responseText).predictions;
      const formatted = predictions
        .map(p => `${p.key}: ${p.chances}`)
        .join("<br />");

      const end = performance.now();
      const wallclock = Math.round((end - start) / 10) / 100;
      result.innerHTML = formatted + "<br/>time:" + wallclock + " seconds";
    } else {
      // We reached our target server, but it returned an error
    }
  };
};

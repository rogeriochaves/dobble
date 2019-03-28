const takePicture = document.querySelector("#take-picture");
takePicture.onchange = function(event) {
  if (event.target.files.length <= 0) return;
  const photo = event.target.files[0];
  document.getElementById("result").textContent = "Loading...";

  let req = new XMLHttpRequest();
  let formData = new FormData();

  formData.append("photo", photo);
  req.open("POST", "/predict");
  req.send(formData);

  req.onload = function() {
    if (req.status >= 200 && req.status < 400) {
      // Success!
      var data = JSON.parse(req.responseText);
      document.getElementById("result").textContent = req.responseText;
    } else {
      // We reached our target server, but it returned an error
    }
  };
};

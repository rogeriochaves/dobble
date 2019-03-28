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
};

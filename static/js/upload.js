// upload.js — drag-and-drop + local preview for index.html

document.addEventListener("DOMContentLoaded", () => {
  const dz = document.getElementById("dz");
  const fi = document.getElementById("fi");
  const lp = document.getElementById("lprev");
  const pi = document.getElementById("pimg");
  const form = document.getElementById("predForm");
  const btn = document.getElementById("predBtn");

  if (!dz) return;

  function showPreview(file) {
    if (!file.type.startsWith("image/")) {
      alert("Please upload a valid image file (e.g., JPG, PNG).");
      fi.value = "";
      return;
    }
    const r = new FileReader();
    r.onload = (e) => {
      pi.src = e.target.result;
      lp.style.display = "block";
    };
    r.onerror = () => {
      alert("Could not read the file. It may be corrupted.");
      lp.style.display = "none";
    };
    r.readAsDataURL(file);
  }

  fi.addEventListener("change", (e) => {
    if (e.target.files[0]) showPreview(e.target.files[0]);
  });

  dz.addEventListener("dragover", (e) => {
    e.preventDefault();
    dz.classList.add("over");
  });
  dz.addEventListener("dragleave", () => dz.classList.remove("over"));
  dz.addEventListener("drop", (e) => {
    e.preventDefault();
    dz.classList.remove("over");
    const f = e.dataTransfer.files[0];
    if (f) {
      fi.files = e.dataTransfer.files;
      showPreview(f);
    }
  });

  // Show loading state while model runs
  form.addEventListener("submit", () => {
    btn.disabled = true;
    btn.innerHTML = "🧠 Predicting...";
  });
});

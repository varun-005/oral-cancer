document.addEventListener("DOMContentLoaded", () => {
  const dz = document.getElementById("dz");
  const fi = document.getElementById("fi");
  const lp = document.getElementById("lprev");
  const pi = document.getElementById("pimg");

  if (!dz) return; // Don't run if the elements aren't on the page

  function showPrev(file) {
    const r = new FileReader();
    r.onload = (e) => {
      pi.src = e.target.result;
      lp.style.display = "block";
    };
    r.onerror = () => {
      alert("Error: Could not read the selected file. It may be corrupted.");
      lp.style.display = "none";
    };
    r.readAsDataURL(file);
  }
  fi.addEventListener("change", (e) => {
    if (e.target.files[0]) showPrev(e.target.files[0]);
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
      showPrev(f);
    }
  });

  const form = document.getElementById("predForm");
  const btn = document.getElementById("predBtn");
  form.addEventListener("submit", () => {
    btn.disabled = true;
    btn.innerHTML = "🧠 Predicting...";
  });
});

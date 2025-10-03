// same-origin
const backendURL = "";

// ---- elements
const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const dropZone = document.getElementById("dropZone");
const dzFileName = document.getElementById("dzFileName");
const originalEl = document.getElementById("original");
const processedEl = document.getElementById("processed");
const processBtn = document.getElementById("processBtn");
const downloadBtn = document.getElementById("downloadBtn");

// Inline status elements (under images)
const statusBox  = document.getElementById("statusInline");
const statusIcon = document.getElementById("statusIcon");
const statusText = document.getElementById("statusText");
let statusTimer  = null;

// ---- inline status helpers
function showStatus(type, icon, text, autohideMs = null) {
  if (!statusBox) return;
  clearTimeout(statusTimer);
  statusBox.className = `status-inline ${type}`; // "info" | "success" | "error"
  statusIcon.textContent = icon || "";
  statusText.textContent = text || "";
  if (autohideMs) statusTimer = setTimeout(hideStatus, autohideMs);
}
function hideStatus() {
  if (!statusBox) return;
  statusBox.className = "status-inline";
  statusIcon.textContent = "";
  statusText.textContent = "";
}

// ---- img helpers
function setImage(imgEl, src) {
  if (!src) { imgEl.removeAttribute("src"); imgEl.classList.remove("show"); return; }
  imgEl.classList.remove("show");
  imgEl.onload = () => imgEl.classList.add("show");
  imgEl.onerror = () => imgEl.classList.remove("show");
  imgEl.src = src;
}

// ---- file validation
const ALLOWED_MIME = new Set(["image/jpeg","image/png"]);
const ALLOWED_EXT  = new Set([".jpg",".jpeg",".png"]);
let selectedFile = null;
let processedB64 = null;

function extOf(name){ const m=/\.[^.]+$/.exec(name||""); return m?m[0].toLowerCase():""; }
function isAllowedFile(file){ return (file.type && ALLOWED_MIME.has(file.type)) || ALLOWED_EXT.has(extOf(file.name)); }

function setSelectedFile(file){
  if (file && !isAllowedFile(file)) {
    showStatus("error","⚠️","Formato non valido. Solo JPG/JPEG/PNG.");
    resetSelectionUI();            // resets everything so user can pick again
    return;
  }

  selectedFile = file || null;
  dzFileName && (dzFileName.textContent = selectedFile ? selectedFile.name : "Nessun file scelto");

  // clear previous result on any new (valid) selection
  processedB64 = null;
  downloadBtn.disabled = true;
  setImage(processedEl, null);

  // preview original if valid file exists
  setImage(originalEl, selectedFile ? URL.createObjectURL(selectedFile) : null);
}

function setBusy(on){
  form.classList.toggle("is-busy", on);
  [...form.elements].forEach(el => el.disabled = on && el.id !== "downloadBtn");
}

// ---- reset UI helper
function resetSelectionUI() {
  // clear state
  selectedFile = null;
  processedB64 = null;

  // clear widgets
  if (dzFileName) dzFileName.textContent = "Nessun file scelto";
  if (fileInput) fileInput.value = "";                 // IMPORTANT: allows re-selecting same file
  setImage(originalEl, null);
  setImage(processedEl, null);
  downloadBtn.disabled = true;

  // cleanup any hover style
  dropZone?.classList.remove("dragover");
}

// ---- DnD + picker
["dragenter","dragover"].forEach(evt =>
  dropZone?.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); dropZone.classList.add("dragover"); })
);
["dragleave","drop"].forEach(evt =>
  dropZone?.addEventListener(evt, e => { e.preventDefault(); e.stopPropagation(); dropZone.classList.remove("dragover"); })
);
dropZone?.addEventListener("drop", e => { const f = e.dataTransfer?.files?.[0]; setSelectedFile(f||null); });
dropZone?.addEventListener("click", () => fileInput.click());
dropZone?.addEventListener("keydown", e => { if (e.key==="Enter"||e.key===" "){ e.preventDefault(); fileInput.click(); }});
fileInput.addEventListener("change", () => setSelectedFile(fileInput.files[0]||null));

// ---- submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!selectedFile) { showStatus("error","⚠️","Seleziona o trascina un'immagine."); return; }

  const phase = [...document.querySelectorAll('input[name="phase"]')].find(r=>r.checked).value;
  const formData = new FormData(); formData.append("file", selectedFile); formData.append("phase", phase);

  setBusy(true);
  processBtn.textContent = "Elaborazione…";
  showStatus("info","⏳","Elaborazione in corso…");

  try {
    const res = await fetch(`${backendURL}/process`, { method: "POST", body: formData });
    if (!res.ok) {
      let msg = `Errore ${res.status}`; try { const err = await res.json(); if (err.detail) msg = err.detail; } catch {}
      showStatus("error","⚠️", msg);
      setImage(processedEl, null); processedB64=null; downloadBtn.disabled=true;
      return;
    }
    const data = await res.json();
    processedB64 = data.processed_image_base64;
    setImage(processedEl, `data:image/png;base64,${processedB64}`);
    downloadBtn.disabled = false;
    showStatus("success","✅","Elaborazione completata", 2500);
  } catch (err) {
    console.error(err);
    showStatus("error","⚠️","Elaborazione fallita. Verifica che il backend sia attivo.");
    setImage(processedEl, null); processedB64=null; downloadBtn.disabled=true;
  } finally {
    setBusy(false);
    processBtn.textContent = "Elabora immagine";
  }
});

// ---- download
downloadBtn.addEventListener("click", () => {
  if (!processedB64) return;
  const bin = atob(processedB64);
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  const blob = new Blob([arr], { type: "image/png" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const baseName = (selectedFile?.name || "processed").replace(/\.[^.]+$/, "");
  a.download = `${baseName}_elaborata.png`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});

// initial UI
setSelectedFile(null);
---
title: Medical Simulator Demo
emoji: 🩺
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Medical Simulator Demo

A simple demo project combining **FastAPI** (backend) and a small **HTML/CSS/JS frontend**  to simulate CT-slice phase processing (**arterial** vs **venous**).  
---

## 🚀 Features
- Upload a CT-slice image (`.jpg` / `.png`)
- Simulate **arterial phase** (contrast + sharpening)
- Simulate **venous phase** (smoothing / blur)
- Preview **original (left)** and **processed (right)** images
- Status messages with icons (⏳ processing, ✅ done, ⚠️ error)
- Download processed results (Not requested - Extra feature)

---

## 🐳 Run with Docker (If you have docker installed)

```bash
docker compose up --build
```

👉 Open [http://127.0.0.1:7860](http://127.0.0.1:7860)

This setup mounts your local files (`backend/`, `frontend/`, `main.py`) into the container,  
so changes are reflected instantly without rebuilding.

---
## 🛠️ Run locally (Python)
Recommended: use **Python 3.11** for easiest setup (avoids Pillow build issues on macOS).

```bash
# create and activate venv
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run FastAPI server
python main.py
```

👉 Open [http://127.0.0.1:7860](http://127.0.0.1:7860)

---

## 📂 Project Structure
```
medical-simulator-demo/
│
├── backend/         # FastAPI backend (API + image processing)
│   ├── app.py
│   ├── processing.py
│
├── frontend/        # Simple static frontend
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── main.py          # Entrypoint for FastAPI (uvicorn)
├── requirements.txt # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

## 📂Testing with Python client (Optional)
For quick testing without the browser, a helper script client_process.py is included. It uploads an image to the backend and saves the processed result. To use this script, you should have the main.py running in the background. Place your input image in the root and:

```
# arterial phase example
python client_process.py --image CTA_Slice.jpg --phase arterial --out arterial.png

# venous phase example
python client_process.py --image CTA_Slice.jpg --phase venous --out venous.png
```

---

## ✨ How to Use
1. Open the web UI in your browser. Open [http://127.0.0.1:7860](http://127.0.0.1:7860)
2. Drag & drop or select an image (`.jpg`/`.png`).
3. Choose phase: **Arteriosa** or **Venosa**.
4. Click *Elabora immagine*.
5. ⏳ Status shows *Processing…*  
   ✅ On success: *Elaborazione completata*.  
6. Download your processed result.
7. You can always find the log file in your root folder "backend.log".


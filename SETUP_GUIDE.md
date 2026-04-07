# 🌊 Flood Prediction Platform — Setup Guide (Any PC)

---

## ✅ Step 1 — Install Python

1. Go to 👉 https://www.python.org/downloads/
2. Download **Python 3.10 or newer**
3. Run the installer
4. ⚠️ **IMPORTANT:** On the first screen, check the box **"Add Python to PATH"**
5. Click **Install Now**

Verify installation — open PowerShell and run:
```powershell
python --version
```
You should see something like `Python 3.12.x`

---

## ✅ Step 2 — Copy the Project Folder

Copy the entire `Flood_Prediction_system` folder to the new PC.

> Example location: `C:\Flood_Prediction_system`

---

## ✅ Step 3 — Open PowerShell in the Project Folder

1. Open **File Explorer** and navigate to the project folder
2. Click on the address bar, type `powershell`, press **Enter**

OR open PowerShell manually and run:
```powershell
cd C:\Flood_Prediction_system
```
*(adjust path if you placed it somewhere else)*

---

## ✅ Step 4 — Create a Virtual Environment

```powershell
python -m venv .venv
```

This creates a `.venv` folder inside the project — it isolates the project's packages from the rest of the system.

---

## ✅ Step 5 — Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

You should now see `(.venv)` at the start of your prompt.

> ⚠️ **If you get an error about "execution policy"**, run this first, then retry:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## ✅ Step 6 — Install All Dependencies

```powershell
pip install -r requirements.txt
```

This installs FastAPI, Streamlit, scikit-learn, and all other required packages.
It may take 2–5 minutes depending on internet speed.

---

## ✅ Step 7 — Train the Machine Learning Model

```powershell
python train_model.py
```

This will:
- Auto-generate the flood dataset (`data/flood_dataset.csv`)
- Train the Random Forest model
- Save `models/flood_model.pkl` and `models/scaler.pkl`

Expected output at the end:
```
[✓] Training complete — ready to start backend.
```

---

## ✅ Step 8 — Start the Backend (Terminal 1)

Keep this terminal open and running:

```powershell
uvicorn backend.main:app --reload --port 8000
```

Wait until you see:
```
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

---

## ✅ Step 9 — Start the Dashboard (Terminal 2)

Open a **second PowerShell window** in the project folder, activate venv, then run:

```powershell
.\.venv\Scripts\Activate.ps1
cd frontend
streamlit run app.py
```

The browser will automatically open at:
```
http://localhost:8501
```

---

## 🌐 What You'll See

| URL | What it is |
|-----|-----------|
| `http://localhost:8501` | 🌊 Flood prediction dashboard |
| `http://localhost:8000/docs` | API documentation (Swagger UI) |
| `http://localhost:8000/predict` | Raw JSON prediction result |

---

## ⚠️ Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| `python` not found | Reinstall Python and check "Add to PATH" |
| `Activate.ps1` execution policy error | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `pip install` network error | Check internet connection and retry |
| Dashboard shows "Cannot reach backend" | Make sure Terminal 1 (backend) is still running |
| `Model not found` error | Run `python train_model.py` again |
| `uvicorn` not recognized | Make sure `.venv` is activated (you should see `(.venv)`) |

---

## 📋 Quick Reference (Once Set Up)

Every time you want to run the project, open **2 terminals** and run:

**Terminal 1:**
```powershell
cd C:\Flood_Prediction_system
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2:**
```powershell
cd C:\Flood_Prediction_system
.\.venv\Scripts\Activate.ps1
cd frontend
streamlit run app.py
```

> 💡 You only need to run Steps 4–7 **once** on a new PC.  
> After that, just use the **Quick Reference** above each time.

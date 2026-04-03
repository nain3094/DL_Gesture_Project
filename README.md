#  Gesture Controlled Lecture Note Making System

Made By:
NAINA GARG, 
NISHTHA SINGH, 
RAJSEKHAR ROY

An AI-powered Deep learning system that converts lecture videos into structured notes using **speech recognition, NLP, and computer vision**, with **gesture-based video control**.

---

##  Features

*  This project supports **YouTube links & local video files**
*  **Speech-to-Text using OpenAI Whisper**
*  **GPT/LLM-based Summarization** (structured notes)
*  **Keyword Extraction**
*  **Gesture-Based Controls (MediaPipe)**

  * Play / Pause
  * Forward / Rewind
  * Volume Up/Down
  * Mute
    
*  **Export Notes as TXT and PDF**
*  **Streamlit Web App**

---

##  Project Architecture

```
Video Input (YouTube / Local)
        ↓
Audio Extraction (MoviePy)
        ↓
Speech-to-Text (Whisper)
        ↓
Chapter Detection (Sentence Transformers)
        ↓
Summarization (GPT / FLAN-T5)
        ↓
Keyword Extraction (TF-IDF)
        ↓
PDF Export
        ↓
Gesture Control (OpenCV + MediaPipe)
```

---

##  Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/nain3094/Gesture_Lec.git
cd Gesture_Lec
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

###  Run Web App (Recommended)

```bash
streamlit run app.py
```

## ✋ Gesture Controls

 -✋ **Palm** → Play/Pause
 - ✊ **Fist** → Mute
 - 👍 **Thumbs Up** → Volume +
 - 👎 **Thumbs Down** → Volume -
 - ☝️ **Index Right** → Next
 - ☝️ **Index Left** → Previous
---



## 🧠 Tech Stack

* **Computer Vision:** OpenCV, MediaPipe
* **Speech Recognition:** Whisper
* **NLP / LLM:** GPT / BART / FLAN-T5
* **ML:** Sentence Transformers, TF-IDF
* **Visualization:** NetworkX, Matplotlib
* **Backend/UI:** Streamlit

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first.

---

## 📜 License

MIT License

---

## ⭐ Support

If you found this project useful, please ⭐ the repo!

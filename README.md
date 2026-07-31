# 📘 NoteLense – AI Notes Analyzer

> **Zoom into what matters.**

NoteLense is an AI-powered study assistant that transforms notes, PDFs, documents, and images into structured study material using **Google Gemini AI**. It helps students save time by automatically generating summaries, key points, MCQs, viva questions, flashcards, and study plans.

---

## ✨ Features

- 📄 Upload PDF, DOCX, TXT, PNG, JPG & JPEG files
- 🤖 AI-powered analysis using Google Gemini
- 📝 Smart Summary Generation
- 📚 Short Notes for Quick Revision
- 🎯 Key Points Extraction
- ❓ Exam-Oriented Questions
- ✅ Multiple Choice Questions (MCQs)
- 🎤 Viva Questions with Answers
- 🧠 Flashcards for Revision
- 📅 Personalized Study Plan
- 🔍 OCR support for scanned PDFs & images (Tesseract OCR)
- 👤 User Authentication
- 💾 Save AI study guides in history
- 📱 Responsive UI

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap

### Backend
- Python
- Flask

### AI
- Google Gemini API

### OCR
- Tesseract OCR
- pdf2image
- Pillow

### Database
- MySQL

### Deployment
- Render
- Gunicorn

---

## 📂 Supported File Types

- PDF
- Scanned PDF
- DOCX
- TXT
- PNG
- JPG
- JPEG

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/mayursingh24/SD_mayur_0090.git
cd SD_mayur_0090
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file.

```env
GEMINI_API_KEY=YOUR_API_KEY

DB_HOST=YOUR_DATABASE_HOST
DB_PORT=3306
DB_USER=YOUR_DATABASE_USER
DB_PASSWORD=YOUR_DATABASE_PASSWORD
DB_NAME=YOUR_DATABASE_NAME
```

### Run

```bash
python app.py
```

---

## 🌐 Deployment

The application is configured for deployment on **Render** using **Gunicorn**.

Start Command

```bash
gunicorn app:app
```

---

## 📁 Project Structure

```
NoteLense/
│
├── app.py
├── requirements.txt
├── runtime.txt
├── .env
│
├── templates/
├── static/
│
├── uploads/
├── README.md
└── LICENSE
```

---

## 📸 Workflow

1. User uploads notes.
2. Text is extracted.
3. OCR is applied when needed.
4. Gemini AI analyzes the content.
5. Study material is generated.
6. Results can be saved to history.

---

## 👨‍💻 Developer

**Mayur Kumar Singh**

B.Tech CSE (AI & ML)

Shri Ramswaroop Memorial College of Engineering and Management (SRMCEM)

Lucknow, Uttar Pradesh

---

## 🙏 Acknowledgements

- Google Gemini AI
- Flask
- Tesseract OCR
- Render
- SRDT
- Guidance by **Mr. Suryamani Sir**

---

## 📜 License

This project is developed for educational and learning purposes.

---

⭐ If you like this project, consider giving the repository a star.

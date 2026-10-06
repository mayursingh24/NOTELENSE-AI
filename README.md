<div align="center">

<img src="static/images/logo.png" alt="NoteLense Logo" width="120"/>

# 🔬 NoteLense — AI Notes Analyzer
### *Zoom into what matters*

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.2-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-8A2BE2?style=for-the-badge&logo=google)](https://ai.google.dev)
[![MySQL](https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge&logo=mysql)](https://mysql.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=for-the-badge&logo=railway)](https://railway.app)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render)](https://render.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**NoteLense** is an AI-powered study assistant that transforms your raw notes into structured, exam-ready study material — in seconds. Powered by **Google Gemini AI**, it reads PDFs, DOCX, TXT, and even scanned images, then generates summaries, MCQs, flashcards, viva questions, study plans, and much more.

[🚀 Live Demo](https://notelense-ai-production.up.railway.app/) &nbsp;|&nbsp; [📦 GitHub Repo](https://github.com/mayursingh24/NOTELENSE-AI) &nbsp;|&nbsp; [🐛 Report Bug](https://github.com/mayursingh24/NOTELENSE-AI/issues)

</div>

---

## 📸 Preview

| Home Page | Upload & Analyze | AI Study Dashboard |
|:---------:|:----------------:|:-----------------:|
| Hero section with feature highlights | Drag & drop file upload | Full Gemini AI generated study guide |

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🔄 User Flow](#-user-flow)
- [📊 System Flowchart](#-system-flowchart)
- [🗂️ Project Structure](#️-project-structure)
- [🛠️ Tech Stack](#️-tech-stack)
- [⚙️ Installation & Setup](#️-installation--setup)
- [🔑 Environment Variables](#-environment-variables)
- [🐳 Docker Deployment](#-docker-deployment)
- [🚂 Deploy on Railway](#-deploy-on-railway)
- [☁️ Deploy on Render](#️-deploy-on-render)
- [🧪 Running Tests](#-running-tests)
- [📂 API Reference](#-api-reference)
- [👥 Team](#-team)
- [📄 License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📖 **AI Summary** | Concise, meaningful summary of your notes |
| ⭐ **Key Points** | Auto-extracted most important concepts |
| 📝 **Short Notes** | Quick revision-friendly condensed notes |
| 📚 **Detailed Explanation** | In-depth breakdown of all topics |
| 🎯 **Exam Important Topics** | AI identifies what matters most for exams |
| ❓ **MCQs with Answers** | 5+ practice multiple-choice questions |
| 🎤 **Viva Questions** | Interview-style Q&A with model answers |
| 🧠 **Flashcards** | Term/definition pairs for active recall |
| ⚡ **Quick Revision Sheet** | Last-minute exam cheat sheet |
| 📅 **Study Plan** | Day-wise personalized revision roadmap |
| 📖 **Important Definitions** | All key terms defined clearly |
| 🔢 **Formulas & Concepts** | Auto-detected formulas (for STEM subjects) |
| 💬 **FAQs** | Frequently asked questions on the topic |
| 🔍 **OCR Support** | Reads scanned PDFs and images via Tesseract |
| 🔐 **User Auth** | Signup / Login with session management |
| 📜 **Analysis History** | All your analyses saved per account |
| 🔄 **Local Fallback** | Works even if Gemini API is unavailable |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                        FRONTEND                          │
│   HTML5 + CSS3 + Vanilla JS + Marked.js + KaTeX         │
│   Templates: index, login, signup, profile, history      │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP (Flask Routes)
┌────────────────────────▼─────────────────────────────────┐
│                    FLASK BACKEND                         │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Auth      │  │  File Upload │  │   /analyze     │  │
│  │  (session)  │  │  Validation  │  │   Route        │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘  │
│         │                │                   │           │
│  ┌──────▼──────┐  ┌──────▼───────────────────▼────────┐  │
│  │   MySQL DB  │  │         Text Extraction Engine     │  │
│  │  (users +   │  │  PDF → PyPDF2 → OCR (if scanned)  │  │
│  │   history)  │  │  DOCX → python-docx               │  │
│  └─────────────┘  │  TXT  → plain read                │  │
│                   │  IMG  → Tesseract OCR              │  │
│                   └─────────────┬────────────────────── ┘  │
│                                 │                          │
│                   ┌─────────────▼──────────────────────┐  │
│                   │       Google Gemini AI              │  │
│                   │  (gemini-3.5-flash via google-genai)│  │
│                   │  Fallback: Local generator          │  │
│                   └────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │   External Services  │
              │  • Google Gemini API │
              │  • MySQL (optional)  │
              │  • Tesseract OCR     │
              │  • Poppler (PDF→img) │
              └─────────────────────┘
```

---

## 🔄 User Flow

```
┌─────────────┐
│    USER     │
│   Visits    │
│  NoteLense  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────┐
│  Is user logged in?          │
└──────────┬───────────────────┘
           │
     ┌─────┴──────┐
     │            │
    YES           NO
     │            │
     ▼            ▼
┌─────────┐  ┌──────────────────┐
│ Go to   │  │  Signup / Login  │
│ Upload  │  │   Page           │
│ Section │  └────────┬─────────┘
└────┬────┘           │
     │         ┌──────▼────────┐
     │         │ Auth Success? │
     │         └──────┬────────┘
     │                │
     │           ┌────┴────┐
     │           │         │
     │          YES        NO
     │           │         │
     │           ▼         ▼
     │    ┌──────────┐ ┌────────────┐
     │    │ Session  │ │Show Error  │
     │    │ Created  │ │Flash Msg   │
     │    └────┬─────┘ └────────────┘
     │         │
     └────┬────┘
          │
          ▼
┌─────────────────────┐
│  Upload Notes File  │
│  (PDF/DOCX/TXT/IMG) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  File Validation    │
│  • Extension check  │
│  • Size ≤ 20 MB     │
└──────────┬──────────┘
           │
     ┌─────┴──────┐
     │            │
   Valid       Invalid
     │            │
     ▼            ▼
┌─────────┐  ┌───────────────┐
│  Save   │  │ Return Error  │
│  File   │  │   to User     │
│Securely │  └───────────────┘
└────┬────┘
     │
     ▼
┌─────────────────────────────┐
│     Text Extraction         │
│                             │
│  PDF ──► PyPDF2             │
│         └─(no text?)──►OCR  │
│  DOCX ──► python-docx       │
│  TXT  ──► file.read()       │
│  IMG  ──► Tesseract OCR     │
└──────────────┬──────────────┘
               │
         ┌─────┴──────┐
         │            │
      Got Text    No Text
         │            │
         ▼            ▼
┌────────────┐  ┌────────────────┐
│Send to     │  │Return Error:   │
│Gemini AI   │  │"Low quality    │
│            │  │ scan / no text"│
└─────┬──────┘  └────────────────┘
      │
      ▼
┌──────────────────────────────┐
│   Gemini API Call            │
│   (gemini-3.5-flash)         │
│   Prompt: 13-section guide   │
└──────────────┬───────────────┘
               │
         ┌─────┴──────┐
         │            │
      Success       Failure
         │            │
         ▼            ▼
┌────────────┐  ┌──────────────────┐
│  Return AI │  │ Local Fallback   │
│  Result    │  │ Generator        │
│            │  │ (basic summary)  │
└─────┬──────┘  └──────┬───────────┘
      │                │
      └────────┬───────┘
               │
               ▼
┌──────────────────────────────┐
│  Save to Analysis History    │
│  (MySQL, if user logged in)  │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Render Result on Dashboard  │
│  • Markdown rendered         │
│  • KaTeX for formulas        │
│  • Copy / Print options      │
└──────────────────────────────┘
```

---

## 📊 System Flowchart

```
                    ┌─────────────────┐
                    │   Client Browser │
                    └────────┬────────┘
                             │ HTTP Request
                    ┌────────▼────────┐
                    │   Flask Server  │
                    │  (Gunicorn)     │
                    └──┬──────────┬───┘
                       │          │
            ┌──────────▼──┐  ┌────▼───────────┐
            │  Auth Routes │  │  /analyze POST │
            │  /login      │  └────────┬───────┘
            │  /signup     │           │
            │  /logout     │  ┌────────▼───────┐
            │  /profile    │  │ File Validator  │
            │  /history    │  └────────┬───────┘
            └──────┬───────┘           │
                   │          ┌────────▼───────┐
            ┌──────▼──────┐   │Text Extraction │
            │  MySQL DB   │   │  Engine        │
            │ ┌─────────┐ │   └────────┬───────┘
            │ │  users  │ │            │
            │ └─────────┘ │   ┌────────▼───────┐
            │ ┌─────────┐ │   │ Gemini AI API  │
            │ │ history │ │   │ (or fallback)  │
            │ └─────────┘ │   └────────┬───────┘
            └─────────────┘            │
                   ▲           ┌───────▼────────┐
                   │           │ Save to History │
                   └───────────┤   (MySQL)       │
                               └───────┬────────┘
                                       │
                               ┌───────▼────────┐
                               │  JSON Response  │
                               │  to Frontend   │
                               └────────────────┘
```

---

## 🗂️ Project Structure

```
📁 NOTELENSE-AI/
│
├── 📄 app.py                  # Main Flask application (840 lines)
├── 📄 requirements.txt        # Python dependencies
├── 📄 .env                    # Environment variables (not committed)
├── 📄 .gitignore
├── 📄 Dockerfile              # Docker container config
├── 📄 render.yaml             # Render.com deployment config
├── 📄 Procfile                # Process config (Gunicorn)
├── 📄 runtime.txt             # Python version spec
│
├── 📁 templates/              # Jinja2 HTML templates
│   ├── 📄 index.html          # Main page (Hero + Upload + Dashboard)
│   ├── 📄 login.html          # Login page
│   ├── 📄 signup.html         # Signup / Registration page
│   ├── 📄 profile.html        # User profile & stats
│   └── 📄 history.html        # Analysis history listing
│
├── 📁 static/                 # Static assets
│   ├── 📁 css/
│   │   └── 📄 style.css       # Main stylesheet
│   ├── 📁 js/                 # Frontend JavaScript
│   └── 📁 images/
│       └── 🖼️ logo.png        # NoteLense logo
│
├── 📁 uploads/                # Uploaded files (auto-cleaned)
├── 📁 poppler/                # Poppler binaries (Windows)
└── 📁 tests/
    └── 📄 test_app.py         # Unit & integration tests
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12 | Core language |
| **Flask** | 2.3.2 | Web framework |
| **Gunicorn** | 23.0.0 | WSGI server (production) |
| **Werkzeug** | 2.3.6 | WSGI utilities + password hashing |
| **python-dotenv** | 1.0.0 | Environment variable management |

### AI & Processing
| Technology | Version | Purpose |
|-----------|---------|---------|
| **google-genai** | ≥1.0.0 | Google Gemini AI SDK |
| **PyPDF2** | 3.0.1 | PDF text extraction |
| **python-docx** | ≥1.1.0 | DOCX text extraction |
| **pdf2image** | 1.16.3 | PDF → image (for OCR) |
| **pytesseract** | 0.3.10 | OCR engine wrapper |
| **Pillow** | ≥11.0.0 | Image processing |
| **Poppler** | system | PDF rendering backend |
| **Tesseract** | system | OCR engine |

### Database
| Technology | Purpose |
|-----------|---------|
| **MySQL** | User accounts + analysis history |
| **mysql-connector-python** | Python ↔ MySQL driver |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **HTML5 / CSS3** | UI structure & styling |
| **Vanilla JavaScript** | Form handling, AJAX requests |
| **Marked.js** | Markdown → HTML rendering |
| **KaTeX** | LaTeX math formula rendering |
| **Google Fonts (Poppins)** | Typography |

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.12+
- MySQL Server (optional — auth/history features only)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (for image & scanned PDF support)
- [Poppler](https://poppler.freedesktop.org/) (for PDF-to-image conversion)
- A [Google Gemini API Key](https://ai.google.dev/)

---

### 1. Clone the Repository

```bash
git clone https://github.com/mayursingh24/NOTELENSE-AI.git
cd NOTELENSE-AI
```

### 2. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

**Windows:**
- Download and install [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
- Download [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)
- Extract Poppler to `C:\poppler\` or the project `poppler/` folder

**Linux / Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash

# Flask
SECRET_KEY=your_super_secret_key_here

# MySQL (optional — skip if you don't need auth/history)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=notelense

# System paths (Windows examples — adjust as needed)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\poppler\Library\bin
```

### 6. Run the Application

```bash
python app.py
```

Open your browser and navigate to: **http://localhost:5000**

---

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | — | Your Google Gemini API key |
| `GEMINI_MODEL` | ❌ No | `gemini-3.5-flash` | Gemini model to use |
| `SECRET_KEY` | ✅ Yes | `notelense-dev-secret-key` | Flask session secret |
| `MYSQL_HOST` | ❌ No | `localhost` | MySQL server host |
| `MYSQL_PORT` | ❌ No | `3306` | MySQL port |
| `MYSQL_USER` | ❌ No | `root` | MySQL username |
| `MYSQL_PASSWORD` | ❌ No | `""` | MySQL password |
| `MYSQL_DATABASE` | ❌ No | `notelense` | MySQL database name |
| `MYSQL_CONNECTION_TIMEOUT` | ❌ No | `3` | DB connection timeout (seconds) |
| `TESSERACT_PATH` | ❌ No | auto-detected | Path to `tesseract.exe` |
| `POPPLER_PATH` | ❌ No | auto-detected | Path to Poppler `bin/` folder |

> **Note:** If MySQL is not configured, the app still works for analysis — only Login, Signup, Profile, and History features will be disabled.

---

## 🐳 Docker Deployment

### Build & Run with Docker

```bash
# Build the image
docker build -t notelense-ai .

# Run the container
docker run -d \
  -p 10000:10000 \
  -e GEMINI_API_KEY=your_key_here \
  -e SECRET_KEY=your_secret_here \
  -e MYSQL_HOST=your_mysql_host \
  -e MYSQL_USER=your_mysql_user \
  -e MYSQL_PASSWORD=your_mysql_password \
  -e MYSQL_DATABASE=notelense \
  --name notelense \
  notelense-ai
```

The app will be available at **http://localhost:10000**

### Docker Compose (with MySQL)

```yaml
version: '3.8'
services:
  notelense:
    build: .
    ports:
      - "10000:10000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - MYSQL_HOST=db
      - MYSQL_USER=notelense
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DATABASE=notelense
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=notelense
      - MYSQL_USER=notelense
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

---

## 🚂 Deploy on Railway

NoteLense is deployed live on Railway at: **[https://notelense-ai-production.up.railway.app/](https://notelense-ai-production.up.railway.app/)**

### Quick Railway Setup:
1. Log in to [railway.app](https://railway.app) with your GitHub account.
2. Click **New Project** → **Deploy from GitHub repo** → select `mayursingh24/NOTELENSE-AI`.
3. Add a **MySQL** database service:
   - Click `+ Add Service` → `Database` → `MySQL`.
4. In your `NOTELENSE-AI` service, open the **Variables** tab and set:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-flash-lite-latest
   SECRET_KEY=notelense-secret-2026
   MYSQL_HOST=${{MySQL.MYSQLHOST}}
   MYSQL_PORT=${{MySQL.MYSQLPORT}}
   MYSQL_USER=${{MySQL.MYSQLUSER}}
   MYSQL_PASSWORD=${{MySQL.MYSQLPASSWORD}}
   MYSQL_DATABASE=${{MySQL.MYSQLDATABASE}}
   TESSERACT_PATH=/usr/bin/tesseract
   POPPLER_PATH=/usr/bin
   WEB_CONCURRENCY=1
   WEB_TIMEOUT=120
   ```
5. In **Settings** → **Networking**, click **Generate Domain** (Port: `8080`).

---

## ☁️ Deploy on Render

This project is pre-configured for one-click deployment on [Render.com](https://render.com).

### Steps:
1. Fork this repository to your GitHub account
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` and configures everything
5. Set the following environment variables in Render dashboard:
   - `GEMINI_API_KEY` → Your Gemini API key
   - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` → Your MySQL credentials
6. Click **Deploy** 🚀

> **Tip:** Use [Railway](https://railway.app) or [PlanetScale](https://planetscale.com) for a free MySQL database on Render's free plan.

---

## 🧪 Running Tests

```bash
# Install test dependencies (if any)
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v
```

---

## 📂 API Reference

### `POST /analyze`
Analyze uploaded notes using Gemini AI.

**Auth Required:** ✅ Yes (session)

**Request:**
```
Content-Type: multipart/form-data
Body: notes=<file>  (PDF, DOCX, TXT, PNG, JPG — max 20MB)
```

**Success Response (200):**
```json
{
  "result": "## Summary\n...\n## MCQs\n..."
}
```

**Fallback Response (200 with warning):**
```json
{
  "result": "## Summary\n...",
  "warning": "Gemini failed. Local fallback generated.",
  "warning_detail": "Gemini quota/rate limit was reached."
}
```

**Error Response (400/401/500):**
```json
{
  "error": "Description of what went wrong."
}
```

---

### `POST /clear`
Clears all files from the uploads folder.

**Auth Required:** ❌ No

**Response (200):**
```json
{
  "message": "Uploads cleared.",
  "deleted": ["file1.pdf", "file2.jpg"]
}
```

---

### `GET /history`
View analysis history for the logged-in user.

**Auth Required:** ✅ Yes

**Response:** HTML page with history records.

---

## 📤 What Gemini AI Generates

For every uploaded file, NoteLense asks Gemini to produce **13 structured sections**:

```
 1. 📖  Summary
 2. ⭐  Important Key Points
 3. 📝  Short Notes
 4. 📚  Detailed Explanation
 5. 🎯  Exam Important Topics
 6. ❓  MCQs with Answers (≥5)
 7. 🎤  Viva Questions (≥5 with answers)
 8. 🧠  Flashcards (term/definition pairs)
 9. ⚡  Quick Revision Sheet
10. 📅  Study Plan (day-wise)
11. 📖  Important Definitions
12. 🔢  Formulas / Concepts (if applicable)
13. 💬  Frequently Asked Questions
```

---

## 🔐 Authentication Flow

```
User Signup → Hash Password (Werkzeug) → Store in MySQL
User Login  → Verify Hash → Create Flask Session
Protected Routes → @login_required decorator
Session Clear → Logout
```

---

## 👥 Team

<div align="center">

| Member | Role |
|--------|------|
| **Mayur Kumar Singh** | Lead Developer |
| **Manya Vishwakarma** | Frontend & UI |
| **Kritika Gaur** | Testing & Documentation |

**B.Tech Computer Science (AI & ML)**  
Shri Ramswaroop Memorial College of Engineering and Management (SRMCEM), Lucknow

**Guided by:** Mr. Suryamani Sir  
**Program:** SRDT Summer Training 2026

</div>

---

## 🗺️ Roadmap

- [x] File upload & text extraction (PDF, DOCX, TXT, IMG)
- [x] Google Gemini AI integration
- [x] OCR support for scanned PDFs/images
- [x] User authentication (Signup/Login/Logout)
- [x] Analysis history per user
- [x] Docker & Render deployment
- [ ] Export to PDF/Word
- [ ] Chat with your notes (Q&A mode)
- [ ] Multiple language support
- [ ] Mobile app (Flutter/React Native)
- [ ] Dark/Light theme toggle
- [ ] Batch file analysis

---

## 🤝 Contributing

Contributions are welcome! Here's how:

```bash
# 1. Fork the repo
# 2. Create a feature branch
git checkout -b feature/AmazingFeature

# 3. Commit your changes
git commit -m "Add some AmazingFeature"

# 4. Push to the branch
git push origin feature/AmazingFeature

# 5. Open a Pull Request
```

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) file for details.

---

<div align="center">

Made with ❤️ by **Mayur Kumar Singh & Team** | SRMCEM Lucknow

⭐ **Star this repo if you found it useful!** ⭐

</div>

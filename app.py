"""
NoteLense - AI Notes Analyzer
Backend: Flask + Google Gemini AI + OCR
Developer: Mayur Kumar Singh
"""

import os
import shutil
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# ---- Text extraction libraries ----
import PyPDF2
import docx
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# ---- Gemini AI ----
from google import genai

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    mysql = None
    MySQLError = Exception


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "notelense-dev-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "png", "jpg", "jpeg"}

def get_db_config():
    """Extract MySQL config supporting both standard and Railway environment variables."""
    host = os.getenv("MYSQL_HOST") or os.getenv("MYSQLHOST") or "localhost"
    port_str = os.getenv("MYSQL_PORT") or os.getenv("MYSQLPORT") or "3306"
    try:
        port = int(port_str)
    except (ValueError, TypeError):
        port = 3306
    user = os.getenv("MYSQL_USER") or os.getenv("MYSQLUSER") or "root"
    password = os.getenv("MYSQL_PASSWORD") or os.getenv("MYSQLPASSWORD") or ""
    database = os.getenv("MYSQL_DATABASE") or os.getenv("MYSQLDATABASE") or "notelense"
    timeout_str = os.getenv("MYSQL_CONNECTION_TIMEOUT", "3")
    try:
        timeout = int(timeout_str)
    except (ValueError, TypeError):
        timeout = 3

    # Support full connection string if provided (Railway/Render standard)
    db_url = os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("mysql"):
        try:
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            if parsed.hostname:
                host = parsed.hostname
            if parsed.port:
                port = parsed.port
            if parsed.username:
                user = parsed.username
            if parsed.password:
                password = parsed.password
            dbname = parsed.path.lstrip("/")
            if dbname:
                database = dbname
        except Exception:
            pass

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "connection_timeout": timeout,
    }


DB_CONFIG = get_db_config()

db_ready = False

def resolve_executable_path(executable_name, env_var_name, default_locations=None):
    """Resolve an executable path from env vars, PATH, or common install locations."""
    env_value = os.getenv(env_var_name)
    candidates = []

    if env_value:
        candidates.append(env_value)

    if os.name == "nt":
        candidates.extend([executable_name, executable_name + ".exe"])
    else:
        candidates.append(executable_name)

    for default_location in default_locations or []:
        candidates.append(default_location)

    for candidate in candidates:
        if not candidate:
            continue

        if os.path.isfile(candidate):
            return candidate

        if os.path.isdir(candidate):
            for suffix in (executable_name, executable_name + ".exe"):
                exe_path = os.path.join(candidate, suffix)
                if os.path.isfile(exe_path):
                    return exe_path

        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    return None


def resolve_poppler_path():
    """Return a Poppler bin directory, or None if pdftoppm is only on PATH/missing."""
    env_value = os.getenv("POPPLER_PATH")
    executable_name = "pdftoppm.exe" if os.name == "nt" else "pdftoppm"
    candidates = [
        env_value,
        os.path.join(BASE_DIR, "poppler", "Library", "bin"),
        os.path.join(BASE_DIR, "poppler", "bin"),
        os.path.join(BASE_DIR, "poppler"),
        r"C:\poppler\poppler-26.02.0\Library\bin",
        r"C:\poppler\Library\bin",
        r"C:\poppler\bin",
        r"C:\poppler",
    ]

    for candidate in candidates:
        if not candidate:
            continue

        if os.path.isfile(candidate):
            parent_dir = os.path.dirname(candidate)
            if os.path.basename(candidate).lower() in ("pdftoppm", "pdftoppm.exe"):
                return parent_dir

        if os.path.isdir(candidate):
            pdftoppm_path = os.path.join(candidate, executable_name)
            if os.path.isfile(pdftoppm_path):
                return candidate

    return None


TESSERACT_PATH = resolve_executable_path(
    "tesseract",
    "TESSERACT_PATH",
    default_locations=[
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ],
)

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"Tesseract configured at {TESSERACT_PATH}.")
else:
    print("WARNING: Tesseract was not found. OCR for images/scanned PDFs will be unavailable until Tesseract is installed or TESSERACT_PATH is set.")

POPPLER_PATH = resolve_poppler_path()

# Verify Poppler is accessible
if POPPLER_PATH:
    print(f"Poppler configured at {POPPLER_PATH}.")
elif shutil.which("pdftoppm"):
    print("Poppler found on PATH.")
else:
    print("WARNING: Poppler ('pdftoppm') not found. "
          "Scanned PDF OCR will fail until Poppler is properly installed or POPPLER_PATH is set.")

def resolve_model_name():
    """Return active Gemini model, automatically upgrading deprecated versions."""
    model = (os.getenv("GEMINI_MODEL") or "").strip()
    deprecated_prefixes = ("gemini-2.5", "gemini-2.0", "gemini-1.5", "gemini-3.5")
    if not model or any(model.startswith(prefix) for prefix in deprecated_prefixes):
        return "gemini-3.8-flash"
    return model


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found. The app will use the local fallback generator.")
GEMINI_MODEL = resolve_model_name()
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# HELPERS
# =========================================================

def allowed_file(filename):
    """Check whether the uploaded file has a supported extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection(use_database=True):
    """Create a MySQL connection, dynamically reading config and supporting cloud environments."""
    if mysql is None:
        raise RuntimeError("mysql-connector-python is not installed.")

    config = get_db_config()
    if not use_database:
        config.pop("database", None)

    return mysql.connector.connect(**config)


def init_database():
    """Create the NoteLense database and tables if they do not already exist."""
    global db_ready

    if mysql is None:
        print("WARNING: mysql-connector-python is not installed. MySQL features are disabled.")
        db_ready = False
        return False

    config = get_db_config()
    db_name = config.get("database", "notelense")

    # Step 1: Attempt direct connection to the database (standard on cloud providers like Railway)
    try:
        conn = get_db_connection(use_database=True)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_type VARCHAR(20) NOT NULL,
                extracted_text LONGTEXT,
                result LONGTEXT NOT NULL,
                warning VARCHAR(255),
                warning_detail TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conn.commit()
        cursor.close()
        conn.close()
        db_ready = True
        print(f"MySQL database '{db_name}' is connected and tables are verified.")
        return True
    except Exception as direct_err:
        print(f"Direct connection to database '{db_name}' not available yet ({direct_err}). Trying server-level creation...")

    # Step 2: Attempt server-level CREATE DATABASE if direct connection wasn't possible
    try:
        server_conn = get_db_connection(use_database=False)
        server_cursor = server_conn.cursor()
        server_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        server_cursor.close()
        server_conn.close()

        conn = get_db_connection(use_database=True)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_type VARCHAR(20) NOT NULL,
                extracted_text LONGTEXT,
                result LONGTEXT NOT NULL,
                warning VARCHAR(255),
                warning_detail TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conn.commit()
        cursor.close()
        conn.close()
        db_ready = True
        print(f"MySQL database '{db_name}' created and tables are ready.")
        return True
    except Exception as e:
        db_ready = False
        print(f"WARNING: MySQL setup failed ({e}). Login, profile, and history will be unavailable.")
        return False



def query_one(sql, params=None):
    """Return one row as a dictionary."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def query_all(sql, params=None):
    """Return all rows as dictionaries."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def execute_db(sql, params=None):
    """Execute a write query and return the inserted row id when available."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    conn.commit()
    lastrowid = cursor.lastrowid
    cursor.close()
    conn.close()
    return lastrowid


def login_required(view):
    """Redirect anonymous users to login for account-only pages."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            if request.path == "/analyze":
                return jsonify({
                    "error": "Please login or signup before analyzing notes."
                }), 401
            flash("Please login to continue.", "error")
            return redirect(url_for("login"))

        if current_user() is None:
            session.clear()
            if request.path == "/analyze":
                return jsonify({
                    "error": "Please login or signup before analyzing notes."
                }), 401
            flash("Please login again to continue.", "error")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view


def current_user():
    """Return the logged-in user record, if any."""
    user_id = session.get("user_id")
    if not user_id or not db_ready:
        return None

    try:
        return query_one(
            "SELECT id, name, email, created_at FROM users WHERE id = %s",
            (user_id,),
        )
    except Exception:
        return None


def save_analysis_history(filename, file_type, extracted_text, result, warning=None, warning_detail=None):
    """Persist an analysis result for the logged-in user."""
    user_id = session.get("user_id")
    if not user_id or not db_ready:
        return

    try:
        execute_db(
            """
            INSERT INTO analysis_history
                (user_id, filename, file_type, extracted_text, result, warning, warning_detail)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, filename, file_type, extracted_text, result, warning, warning_detail),
        )
    except Exception as e:
        print("History save error:", e)


def extract_text_from_pdf(filepath):
    """Extract text from a PDF. Falls back to OCR if no text layer is found."""
    text = ""

    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("PyPDF2 extraction error:", e)
        text = ""

    # If no usable text was found, treat it as a scanned PDF and run OCR
    if not text.strip():
        text = extract_text_from_scanned_pdf(filepath)

    return text


def extract_text_from_scanned_pdf(filepath):
    """Convert PDF pages to images and run OCR on each page."""
    ocr_text = ""

    if not TESSERACT_PATH:
        raise RuntimeError(
            "This PDF appears to be scanned, but Tesseract OCR is not installed. "
            "Install Tesseract or set TESSERACT_PATH to tesseract.exe."
        )

    if not POPPLER_PATH and not shutil.which("pdftoppm"):
        raise RuntimeError(
            "This PDF appears to be scanned, but Poppler is not available. "
            "Install Poppler and set POPPLER_PATH to its bin folder, for example "
            r"C:\poppler\Library\bin."
        )

    convert_kwargs = {}
    if POPPLER_PATH:
        convert_kwargs["poppler_path"] = POPPLER_PATH

    pages = convert_from_path(filepath, **convert_kwargs)
    for page_image in pages:
        page_text = pytesseract.image_to_string(page_image)
        ocr_text += page_text + "\n"

    return ocr_text


def extract_text_from_docx(filepath):
    """Extract text from a DOCX file."""
    text = ""

    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print("DOCX extraction error:", e)

    return text


def extract_text_from_txt(filepath):
    """Read text from a plain TXT file."""
    text = ""

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception as e:
        print("TXT extraction error:", e)

    return text


def extract_text_from_image(filepath):
    """Run OCR on an image file (PNG/JPG/JPEG)."""
    if not TESSERACT_PATH:
        raise RuntimeError(
            "Tesseract OCR is not installed. Install Tesseract or set TESSERACT_PATH to tesseract.exe."
        )

    image = Image.open(filepath)
    text = pytesseract.image_to_string(image)
    return text


def extract_text(filepath, ext):
    """
    Master extraction function.
    Routes the file to the correct extractor based on its extension
    and returns one combined string: extracted_text.
    """
    extracted_text = ""

    if ext == "pdf":
        extracted_text = extract_text_from_pdf(filepath)

    elif ext == "docx":
        extracted_text = extract_text_from_docx(filepath)

    elif ext == "txt":
        extracted_text = extract_text_from_txt(filepath)

    elif ext in ("png", "jpg", "jpeg"):
        extracted_text = extract_text_from_image(filepath)

    return extracted_text


def build_gemini_prompt(notes_text):
    """Builds the full study-material generation prompt for Gemini."""

    prompt = f"""
You are NoteLense, an advanced AI study assistant for students.

A student has uploaded their notes. Carefully analyze the content below and
generate a complete, well-structured study guide using proper Markdown
formatting (headings, bullet points, bold text where useful).

Produce the following sections, in this exact order:

1. **Summary**
2. **Important Key Points**
3. **Short Notes**
4. **Detailed Explanation**
5. **Exam Important Topics**
6. **MCQs with Answers** (at least 5, mark the correct option clearly)
7. **Viva Questions** (at least 5, with brief model answers)
8. **Flashcards** (term / definition pairs)
9. **Quick Revision Sheet**
10. **Study Plan** (a short day-wise plan to revise this topic)
11. **Important Definitions**
12. **Formulas / Concepts** (only if applicable to the subject matter)
13. **Frequently Asked Questions**

Base everything strictly on the notes provided below. If a section does not
apply to the subject matter (e.g. no formulas exist), briefly say so instead
of making something up.

---
NOTES:
{notes_text[:15000]}
---
"""
    return prompt


def build_local_study_material(notes_text):
    """Generate a useful study guide locally when Gemini is unavailable."""
    text = (notes_text or "").strip()
    if not text:
        return "## Summary\nNo notes were available for analysis."

    summary = text[:300].rstrip()
    key_points = []
    for sentence in text.split('.'):
        cleaned = sentence.strip()
        if cleaned:
            key_points.append(f"- {cleaned}")
            if len(key_points) >= 5:
                break

    return f"""## Summary
{summary}

## Important Key Points
{chr(10).join(key_points) if key_points else '- Review the uploaded notes carefully.'}

## Short Notes
- The uploaded material has been summarized locally because the AI service is temporarily unavailable.
- Review the original notes for detailed understanding.

## Detailed Explanation
The provided notes contain the main ideas needed for study. Use them as a base to expand on the topic with additional reading and revision.

## Exam Important Topics
- Core concepts from the uploaded notes
- Definitions and examples included in the material

## MCQs with Answers
1. What is the main topic discussed in the uploaded notes?  
   Answer: The topic is summarized from the provided content.
2. Which section should be reviewed first?  
   Answer: The summary and key points section.
3. Why is revision important?  
   Answer: It strengthens understanding and memory retention.
"""


def format_gemini_error(error):
    """Return a helpful browser-facing explanation for common Gemini failures."""
    error_text = str(error)

    if "401" in error_text or "UNAUTHENTICATED" in error_text:
        return (
            "Gemini rejected authentication. If your key starts with AQ., it may "
            "be a new Google AI Studio authorization key; these are valid, but "
            "some projects/keys can return ACCESS_TOKEN_TYPE_UNSUPPORTED. Try "
            "creating a fresh key in a new/imported AI Studio project, make sure "
            "it is restricted to Gemini API only, and keep GEMINI_MODEL set to a "
            "current model such as gemini-3.5-flash."
        )

    if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
        return "Gemini quota/rate limit was reached. Wait a bit or check your Google AI Studio quota."

    if "403" in error_text or "PERMISSION_DENIED" in error_text:
        return "Gemini access was denied. Check API key restrictions and make sure Generative Language API access is allowed."

    return error_text


def clear_uploads_folder():
    """Deletes all files inside the uploads folder."""
    deleted = []

    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                deleted.append(filename)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                deleted.append(filename)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

    return deleted


init_database()


# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def home():
    """Serves the main NoteLense frontend page."""
    return render_template("index.html", user=current_user(), db_ready=db_ready)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Create a NoteLense account."""
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        if not db_ready:
            flash("MySQL is not available. Check your database settings and try again.", "error")
            return render_template("signup.html", user=None, db_ready=db_ready)

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Name, email, and password are required.", "error")
            return render_template("signup.html", user=None, db_ready=db_ready)

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html", user=None, db_ready=db_ready)

        existing_user = query_one("SELECT id FROM users WHERE email = %s", (email,))
        if existing_user:
            flash("An account with this email already exists.", "error")
            return render_template("signup.html", user=None, db_ready=db_ready)

        password_hash = generate_password_hash(password)
        user_id = execute_db(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, password_hash),
        )
        session["user_id"] = user_id
        flash("Account created successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("signup.html", user=None, db_ready=db_ready)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an existing NoteLense user."""
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        if not db_ready:
            flash("MySQL is not available. Check your database settings and try again.", "error")
            return render_template("login.html", user=None, db_ready=db_ready)

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = query_one("SELECT * FROM users WHERE email = %s", (email,))

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html", user=None, db_ready=db_ready)

        session["user_id"] = user["id"]
        flash("Logged in successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("login.html", user=None, db_ready=db_ready)


@app.route("/logout")
def logout():
    """End the current user session."""
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    """Show account details and simple usage stats."""
    user = current_user()
    history_count = 0

    if user:
        count_row = query_one(
            "SELECT COUNT(*) AS total FROM analysis_history WHERE user_id = %s",
            (user["id"],),
        )
        history_count = count_row["total"] if count_row else 0

    return render_template(
        "profile.html",
        user=user,
        db_ready=db_ready,
        history_count=history_count,
    )


@app.route("/history")
@login_required
def history():
    """Show saved Gemini analyses for the logged-in user."""
    user = current_user()
    records = []

    if user:
        records = query_all(
            """
            SELECT id, filename, file_type, result, warning, warning_detail, created_at
            FROM analysis_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user["id"],),
        )

    return render_template("history.html", user=user, db_ready=db_ready, records=records)


@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    """
    Receives the uploaded notes file, validates it, extracts text
    (using OCR if needed), sends it to Gemini, and returns the result.
    """

    # ---- Validate file presence ----
    if "notes" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["notes"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Unsupported file type. Please upload PDF, DOCX, TXT, PNG, or JPG/JPEG."
        }), 400

    # ---- Save file securely ----
    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    try:
        file.save(filepath)
    except Exception as e:
        print("File save error:", e)
        return jsonify({"error": "Could not save the uploaded file."}), 500

    # ---- Extract text ----
    try:
        extracted_text = extract_text(filepath, ext)
    except Exception as e:
        print("Extraction error:", e)
        # Surfacing the real exception (dev/debug mode) so the actual cause is visible
        # in the browser instead of only in the terminal. Remove str(e) before deploying publicly.
        return jsonify({
            "error": f"Failed to extract text from the uploaded file. Details: {str(e)}"
        }), 500

    if not extracted_text or not extracted_text.strip():
        return jsonify({
            "error": "Text extraction ran without errors but returned nothing. "
                     "This usually means the image/scan is too low quality for OCR to read, "
                     "or the file itself has no visible text on the page."
        }), 400

    # ---- Call Gemini or fall back locally ----
    try:
        active_client = client
        if active_client is None:
            current_key = os.getenv("GEMINI_API_KEY")
            if current_key:
                active_client = genai.Client(api_key=current_key)

        if active_client is None:
            raise RuntimeError("GEMINI_API_KEY is missing.")

        prompt = build_gemini_prompt(extracted_text)
        active_model = resolve_model_name()

        response = active_client.models.generate_content(
            model=active_model,
            contents=prompt,
        )

        result_text = response.text

        if not result_text or not result_text.strip():
            raise ValueError("Gemini returned an empty response.")

        save_analysis_history(filename, ext, extracted_text, result_text)

        return jsonify({"result": result_text})

    except Exception as e:
        print("Gemini API ERROR:")
        print(type(e).__name__)
        print(str(e))

        fallback_result = build_local_study_material(extracted_text)
        warning_detail = format_gemini_error(e)
        save_analysis_history(
            filename,
            ext,
            extracted_text,
            fallback_result,
            "Gemini failed. Local fallback generated.",
            warning_detail,
        )

        return jsonify({
            "result": fallback_result,
            "warning": "Gemini failed. Local fallback generated.",
            "warning_detail": warning_detail
        })

@app.route("/clear", methods=["POST"])
def clear():
    """Deletes all files currently stored in the uploads folder."""
    try:
        deleted_files = clear_uploads_folder()
        return jsonify({
            "message": "Uploads folder cleared successfully.",
            "deleted_files": deleted_files
        })
    except Exception as e:
        print("Clear uploads error:", e)
        return jsonify({"error": "Failed to clear uploaded files."}), 500


@app.route("/healthz")
@app.route("/health")
def healthz():
    """Health check endpoint for Railway, Render, Docker, and monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "NoteLense-AI",
        "database": "ready" if db_ready else "offline"
    }), 200


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "The requested resource was not found."}), 404


@app.errorhandler(413)
def file_too_large(e):
    return jsonify({"error": "File is too large. Maximum allowed size is 20MB."}), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error. Please try again later."}), 500


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
        port=int(os.getenv("PORT", "5000")),
        use_reloader=False,
    )

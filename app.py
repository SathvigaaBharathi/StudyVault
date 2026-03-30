import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret')

app.config['MYSQL_HOST'] = os.getenv('MYSQLHOST', os.getenv('MYSQL_HOST', 'localhost'))
app.config['MYSQL_USER'] = os.getenv('MYSQLUSER', os.getenv('MYSQL_USER', 'root'))
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQLPASSWORD', os.getenv('MYSQL_PASSWORD', ''))
app.config['MYSQL_DB'] = os.getenv('MYSQLDATABASE', os.getenv('MYSQL_DB', 'studyvault'))
app.config['MYSQL_PORT'] = int(os.getenv('MYSQLPORT', os.getenv('MYSQL_PORT', 3306)))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'ppt', 'doc'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_doc_status(last_opened):
    if last_opened is None:
        return 'Cold'
    if isinstance(last_opened, datetime):
        last_opened = last_opened.date()
    days = (date.today() - last_opened).days
    if days < 7:
        return 'Active'
    elif days <= 30:
        return 'Fading'
    else:
        return 'Cold'


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email already registered.', 'danger')
            return redirect(url_for('login'))
        hashed = generate_password_hash(password)
        cur.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                    (name, email, hashed))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    uid = session['user_id']

    cur.execute("SELECT COUNT(*) AS total FROM documents WHERE user_id = %s", (uid,))
    total = cur.fetchone()['total']

    cur.execute("SELECT * FROM documents WHERE user_id = %s ORDER BY created_at DESC LIMIT 5", (uid,))
    recent = cur.fetchall()

    cur.execute("SELECT * FROM documents WHERE user_id = %s ORDER BY view_count DESC LIMIT 5", (uid,))
    most_opened = cur.fetchall()

    cur.execute("SELECT * FROM documents WHERE user_id = %s", (uid,))
    all_docs = cur.fetchall()
    cur.close()

    cold_docs = [d for d in all_docs if get_doc_status(d['last_opened']) == 'Cold']

    for d in recent:
        d['status'] = get_doc_status(d['last_opened'])
    for d in most_opened:
        d['status'] = get_doc_status(d['last_opened'])
    for d in cold_docs:
        d['status'] = get_doc_status(d['last_opened'])

    return render_template('dashboard.html', total=total, recent=recent,
                           most_opened=most_opened, cold_docs=cold_docs)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title'].strip()
        subject = request.form['subject'].strip()
        tags = request.form['tags'].strip()
        difficulty = int(request.form['difficulty'])
        file = request.files.get('file')

        if not file or file.filename == '':
            flash('Please select a file to upload.', 'danger')
            return redirect(url_for('upload'))

        if not allowed_file(file.filename):
            flash('File type not allowed. Use PDF, DOCX, or PPTX.', 'danger')
            return redirect(url_for('upload'))

        filename = secure_filename(file.filename)
        # Prefix with timestamp to avoid collisions
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO documents (user_id, title, file_path, subject, tags, difficulty)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (session['user_id'], title, filename, subject, tags, difficulty))
        mysql.connection.commit()
        cur.close()
        flash('Document uploaded successfully.', 'success')
        return redirect(url_for('documents'))
    return render_template('upload.html')


@app.route('/documents')
@login_required
def documents():
    cur = mysql.connection.cursor()
    uid = session['user_id']
    search = request.args.get('search', '').strip()
    subject_filter = request.args.get('subject', '').strip()

    query = "SELECT * FROM documents WHERE user_id = %s"
    params = [uid]

    if search:
        query += " AND (title LIKE %s OR tags LIKE %s)"
        params += [f'%{search}%', f'%{search}%']
    if subject_filter:
        query += " AND subject = %s"
        params.append(subject_filter)

    query += " ORDER BY created_at DESC"
    cur.execute(query, params)
    docs = cur.fetchall()

    cur.execute("SELECT DISTINCT subject FROM documents WHERE user_id = %s", (uid,))
    subjects = [r['subject'] for r in cur.fetchall() if r['subject']]
    cur.close()

    for d in docs:
        d['status'] = get_doc_status(d['last_opened'])

    difficulty_map = {1: 'Easy', 2: 'Medium', 3: 'Hard'}
    return render_template('documents.html', documents=docs, subjects=subjects,
                           search=search, subject_filter=subject_filter,
                           difficulty_map=difficulty_map)


@app.route('/open/<filename>')
@login_required
def open_doc(filename):
    cur = mysql.connection.cursor()
    cur.execute("""UPDATE documents SET view_count = view_count + 1, last_opened = %s
                   WHERE file_path = %s AND user_id = %s""",
                (datetime.now(), filename, session['user_id']))
    mysql.connection.commit()
    cur.close()
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)


@app.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete(doc_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT file_path FROM documents WHERE id = %s AND user_id = %s",
                (doc_id, session['user_id']))
    doc = cur.fetchone()
    if doc:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], doc['file_path'])
        if os.path.exists(filepath):
            os.remove(filepath)
        cur.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
        mysql.connection.commit()
        flash('Document deleted.', 'success')
    cur.close()
    return redirect(url_for('documents'))


if __name__ == '__main__':
    # Get the port from Render's environment, default to 5000 for local dev
    port = int(os.environ.get('PORT', 5000))
    # Bind to 0.0.0.0 to make it accessible externally
    app.run(host='0.0.0.0', port=port, debug=False)

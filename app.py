from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import pytesseract
import os
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Mock "user data" for simple login/logout functionality
users = {'testuser': 'password123'}

# ISO 639 language codes dictionary (trimmed for simplicity)
ISO_639_3 = {
    'eng': {'name': 'English', 'code': 'eng'},
    'spa': {'name': 'Spanish', 'code': 'spa'},
    'fra': {'name': 'French', 'code': 'fra'},
    'deu': {'name': 'German', 'code': 'deu'},
    'hin': {'name': 'Hindi', 'code': 'hin'},
    'tel': {'name': 'Telugu', 'code': 'tel'}
}

def extract_text_from_pdf(pdf_path, language='eng'):
    """Extract text from a PDF file with support for multiple languages."""
    text_content = []
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            text = pytesseract.image_to_string(image, lang=language)
            text_content.append(text)
        return ''.join(text_content)
    finally:
        os.remove(pdf_path)  # Clean up after processing

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle the home page and file upload."""
    if request.method == 'POST':
        file = request.files.get('file')
        language = request.form.get('language', 'eng')  # Default to English if no language is selected

        if not file or not file.filename.lower().endswith('.pdf'):
            flash('Invalid file format. Please upload a PDF file.', 'error')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            extracted_text = extract_text_from_pdf(file_path, language)
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
            return redirect(request.url)

        return render_template('result.html', text=extracted_text)

    return render_template('index.html', languages=ISO_639_3)

@app.route('/about')
def about():
    """Render the About page."""
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = password
            session['user'] = username
            flash('Signup successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('User already exists!', 'error')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, render_template_string
import sqlite3
import subprocess
import os
import shlex

app = Flask(__name__)

# Create a basic SQLite database
def init_db():
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, email TEXT)''')
    c.execute("INSERT OR IGNORE INTO users (id, username, email) VALUES (1, 'admin', 'admin@test.com')")
    conn.commit()
    conn.close()

PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>User Search</title>
    <style>
        body { padding: 20px; font-family: Arial, sans-serif; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 4px; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>User Search</h1>
    <form method="POST">
        <input type="text" name="username" placeholder="Enter username or command">
        <input type="submit" value="Search">
    </form>
    {% if result %}
        <h2>Results:</h2>
        <pre>{{ result }}</pre>
    {% endif %}
    
    <h1>File Upload</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        if 'username' in request.form:
            username = request.form['username']
            
            # Command injection check
            if ';' in username or '|' in username:
                try:
                    # Execute the command after the semicolon or pipe
                    cmd = username.split(';')[-1] if ';' in username else username.split('|')[-1]
                    cmd = cmd.strip()
                    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    result = f"Command output:\n{output.stdout}\n{output.stderr}"
                except Exception as e:
                    result = f"Error executing command: {str(e)}"
            else:
                try:
                    # Regular SQL query
                    conn = sqlite3.connect('demo.db')
                    c = conn.cursor()
                    query = f"SELECT * FROM users WHERE username = '{username}'"
                    c.execute(query)
                    result = str(c.fetchall())
                    conn.close()
                except Exception as e:
                    result = f"SQL Error: {str(e)}"
        
        if 'file' in request.files:
            file = request.files['file']
            if file:
                filename = file.filename
                filepath = os.path.join('uploads', filename)
                file.save(filepath)
                result = f'File uploaded to: {filepath}'

    return render_template_string(PAGE_TEMPLATE, result=result)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
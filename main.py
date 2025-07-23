import os
from flask import Flask, render_template_string, send_file, abort, url_for
from werkzeug.utils import secure_filename
import urllib.parse

app = Flask(__name__)

# Read shared directories from dirs.txt
try:
    with open('dirs.txt', 'r') as f:
        SHARED_DIRECTORIES = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("Warning: dirs.txt not found. No directories will be shared.")
    SHARED_DIRECTORIES = []

# HTML template for the directory listing page
DIRECTORY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Take My File!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .directory-list {
            list-style: none;
            padding: 0;
        }
        .directory-item {
            padding: 15px;
            margin: 10px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        .directory-item:hover {
            background-color: #e9ecef;
        }
        .directory-link {
            text-decoration: none;
            color: #28a745;
            font-weight: 500;
            font-size: 16px;
        }
        .directory-link:hover {
            color: #1e7e34;
        }
        .directory-status {
            font-size: 12px;
            color: #6c757d;
            margin-top: 5px;
        }
        .status-available {
            color: #28a745;
        }
        .status-unavailable {
            color: #dc3545;
        }
        .intro-text {
            text-align: center;
            color: #6c757d;
            margin-bottom: 30px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 Take My File!</h1>
        <div class="intro-text">
            Select a directory to browse and download files
        </div>
        
        <ul class="directory-list">
            {% for directory in directories %}
                <li class="directory-item">
                    {% if directory.available %}
                        <a href="/browse?dir={{ directory.encoded_path }}" class="directory-link">
                            📂 {{ directory.path }}
                        </a>
                        <div class="directory-status status-available">
                            ✓ Available ({{ directory.file_count }} files)
                        </div>
                    {% else %}
                        <div class="directory-link" style="color: #6c757d; cursor: not-allowed;">
                            📂 {{ directory.path }}
                        </div>
                        <div class="directory-status status-unavailable">
                            ✗ Directory not accessible
                        </div>
                    {% endif %}
                </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

# HTML template for the file listing page
FILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Take My File!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .file-list {
            list-style: none;
            padding: 0;
        }
        .file-item {
            padding: 10px;
            margin: 5px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .file-item:hover {
            background-color: #e9ecef;
        }
        .file-link {
            text-decoration: none;
            color: #007bff;
            font-weight: 500;
        }
        .file-link:hover {
            color: #0056b3;
        }
        .directory-path {
            background-color: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-family: monospace;
            color: #495057;
        }
        .no-files {
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 20px;
        }
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            padding: 8px 16px;
            background-color: #6c757d;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 14px;
        }
        .back-link:hover {
            background-color: #5a6268;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Directories</a>
        <h1>📁 Take My File!</h1>
        <div class="directory-path">
            <strong>Current Directory:</strong> {{ directory_path }}
        </div>
        
        {% if files %}
            <ul class="file-list">
                {% for file in files %}
                    <li class="file-item">
                        <a href="/download?dir={{ encoded_directory }}&file={{ file.encoded_name }}" class="file-link">
                            📄 {{ file.name }}
                        </a>
                    </li>
                {% endfor %}
            </ul>
        {% else %}
            <div class="no-files">
                No files found in this directory.
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

def get_directory_info(directory_path):
    """Get information about a directory including availability and file count."""
    try:
        if not os.path.exists(directory_path):
            return {"available": False, "file_count": 0}
        
        file_count = 0
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                file_count += 1
        
        return {"available": True, "file_count": file_count}
    except (PermissionError, OSError):
        return {"available": False, "file_count": 0}

@app.route('/')
def index():
    """Display the list of available directories."""
    directories = []
    
    for directory_path in SHARED_DIRECTORIES:
        info = get_directory_info(directory_path)
        directories.append({
            "path": directory_path,
            "encoded_path": urllib.parse.quote(directory_path, safe=''),
            "available": info["available"],
            "file_count": info["file_count"]
        })
    
    return render_template_string(DIRECTORY_TEMPLATE, directories=directories)

@app.route('/browse')
def browse_directory():
    """Display the list of files in the specified directory."""
    try:
        from flask import request
        
        # Get directory from query parameters
        encoded_directory = request.args.get('dir')
        if not encoded_directory:
            return "<h1>Error: Missing directory parameter</h1>", 400
            
        # Decode the directory path
        directory_path = urllib.parse.unquote(encoded_directory)
        
        # Verify this is one of our allowed directories
        if directory_path not in SHARED_DIRECTORIES:
            abort(403)
        
        # Check if the directory exists
        if not os.path.exists(directory_path):
            return f"<h1>Error: Directory '{directory_path}' does not exist!</h1>", 404
        
        # Get list of files (not directories) in the shared directory
        files = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                files.append({
                    "name": item,
                    "encoded_name": urllib.parse.quote(item, safe='')
                })
        
        # Sort files alphabetically by name
        files.sort(key=lambda x: x["name"].lower())
        
        return render_template_string(
            FILE_TEMPLATE, 
            files=files, 
            directory_path=directory_path,
            encoded_directory=encoded_directory
        )
    
    except PermissionError:
        return f"<h1>Error: Permission denied to access directory '{directory_path}'</h1>", 403
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/download')
def download_file():
    """Download a specific file from the specified directory using query parameters."""
    try:
        from flask import request
        
        # Get parameters from query string
        encoded_directory = request.args.get('dir')
        encoded_filename = request.args.get('file')
        
        if not encoded_directory or not encoded_filename:
            return "<h1>Error: Missing directory or filename parameter</h1>", 400
        
        # Decode the directory path and filename
        directory_path = urllib.parse.unquote(encoded_directory)
        filename = urllib.parse.unquote(encoded_filename)
        
        # Verify this is one of our allowed directories
        if directory_path not in SHARED_DIRECTORIES:
            return f"<h1>Error: Access denied to directory '{directory_path}'</h1>", 403
        
        # Secure the filename to prevent directory traversal attacks
        safe_filename = secure_filename(filename)
        
        # Construct the full file path
        file_path = os.path.join(directory_path, safe_filename)
        
        # Check if file exists and is actually a file (not a directory)
        if not os.path.exists(file_path):
            return f"<h1>Error: File '{filename}' not found</h1>", 404
        
        if not os.path.isfile(file_path):
            return f"<h1>Error: '{filename}' is not a file</h1>", 404
        
        # Send the file as an attachment (forces download)
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return f"<h1>Error downloading file: {str(e)}</h1>", 500

if __name__ == '__main__':
    print(f"Starting file sharing server...")
    print(f"Shared directories:")
    for i, directory in enumerate(SHARED_DIRECTORIES, 1):
        info = get_directory_info(directory)
        status = "✓ Available" if info["available"] else "✗ Not accessible"
        file_count = f"({info['file_count']} files)" if info["available"] else ""
        print(f"  {i}. {directory} - {status} {file_count}")
    
    print(f"Server will be available at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

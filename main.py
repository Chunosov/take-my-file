import os
from flask import Flask, render_template_string, send_file, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Hardcoded directory path for file sharing
SHARED_DIRECTORY = "F:/tmp"  # Change this to your desired directory

# HTML template for the file listing page
HTML_TEMPLATE = """
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
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 Take My File!</h1>
        <div class="directory-path">
            <strong>Shared Directory:</strong> {{ directory_path }}
        </div>
        
        {% if files %}
            <ul class="file-list">
                {% for file in files %}
                    <li class="file-item">
                        <a href="/download/{{ file }}" class="file-link">📄 {{ file }}</a>
                    </li>
                {% endfor %}
            </ul>
        {% else %}
            <div class="no-files">
                No files found in the shared directory.
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Display the list of files in the shared directory."""
    try:
        # Check if the directory exists
        if not os.path.exists(SHARED_DIRECTORY):
            return f"<h1>Error: Directory '{SHARED_DIRECTORY}' does not exist!</h1>", 404
        
        # Get list of files (not directories) in the shared directory
        files = []
        for item in os.listdir(SHARED_DIRECTORY):
            item_path = os.path.join(SHARED_DIRECTORY, item)
            if os.path.isfile(item_path):
                files.append(item)
        
        # Sort files alphabetically
        files.sort()
        
        return render_template_string(HTML_TEMPLATE, files=files, directory_path=SHARED_DIRECTORY)
    
    except PermissionError:
        return f"<h1>Error: Permission denied to access directory '{SHARED_DIRECTORY}'</h1>", 403
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download a specific file from the shared directory."""
    try:
        # Secure the filename to prevent directory traversal attacks
        safe_filename = secure_filename(filename)
        
        # Construct the full file path
        file_path = os.path.join(SHARED_DIRECTORY, safe_filename)
        
        # Check if file exists and is actually a file (not a directory)
        if not os.path.exists(file_path):
            abort(404)
        
        if not os.path.isfile(file_path):
            abort(404)
        
        # Send the file as an attachment (forces download)
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return f"<h1>Error downloading file: {str(e)}</h1>", 500

if __name__ == '__main__':
    print(f"Starting file sharing server...")
    print(f"Shared directory: {SHARED_DIRECTORY}")
    print(f"Server will be available at: http://localhost:5000")
    
    # Check if shared directory exists
    if not os.path.exists(SHARED_DIRECTORY):
        print(f"WARNING: Shared directory '{SHARED_DIRECTORY}' does not exist!")
        print("Please update the SHARED_DIRECTORY variable in the code to point to an existing directory.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

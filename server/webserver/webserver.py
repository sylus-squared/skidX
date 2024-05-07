from flask import Flask, request, jsonify, send_from_directory, render_template, send_file, abort
from werkzeug.utils import secure_filename
import scripts.uploadFile as uploader
import os
import yaml
import hashlib
import re
import socket
from flask_cors import CORS

"""
TODO
Make the webserver send files with the correct name and extention
"""

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
analysis_in_progress = []

with open('config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

def allowed_file(filename):        # This will be just .jar in the furture and is just for testing
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

#---------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/get_files')
def get_files():
    data_dir = 'data'
    files = [
        os.path.splitext(f)[0]
        for f in os.listdir(data_dir) 
        if os.path.isfile(os.path.join(data_dir, f))
    ]
    return jsonify(files)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html") 

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/setup', methods=['GET'])
def send_file():
    filename = request.args.get('filename') # Get the filename and directory from request parameters
    directory = request.args.get('directory')

    if not filename or not directory:
        abort(400, 'Both filename and directory are required.')

    if not os.path.exists(directory): # Check if the directory actually exists
        abort(404, 'Directory not found.')

    file_path = os.path.join(directory, filename) # Check if the file actually exists
    if not os.path.exists(file_path):
        abort(404, 'File not found.')

    return send_file(file_path, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'fileInput' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['fileInput']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        new_filename = f"{os.path.splitext(filename)[0]}_upload{os.path.splitext(filename)[1]}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        uploader.upload_file(os.path.join(app.config['UPLOAD_FOLDER'], new_filename), config)
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file_hash = hashlib.sha256()
        with open(file_path, 'rb') as file:
            file_hash.update(file.read())

        file_name = file_hash.hexdigest()
        analysis_in_progress.append(file_name + ".txt") # The display endpoint needs the extension to work, change this at some point
        return jsonify({'success': 'Upload success', 'hash': file_name}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/display/<file>')
def display(file="test"):
    file_path = os.path.join(os.path.dirname(__file__), 'data', file + ".txt")
    print(file_path)
    file_name_with_extension = os.path.basename(file_path)
    
    if re.search(r'[;\'"]', file):
        return render_template('stupid.html') # Check for SQL injection (just for fun)
    
    try:
        with open(file_path, 'r') as file:
            file_content = file.readlines()
    except FileNotFoundError:
        print(file_name_with_extension)
        print(analysis_in_progress)
        if file_name_with_extension in analysis_in_progress:
            return render_template('analysisPage.html', file_content=None)
        print("ERROR file content is none")
        return render_template('404Analysis.html'), 404
    
    return render_template('analysisPage.html', file_content=file_content)

@app.route('/check_file_status/<file>')
def check_file_status(file):
    data_dir = 'data'
    file_path = os.path.join(data_dir, file + ".txt")
    
    file_exists = os.path.exists(file_path)
    file_content = ''
    if file_exists:
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
        except FileNotFoundError:
            pass

    return jsonify({'fileExists': file_exists, 'fileContent': file_content})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'fileInput' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['fileInput']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        new_filename = f"{os.path.splitext(filename)[0]}_upload{os.path.splitext(filename)[1]}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
        uploader.upload_file(os.path.join(app.config['UPLOAD_FOLDER'], new_filename), config)
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file_hash = hashlib.sha256()
        with open(file_path, 'rb') as file:
            file_hash.update(file.read())

        file_name = file_hash.hexdigest()
        analysis_in_progress.append(file_name + ".txt") # The display endpoint needs the extension to work, change this at some point
        return jsonify({'success': 'Upload success', 'hash': file_name}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
@app.route('/result', methods=['POST'])
def result():
    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        file.save(os.path.join('data', file.filename))
        return 'File uploaded successfully', 200
    else:
        return 'Error saving file', 500

#---------------------------------------------------------------------------

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=False)

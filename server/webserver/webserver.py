from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask import render_template
import scripts.uploadFile as uploader
import os
import yaml
import hashlib

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
analysis_in_progress = []

with open('config/config.yml', 'r') as file:
    config = yaml.safe_load(file)

def allowed_file(filename):        # This will be just .jar in the furture and is just for testing
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def hash_data(data):
    data_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
    return data_hash
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
    files = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    return jsonify(files)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html") 

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/display')
@app.route('/display/<file>')
def display(file="test"):
    file_path = os.path.join(os.path.dirname(__file__), 'data', file + ".txt")
    print(file_path)
    file_name_with_extension = os.path.basename(file_path)
    try:
        with open(file_path, 'r') as file:
            file_content = file.readlines()
    except FileNotFoundError:
        if file_name_with_extension in analysis_in_progress:
            return render_template('analysisPage.html', file_content=None)
        print("ERROR file content is none")
        return render_template('404Analysis.html'), 404
    
    return render_template('analysisPage.html', file_content=file_content)

@app.route('/check_file_status')
def check_file_status():
    data_dir = 'data'
    file_path = os.path.join(data_dir, 'example.txt')
    
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
        return jsonify({'success': True, 'message': 'File uploaded successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400 

#---------------------------------------------------------------------------

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=False)

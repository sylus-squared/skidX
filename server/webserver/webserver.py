from flask import Flask, request, jsonify, send_from_directory, render_template, send_file, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename # This is needed to prevent potential LFI, but is it actually necessary?
import scripts.uploadFile as uploader
import os
import json
import sys
import scripts.uploadFile
import scripts.inetsim
sys.path.insert(0, os.path.abspath('../machinery')) # I hate that I have to do this
from proxmox import get_ticket, get_snapshot_list, create_snapshot, revert_to_snapshot 
import shutil
import hashlib
import re
import socket

"""
TODO
Stop the display endpoint from needing the file extention in analysis_in_progress
"""

app = Flask(__name__)
CORS(app)

app.config["UPLOAD_FOLDER"] = "uploads"
ALLOWED_FILES = ["headlessmc-launcher-1.9.0.jar", ".minecraft", "HeadlessMC", "config", "background_blue.png",
 "background_red.png", "background_black.png", "background_purple.png", "background_white.png"] # Files the endpoint is allowed to access from the /setup endpoint (to prevent LFI)
analysis_in_progress = []

sys.path.insert(0, os.path.abspath("server/machinery"))

with open("config/config.json", "r") as read_file:
    config = json.load(read_file)

def allowed_file(filename):        # This will be just .jar in the furture and is just for testing
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"jar"}

#---------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/get_files")
def get_files():
    data_dir = "data"
    files = [
        os.path.splitext(f)[0]
        for f in os.listdir(data_dir) 
        if os.path.isfile(os.path.join(data_dir, f))
    ]
    return jsonify(files)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html") 

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/setup/<file>", methods=["GET"])
def setup(file): # Used to get all necessary files for the endpoint to function without internet
    print(file)
    if file in ALLOWED_FILES:
        file_path = f"setupFiles/{file}"
        if os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True)
        elif os.path.exists(file_path):
            if os.path.exists(f"setupFiles/{file}.zip"):
                return send_file(f"{file_path}.zip", as_attachment=True)
            shutil.make_archive(f"setupFiles/{file}", "zip", f"setupFiles/{file}")
            return send_file(f"{file_path}.zip", as_attachment=True)
        return jsonify({"error": "File not found"}), 404
    return jsonify({"error": "Access denied"}), 403


@app.route("/upload", methods=["POST"])
def upload_file():
    if "fileInput" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["fileInput"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        analysis_time = int(request.form.get("analysisTime"))

        if analysis_time < 40 or analysis_time > 180: # Seconds
            return jsonify({"error": "Analysis time must be between 40s and 180s"}), 406

        new_filename = f"{os.path.splitext(filename)[0]}_upload{os.path.splitext(filename)[1]}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], new_filename))
        
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)
        file_hash = hashlib.sha256()
        

        with open(file_path, "rb") as file:
            file_hash.update(file.read())
        file_name = file_hash.hexdigest()

        if file_name + ".txt" in analysis_in_progress or os.path.exists(f"data/{file_name}"):
            return jsonify({"error": "File has already been analysed"}), 409

        try:
            uploader.upload_file(os.path.join(app.config["UPLOAD_FOLDER"], new_filename), config, analysis_time + 10) # The +10 is to make sure the client does not try and sent the report while inetsim is running
        except ConnectionRefusedError:
            print("Client refused the connection, is it online?")
            return jsonify({"error": "File upload failed, is the analysis server online?"}), 500
    
        analysis_in_progress.append(file_name + ".txt") # The display endpoint needs the extension to work, change this at some point
        run_inetsim(file_name)
        return jsonify({"success": "Upload success", "hash": file_name}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route("/display/<file>")
def display(file="test"):
    file_path = os.path.join(os.path.dirname(__file__), "data", file + ".txt")
    print(file_path)
    file_name_with_extension = os.path.basename(file_path)
    
    if re.search(r'[;\'"]', file): # Check for SQL injection (the backend doesn't use a database :), this is just to troll people that try)
        return render_template("stupid.html")
    
    try:
        with open(file_path, 'r') as file:
            file_content = file.readlines()
    except FileNotFoundError:
        print(file_name_with_extension)
        print(analysis_in_progress)
        if file_name_with_extension in analysis_in_progress:
            return render_template("analysisPage.html", file_content=None)
        print("ERROR file content is none")
        return render_template("404Analysis.html"), 404
    
    return render_template("analysisPage.html", file_content=file_content)

@app.route("/check_file_status/<file>")
def check_file_status(file):
    data_dir = "data"
    file_path = os.path.join(data_dir, file + ".txt")
    
    file_exists = os.path.exists(file_path)
    file_content = ""
    if file_exists:
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
        except FileNotFoundError:
            pass

    return jsonify({"fileExists": file_exists, "fileContent": file_content})

    
@app.route("/result", methods=["POST"])
def result():
    if "file" not in request.files:
        return "No file part in the request", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    if file:
        file.save(os.path.join("data", file.filename))
        return "File uploaded successfully", 200
    else:
        return "Error saving file", 500

#---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    app.run(debug=False)

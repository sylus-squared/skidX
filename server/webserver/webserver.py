from flask import Flask, request, jsonify, send_from_directory, render_template, send_file, abort
from flask_cors import CORS
import os
import json
import sys
import scripts.uploadFile
import scripts.inetsim
sys.path.insert(0, os.path.abspath('../machinery')) # I hate that I have to do this
from proxmox import get_ticket, get_snapshot_list, create_snapshot, revert_to_snapshot 
import shutil
import hashlib
import logging
import re

app = Flask(__name__)
CORS(app)

print("""
     _    _     ___  __
 ___| | _(_) __| \ \/ /
/ __| |/ / |/ _` |\  / 
\__ \   <| | (_| |/  \ 
|___/_|\_\_|\__,_/_/\_\
                       
""")

app.config["UPLOAD_FOLDER"] = "uploads"
ALLOWED_FILES = ["headlessmc-launcher-1.9.0.jar", ".minecraft", "HeadlessMC", "config", "background_blue.png",
 "background_red.png", "background_black.png", "background_purple.png", "background_white.png", "jre-8u411-windows-x64.exe", "python.exe",
 "requests", "urllib3", "chardet", "certifi", "idna"] # Files the endpoint is allowed to access from the /setup endpoint (to prevent LFI)
analysis_in_progress = []

# Setup propper logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler() # Create a stream handler for printing to the terminal
stream_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(name)s - [%(levelname)s]- %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)  # Add both handlers to the logger
logger.addHandler(stream_handler)

analysis_running = False
file_que = []

if not os.path.exists("config/config.json"):
    logging.critical("Config file does not exist and the program cannot continue")
    quit()

with open("config/config.json", "r") as read_file:
    config = json.load(read_file)

if config == []:
    logging.critical("Log file is empty")
    quit()

logging.info("Loaded config file")

ticket, csrf_token = get_ticket()

if ticket == None or csrf_token == None:
    logging.critical("Ticket or csrf token is null and the program cannot continue")
    quit()

vm_id = config["machinery"]["vm_id"]
snapshot_name = config["machinery"]["snapshot_name"]
snapshot_list = get_snapshot_list(vm_id, ticket, csrf_token)
snapshot_created = False

for i in snapshot_list: # For some reason, python refuses to allow me to just do i["name"], it just gives me a key error, but this works fine for no reason
    for key, value in i.items():
        if value == snapshot_name:
            snapshot_created = True

if snapshot_created == False:
    print("creating snapshot")
    create_snapshot(vm_id, ticket, csrf_token)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"jar"}

def trigger_error(message):
    event_stream().send(f'data: {{ "message": "{message}" }}\n\n')
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

@app.route("/error/<message>")
def show_error(message):
    return render_template('error.html', error_message=message)

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
            logging.warning("Client tried to access a file that does not exist")
        return jsonify({"error": "File not found"}), 404
    logging.warning("Client tried to access a file that is not allowed")
    return jsonify({"error": "Access denied"}), 403

@app.route("/upload", methods=["POST"])
def upload_file():
    global analysis_running
    global file_que

    if "fileInput" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["fileInput"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
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

        if analysis_running:
            file_que.append([new_filename, analysis_time])
            return jsonify({"error": "Analysis in progress, file added to que"}), 200

        try:
            upload_file(os.path.join(app.config["UPLOAD_FOLDER"], new_filename), config, analysis_time)
        except ConnectionRefusedError:
            logging.critical("File upload failed, is the analysis server online?")
            return jsonify({"error": "File upload failed, is the analysis server online?"}), 500
    
        analysis_in_progress.append(file_name + ".txt") # The display endpoint needs the extension to work, change this at some point
        run_inetsim(analysis_time - 10, file_name) # The - 10 is to ensure that inetsim stops before the client sends the report
        logging.info("Sent a file with the hash: " + file_name)
        return jsonify({"success": "Upload success", "hash": file_name}), 200
    else:
        logging.warning("Client tried to upload a file with a disalowed file type")
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
    return jsonify({"fileExists": file_exists})

@app.route("/result", methods=["POST"])
def result():
    global analysis_running
    global file_que

    if "file" not in request.files:
        return "No file part in the request", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    if file:
        file.save(os.path.join("data", file.filename))
        analysis_in_progress.remove(file.filename)

        first_in_que = file_que[0]
        if first_in_que[0] == file.filename:
            file_que.pop[0]

        revert = proxmox.revert_to_snapshot(snapshot_name, vm_id, ticket, csrf_token)
        if not revert:
            logging.critical(revert)
            logging.info("Program will continue on outdated snapshot")
            trigger_error("Critital error: the program could not revert to a the snapshot and will continue in a potentially compromised state")

        if not file_que == []: # If there are files in the que
            try:
                file_array = file_que[0]
                upload_file(os.path.join(app.config["UPLOAD_FOLDER"], file_array[0]), config, file_array[1])
            except ConnectionRefusedError:
                logging.critical("File upload failed, is the analysis server online?")
                        
            analysis_in_progress.append(file_array[0] + ".txt") # The display endpoint needs the extension to work, change this at some point
            run_inetsim(analysis_time - 10, file_array[1]) # The - 10 is to ensure that inetsim stops before the client sends the report
            logging.info("Sent a file from the que with the hash: " + file_array[0])
            return "File uploaded successfully", 200

        analysis_running = False
        return "File uploaded successfully", 200
    else:
        return "Error saving file", 500

#---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    logging.info("Webserver started")
    app.run(host=config["connection"]["webserver_ip"], debug=False)

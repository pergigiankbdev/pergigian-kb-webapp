import os
import json
from flask import Flask, send_from_directory, request, jsonify
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
DATA_FILE = 'data_store.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"banjir": [], "pergerakan": [], "tempahan": [], "kalendar": [], "surat": [], "kertas_kerja": []}
    with open(DATA_FILE, 'r') as f:
        try:
            data = json.load(f)
            # Ensure keys exist
            for key in ["banjir", "pergerakan", "tempahan", "kalendar", "surat", "kertas_kerja"]:
                if key not in data:
                    data[key] = []
            return data
        except json.JSONDecodeError:
            return {"banjir": [], "pergerakan": [], "tempahan": [], "kalendar": [], "surat": [], "kertas_kerja": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# --- BANJIR ENDPOINTS ---
@app.route('/api/banjir', methods=['GET'])
def get_banjir():
    data = load_data()
    return jsonify(data.get("banjir", []))

@app.route('/api/banjir', methods=['POST'])
def add_banjir():
    data = load_data()
    req = request.json
    
    new_report = {
        "id": f"b{len(data.get('banjir', [])) + 1}",
        "location": req.get("location"),
        "water_level_status": req.get("water_level_status", "Normal"),
        "water_level_meters": float(req.get("water_level_meters", 0.0)),
        "reported_at": datetime.now().isoformat(),
        "reporter_name": req.get("reporter_name", "Pentadbir"),
        "notes": req.get("notes", "")
    }
    
    data["banjir"].append(new_report)
    save_data(data)
    return jsonify(new_report), 201

# --- LOG PERGERAKAN STAF ENDPOINTS ---
@app.route('/api/pergerakan', methods=['GET'])
def get_pergerakan():
    data = load_data()
    return jsonify(data.get("pergerakan", []))

@app.route('/api/pergerakan/checkout', methods=['POST'])
def checkout_staff():
    data = load_data()
    req = request.json
    
    new_movement = {
        "id": f"p{len(data.get('pergerakan', [])) + 1}",
        "staff_name": req.get("staff_name"),
        "destination": req.get("destination"),
        "purpose": req.get("purpose"),
        "time_out": req.get("time_out"),
        "expected_time_in": req.get("expected_time_in"),
        "actual_time_in": None,
        "status": "Keluar"
    }
    
    data["pergerakan"].append(new_movement)
    save_data(data)
    return jsonify(new_movement), 201

@app.route('/api/pergerakan/checkin/<id>', methods=['POST'])
def checkin_staff(id):
    data = load_data()
    movements = data.get("pergerakan", [])
    
    for mov in movements:
        if mov["id"] == id:
            mov["status"] = "Kembali"
            mov["actual_time_in"] = datetime.now().strftime("%I:%M %p")
            save_data(data)
            return jsonify(mov)
            
    return jsonify({"error": "Log tidak dijumpai"}), 404

# --- TEMPAHAN BILIK MESYUARAT ENDPOINTS ---
@app.route('/api/tempahan', methods=['GET'])
def get_tempahan():
    data = load_data()
    return jsonify(data.get("tempahan", []))

@app.route('/api/tempahan', methods=['POST'])
def add_tempahan():
    data = load_data()
    req = request.json
    
    room_name = req.get("room_name")
    booking_date = req.get("booking_date")
    start_time = req.get("start_time")
    end_time = req.get("end_time")
    meeting_title = req.get("meeting_title")
    applicant_name = req.get("applicant_name")

    if start_time >= end_time:
        return jsonify({"error": "Waktu tamat mestilah selepas waktu mula."}), 400

    bookings = data.get("tempahan", [])
    for b in bookings:
        if b["room_name"] == room_name and b["booking_date"] == booking_date:
            if (start_time < b["end_time"]) and (end_time > b["start_time"]):
                return jsonify({
                    "error": f"Pertindihan Tempahan! Bilik ini telah ditempah oleh {b['applicant_name']} untuk '{b['meeting_title']}' pada jam {b['start_time']} - {b['end_time']}."
                }), 400

    new_booking = {
        "id": f"t{len(bookings) + 1}",
        "room_name": room_name,
        "booking_date": booking_date,
        "start_time": start_time,
        "end_time": end_time,
        "meeting_title": meeting_title,
        "applicant_name": applicant_name
    }
    
    bookings.append(new_booking)
    data["tempahan"] = bookings
    save_data(data)
    return jsonify(new_booking), 201

# --- KALENDAR ENDPOINTS ---
@app.route('/api/kalendar', methods=['GET'])
def get_kalendar():
    data = load_data()
    return jsonify(data.get("kalendar", []))

@app.route('/api/kalendar', methods=['POST'])
def add_kalendar():
    data = load_data()
    req = request.json
    
    new_event = {
        "id": f"k{len(data.get('kalendar', [])) + 1}",
        "event_name": req.get("event_name"),
        "department_involved": req.get("department_involved", "Semua"),
        "event_date": req.get("event_date"),
        "venue": req.get("venue"),
        "description": req.get("description", "")
    }
    
    data["kalendar"].append(new_event)
    save_data(data)
    return jsonify(new_event), 201

# --- SURAT-MENYURAT ENDPOINTS ---
@app.route('/api/surat', methods=['GET'])
def get_surat():
    data = load_data()
    return jsonify(data.get("surat", []))

@app.route('/api/surat', methods=['POST'])
def add_surat():
    data = load_data()
    req = request.json
    
    new_letter = {
        "id": f"s{len(data.get('surat', [])) + 1}",
        "letter_ref_number": req.get("letter_ref_number"),
        "sender_receiver": req.get("sender_receiver"),
        "category": req.get("category", "Incoming"),
        "date_received": req.get("date_received"),
        "subject": req.get("subject"),
        "status": req.get("status", "Pending")
    }
    
    data["surat"].append(new_letter)
    save_data(data)
    return jsonify(new_letter), 201

@app.route('/api/surat/status/<id>', methods=['POST'])
def toggle_surat_status(id):
    data = load_data()
    letters = data.get("surat", [])
    
    for letter in letters:
        if letter["id"] == id:
            current_status = letter.get("status", "Pending")
            letter["status"] = "Completed" if current_status == "Pending" else "Pending"
            save_data(data)
            return jsonify(letter)
            
    return jsonify({"error": "Surat tidak dijumpai"}), 404

# --- KERTAS KERJA ENDPOINTS ---
@app.route('/api/kertas-kerja', methods=['GET'])
def get_kertas_kerja():
    data = load_data()
    return jsonify(data.get("kertas_kerja", []))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

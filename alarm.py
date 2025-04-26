# na raspbere

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import threading

app = Flask(__name__)
CORS(app) # omijanie zapytania OPTIONS

# state - czy uzbrojony
# status - czy jest awaria
# todo: zmienic nazewnictwo bo mylace

alarm_state = False
alarm_status = False

ip_server = "http://127.0.0.1:5000/"
passphrase = "admin123" # na razie na szytywno tu

MSG_BAD_PASSPHRASE = "Request wasn't successful, passphrase not provided or invalid"
MSG_OK = "Request was successful"

def passphrase_ok(data):
    return "passphrase" in data and data["passphrase"] == passphrase

@app.route("/change_alarm_state", methods=["POST"])
def change_alarm_state():
    global alarm_state
    req_data = request.get_json()
    print(req_data) # debug

    if not passphrase_ok(req_data):
        return jsonify(status="error", message=MSG_BAD_PASSPHRASE)
    
    if "state" not in req_data or not isinstance(req_data["state"], bool):
        return jsonify(status="error", message="ERROR: `state` key not present in the request or invalid value")
    else:
        alarm_state = req_data["state"]
        if alarm_state == True:
            print("Uzbrajam alarm...")
        elif alarm_state == False:
            print("Rozbrajam alarm...")

    return jsonify(status="ok", message=MSG_OK)

@app.route("/get_alarm_state", methods=["POST"])
def get_alarm_state():
    req_data = request.get_json()
    print(req_data) # debug

    if not passphrase_ok(req_data):
        return jsonify(status="error", message=MSG_BAD_PASSPHRASE)

    return jsonify(alarm_state=alarm_state, status="ok", message=MSG_OK)

@app.route("/get_alarm_status", methods=["POST"])
def get_alarm_status():
    req_data = request.get_json()
    print(req_data) # debug

    if not passphrase_ok(req_data):
        return jsonify(status="error", message=MSG_BAD_PASSPHRASE)

    return jsonify(alarm_status=alarm_status, status="ok", message=MSG_OK)

@app.route("/alarm_accept", methods=["POST"])
def alarm_accept():
    global alarm_status
    req_data = request.get_json()
    print(req_data) # debug

    if not passphrase_ok(req_data):
        return jsonify(status="error", message=MSG_BAD_PASSPHRASE)
    
    actually_accepted = alarm_status
    alarm_status = False
    return jsonify(status="ok", message=MSG_OK, actually_accepted=actually_accepted) # actually_accepted - mowi czy rzeczywiscie potwierdzono alarm, bo request normalnie przejdzie nawet jesli nie bylo alarmu podczas potwierzdania, ale niech strona wie co sie dokladnie stalo

# nie mamy fizycznie czujnika na razie wiec ta funkcja bedzie symulowala wykrywanie ruchu i ewentualne zasygnalizowanie ze powinna byc odpalona awaria
def read_sensor_output_sim():
    global alarm_status
    # jesli w pliku jest 1 - to znaczy ze jest ruch, jesli 0 - ruchu nie ma
    sensor_out = None
    with open("symulacja_czy_jest_ruch_na_czujniku", "r") as f: # w przyszlosci zastapic ten blok kodu rzeczywistym odczytywaniem outputu z czujnika
        sensor_out = int(f.read())
        print("sensor:", sensor_out)
        assert sensor_out in (0, 1)

    if sensor_out == 1 and alarm_state == True and alarm_status == False: # jest ruch na czujniku, jest zalaczony alarm, nie ma jeszcze odpalonej awarii (ze nie dzwoni alarm) wiec trzeba odpalic
        alarm_status = True

def alarm_loop(): # w prawdziwej aplikacji, niesymulowanej powinno zostac wystartowane jako osobny thread w mainie, na razie nieuzywane
    while True:
        if alarm_status == True:
            print("ALARM") # w prawdziwym przypadku odpal jakis sygnal dzwiekowy

def sensor_loop():
    SENSOR_INTERVAL_S = 3
    while True:
        read_sensor_output_sim()
        print("ALARM" if alarm_status == True else "BRAK ALARMU") # to jest tylko debug, nie powinno w sensor loopie byc zachowan alarmu, powinnismy go tylko powiadomic, ze powinien wejsc w stan awarii, lecz samo to wejscie dzieje sie w alarm_loop
        print("Czy alarm zalaczony:", alarm_state) # debug
        time.sleep(SENSOR_INTERVAL_S)

if __name__ == "__main__":
    thread_sensor_loop = threading.Thread(target=sensor_loop, args=())
    thread_sensor_loop.daemon = True
    thread_sensor_loop.start()
    app.run(port=5001) # blokujace



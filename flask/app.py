# app.py
from flask import Flask, render_template, request, jsonify
import paho.mqtt.client as mqtt
import ssl

app = Flask(__name__)

# =========================================
# KONFIGURASI SECURE MQTT CLOUD (HIVEMQ)
# =========================================
MQTT_BROKER    = "6028353e09704a62b28cd72dd96f1a1d.s1.eu.hivemq.cloud"
MQTT_PORT      = 8883                      
MQTT_USER      = "nuniksolichatun" 
MQTT_PASS      = "S0l1chatun*" 

# Variabel global untuk menyimpan data sensor terakhir
sensor_data = {
    "cahaya": 0,
    "kelembaban": 0,
    "status_lampu": "OFF",
    "status_pompa": "OFF"
}

# =========================================
# CALLBACK MQTT
# =========================================
def on_connect(client, userdata, flags, rc):
    print("Terhubung ke MQTT Broker dengan kode: " + str(rc))
    # Subscribe ke topik yang dipublish oleh ESP32
    client.subscribe("tjkt/lampu/cahaya")
    client.subscribe("tjkt/lampu/status")
    client.subscribe("tjkt/pompa/kelembaban")
    client.subscribe("tjkt/pompa/status")

def on_message(client, userdata, msg):
    global sensor_data
    topic = msg.topic
    payload = msg.payload.decode('utf-8').strip()
    
    # Memperbarui data berdasarkan topik yang masuk
    if topic == "tjkt/lampu/cahaya":
        sensor_data["cahaya"] = payload
    elif topic == "tjkt/lampu/status":
        sensor_data["status_lampu"] = payload
    elif topic == "tjkt/pompa/kelembaban":
        sensor_data["kelembaban"] = payload
    elif topic == "tjkt/pompa/status":
        sensor_data["status_pompa"] = payload

# Inisialisasi MQTT Client (Paho)
client = mqtt.Client(client_id="Web_Dashboard_TJKT")
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set(tls_version=ssl.PROTOCOL_TLS) # Wajib untuk port 8883 HiveMQ
client.on_connect = on_connect
client.on_message = on_message

# Memulai koneksi MQTT di latar belakang (non-blocking)
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# =========================================
# ROUTING FLASK (WEB API)
# =========================================
@app.route('/')
def index():
    # Menampilkan halaman utama
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    # API untuk memberikan data terbaru ke frontend dalam format JSON
    return jsonify(sensor_data)

@app.route('/api/control', methods=['POST'])
def control():
    # API untuk menerima perintah klik tombol dari frontend
    data = request.json
    device = data.get('device')
    action = data.get('action') # "1" untuk ON, "0" untuk OFF

    # Publish perintah ke ESP32 melalui MQTT
    if device == "lampu":
        client.publish("tjkt/lampu/kontrol", action)
    elif device == "pompa":
        client.publish("tjkt/pompa/kontrol", action)

    return jsonify({"status": "success", "device": device, "action": action})

if __name__ == '__main__':
    # Jalankan server Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
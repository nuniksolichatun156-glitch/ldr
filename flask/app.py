import os
import ssl
import paho.mqtt.client as mqtt
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Menggunakan Environment Variables untuk keamanan
MQTT_BROKER = os.environ.get("MQTT_BROKER", "6028353e09704a62b28cd72dd96f1a1d.s1.eu.hivemq.cloud")
MQTT_USER   = os.environ.get("MQTT_USER", "nuniksolichatun")
MQTT_PASS   = os.environ.get("MQTT_PASS", "S0l1chatun*")

# Inisialisasi MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="Web_Dashboard_TJKT")
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set(cert_reqs=ssl.CERT_NONE) # Memaksa koneksi aman

def connect_mqtt():
    try:
        client.connect(MQTT_BROKER, 8883, 60)
        client.loop_start()
    except Exception as e:
        print(f"Gagal konek MQTT: {e}")

# Koneksi dipanggil saat aplikasi dimulai
connect_mqtt()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    device = data.get('device')
    action = data.get('action')

    topic = f"tjkt/{device}/kontrol"
    client.publish(topic, action)
    return jsonify({"status": "success", "device": device, "action": action})

# Tidak perlu if __name__ == '__main__': di Vercel

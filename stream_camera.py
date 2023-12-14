from flask import Flask, request, jsonify, render_template, Response
from flask_mqtt import Mqtt
import base64
from PIL import Image
import io
import threading
import cv2
import numpy as np
import matplotlib.pyplot as plt


class ImageToMqtt():
	def __init__(self):
		self.image_data_content = ''
		self.video_data_content = ''

app = Flask(__name__)
img_mqtt = ImageToMqtt()

app.config['MQTT_BROKER_URL'] = 'b37.mqtt.one'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = '138chw3762'
app.config['MQTT_PASSWORD'] = '350bghjqvx'
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your server supports TLS, set it True
topic = "138chw3762/rgbcamera"

mqtt_client = Mqtt(app)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topic) 
   else:
       print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    base64_image = message.payload.decode()
    image_bytes = base64.b64decode(base64_image)

    img_mqtt.image_data_content = "data:image/jpeg;base64, " + base64.b64encode(image_bytes).decode()
    img_mqtt.video_data_content = np.array(Image.open(io.BytesIO(image_bytes)))



@app.route('/')
def index():
    return render_template('index.html', image_data=img_mqtt.image_data_content)


def gen():
    while True:
        hsv_image = cv2.cvtColor(img_mqtt.video_data_content, cv2.COLOR_BGR2RGBA)

        _, buffer = cv2.imencode('.jpg', hsv_image)

        frame = buffer.tobytes()

        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
   app.run(host='127.0.0.1', port=1975)


# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Image Stream</title>
# </head>
# <body>
#     <div class="container">
#         <div class="row">
#             <div class="col-lg-8  offset-lg-2">
#                 <h3 class="mt-5">Live Streaming</h3>
#                 <img src="{{ image_data }}" width="50%">
#                 <img src="{{ url_for('video_feed') }}" width="50%">
#             </div>
#         </div>
#     </div>
#     </body>
# </html>

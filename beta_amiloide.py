from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from gpiozero import RGBLED
from colorzero import Color
import json
import time
import ssl

led = RGBLED(*range(22, 25), active_high=False)
archivo_configuracion = '/home/pi/beta_amiloide.json'

with open(archivo_configuracion, 'r') as conf:
    conf_json = json.load(conf)
    color = Color(*conf_json['color'])
    dormir = 0.5 / conf_json['freq']


class MiServidor(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')

    def do_POST(self):
        self.send_response(200)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        global dormir, color
        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        color = Color(*payload['color'])
        dormir = 0.5 / payload['freq']

        with open(archivo_configuracion, 'w') as conf:
            conf_json = {
                'color': [ color.r, color.g, color.b ],
                'freq': 0.5 / dormir
            }
            json.dump(conf_json, conf, indent=4)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()


direccion_server = ('raspberrypi.local', 8000)
httpd = HTTPServer(direccion_server, MiServidor)
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile='/home/pi/.ssl/key.pem', certfile='/home/pi/.ssl/cert.pem', server_side=True)
hilo_server = Thread(target=httpd.serve_forever)
hilo_server.start()
print('Server encendido en {}:{}'.format(*direccion_server))

try:
    while True:
        led.color = color
        time.sleep(dormir)
        led.off()
        time.sleep(dormir)
        pass
except KeyboardInterrupt:
    pass

httpd.shutdown()
hilo_server.join()
print('Ayooooos')

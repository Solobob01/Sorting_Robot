#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from searchByNumber import numberSort
from searchByColor import colorSort
from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import argv
import serial
import logging
import json
import time


arduino = serial.Serial(port = '/dev/ttyS9',baudrate = 9600, timeout=0)
time.sleep(2)

def callRightFunction(sortMode):
    if sortMode == 'color' :
        print("COLOR MODE HAS BEEN CHOSEN!")
        colorSort(arduino, 'linux')
    elif sortMode == 'number' :
        print("NUMBER MODE HAS BEEN CHOSEN!")
        numberSort(arduino)
    elif sortMode == 'wave':
        print("WaVE MODE HSA BEEN CHOSEN")
        #waveMode(arduino)
    else:
        print("INCORECT MODE")


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        #logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        data = json.loads(post_data.decode('utf-8'))
        #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                #str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        callRightFunction(data['mode'])

        

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('130.89.132.207', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')
    arduino.close()

if __name__ == '__main__':
    print("SERVER IS RUNNING!")
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
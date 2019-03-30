import tornado.ioloop
import tornado.web
import os
import uuid
import base64
import socketserver
from threading import Thread
from time import sleep
import time


shared = {'client': None, 'result': None}


def main_handler(predict, remote_predictions=True):
    global shared

    class MainHandler(tornado.web.RequestHandler):
        def post(self):
            photo = self.get_argument('photo', 'No data received')

            if remote_predictions:
                if not shared['client']:
                    raise Exception('no connected client')
                shared['client'].send((photo + "EEENNNDDD").encode())
                shared['result'] = None
                start = time.clock()
                while not shared['result']:
                    if (time.clock() - start) >= 2:
                        raise Exception('timeout')
                self.finish(shared['result'])
            else:
                imgdata = base64.b64decode(photo)
                cname = str(uuid.uuid4()) + ".jpg"
                filepath = '/tmp/' + cname
                with open(filepath, 'wb') as f:
                    f.write(imgdata)
                print("Uploaded to", filepath)
                predictions = predict(filepath)
                self.finish({'predictions': predictions})

    return MainHandler


class TCPRemotePredictionsHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global shared
        while 1:
            self.data = self.request.recv(1024)
            if not self.data:
                shared['client'] = None
                print(self.client_address[0] + " disconnected")
                break
            data = self.data.strip().decode()
            print("data", data)
            shared['client'] = self.request
            if data == 'connect':
                print(str(self.client_address[0]), "connected")
            else:
                shared['result'] = data


class HealthCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('OK')


def start(predict):
    remote_predictions = True

    app = tornado.web.Application([
        (r"/predict", main_handler(predict, remote_predictions)),
        (r"/healthcheck", HealthCheckHandler),
        (r'/(.*)', tornado.web.StaticFileHandler,
         {'path': 'public', "default_filename": "index.html"}),
    ])
    http_server = tornado.httpserver.HTTPServer(app, ssl_options={
        "certfile": "certs/example.crt",
        "keyfile": "certs/example.key",
    })
    port = os.getenv("PORT") or 3000
    http_server.listen(port)
    tcp_server = socketserver.TCPServer(
        ("localhost", port + 1), TCPRemotePredictionsHandler)
    if remote_predictions:
        thread1 = Thread(target=tcp_server.serve_forever)
        thread2 = Thread(target=tornado.ioloop.IOLoop.current().start)
        thread1.start()
        thread2.start()
    else:
        tornado.ioloop.IOLoop.current().start()
    print("Server listening at https://localhost:" +
          str(port) + " http://localhost:" + str(port + 1))

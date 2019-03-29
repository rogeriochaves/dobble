import tornado.ioloop
import tornado.web
import os
import uuid
import base64


def main_handler(predict):
    class MainHandler(tornado.web.RequestHandler):
        def post(self):
            photo = self.get_argument('photo', 'No data received')
            imgdata = base64.b64decode(photo)
            cname = str(uuid.uuid4()) + ".jpg"
            filepath = '/tmp/' + cname
            with open(filepath, 'wb') as f:
                f.write(imgdata)
            print("Uploaded to", filepath)
            predictions = predict(filepath)

            self.finish({'predictions': predictions})
    return MainHandler


class HealthCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('OK')


def start(predict):
    app = tornado.web.Application([
        (r"/predict", main_handler(predict)),
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
    print("Server listening at https://localhost:" + str(port))
    tornado.ioloop.IOLoop.current().start()

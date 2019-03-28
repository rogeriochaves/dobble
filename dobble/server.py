import tornado.ioloop
import tornado.web
import os
import uuid


def main_handler(predict):
    class MainHandler(tornado.web.RequestHandler):
        def post(self):
            fileinfo = self.request.files['photo'][0]
            print("fileinfo is", fileinfo)
            fname = fileinfo['filename']
            extn = os.path.splitext(fname)[1]
            cname = str(uuid.uuid4()) + extn
            filepath = '/tmp/' + cname
            with open(filepath, 'wb') as out:
                body = fileinfo['body']
                out.write(body)
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
    port = os.getenv("PORT") or 3000
    app.listen(port)
    print("Server listening at http://localhost:" + str(port))
    tornado.ioloop.IOLoop.current().start()

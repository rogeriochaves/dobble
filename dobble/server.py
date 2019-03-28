import tornado.ioloop
import tornado.web
import os


def main_handler(predict):
    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            # title = self.get_arguments("title")[0]
            predictions = predict('custom_pics/IMG_3515.jpg')

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

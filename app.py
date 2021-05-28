from fuprox import app
import eventlet.wsgi

if __name__ == "__main__":
    # app.run("0.0.0.0", port=65123)
    eventlet.wsgi.server(eventlet.listen(('', 65123)), app)

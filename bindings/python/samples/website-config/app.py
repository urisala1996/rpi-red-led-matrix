from flask import Flask
from views import views

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.register_blueprint(views, url_prefix="/")


if __name__ == '__main__':
    app.run(host='192.168.42.1', port=8000, debug=True, threaded=False)

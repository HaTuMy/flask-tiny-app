from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "XIN CHÀO CÁC BẠN!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    app.run(debug=True)

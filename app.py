
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def home(): return render_template("index.html")

@app.route("/features")
def features(): return render_template("features.html")

@app.route("/download")
def download(): return render_template("download.html")

@app.route("/docs")
def docs(): return render_template("docs.html")

@app.route("/tutorials")
def tutorials(): return render_template("tutorials.html")

@app.route("/pricing")
def pricing(): return render_template("pricing.html")

if __name__ == "__main__":
    app.run(debug=True)

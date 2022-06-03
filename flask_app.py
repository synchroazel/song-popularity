from flask import Flask, render_template

app = Flask(__name__)

payload = {'your_songs': ['Song1', 'Song2'],
           'your_genres': ['Rock', 'Prog']}


@app.route('/')
def index():
    return render_template('index.html', value=payload)

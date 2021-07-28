from flask import Flask, request
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def test():
    return 'hello!!'


if __name__ == '__main__':
    app.run(debug=True)
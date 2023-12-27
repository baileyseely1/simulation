from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route('/get-data', methods=['GET'])
def get_data():
    try:
        with open('channel_data.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"error": "Data not available or file not found"}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

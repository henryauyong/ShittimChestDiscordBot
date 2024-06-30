from flask import Flask, request
import json
from dctoken import *

TOKEN = server_token
app = Flask(__name__)

@app.route('/', methods=['POST'])
def get_raid_data():
    token = request.headers.get('Token')
    if token != TOKEN:
        return 'Invalid Token'
    result = 'OK'
    if request.is_json:
        data = request.get_json()
        filename = data['File']
        with open(f'raid_data/{filename}', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(data)
    else:
        result = 'Not JSON Data'
    return result

if __name__ == "__main__":
    app.run("0.0.0.0", 9876)
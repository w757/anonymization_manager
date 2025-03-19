from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Docelowy URL API
TARGET_API_URL = 'http://localhost:5000'

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    # Przechwyć żądanie od klienta
    headers = dict(request.headers)
    data = request.get_json() if request.is_json else request.form.to_dict()
    
    # Modyfikuj dane na podstawie Swaggera (przykład)
    if path == 'register' and request.method == 'POST':
        if 'email' in data:
            data['email'] = data['email'].lower()  # Przykład modyfikacji: zamiana email na małe litery
    
    # Przekaż żądanie do docelowego API
    response = requests.request(
        method=request.method,
        url=f'{TARGET_API_URL}/{path}',
        headers=headers,
        json=data if request.is_json else None,
        data=data if not request.is_json else None
    )
    
    # Przekaż odpowiedź z docelowego API do klienta
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(port=5001, debug=True)
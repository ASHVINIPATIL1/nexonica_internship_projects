from flask import Flask, request, jsonify

app = Flask(__name__)
users = []
auto_id = 1

@app.route('/add_user', methods=['POST'])
def add_user():
    global auto_id
    data = request.get_json()
    user = {
        'id': auto_id,
        'username': data.get('username'),
        'email': data.get('email'),
        'phone' : data.get('phone'),
        'password': data.get('password')
    }
    users.append(user) 
    auto_id += 1
    return jsonify({'message': 'User loged in successfully', 'user': user}) 

@app.route('/get_user', methods=['GET'])
def get_user():
    return users

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
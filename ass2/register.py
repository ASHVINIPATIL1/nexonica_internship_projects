from flask import Flask, request, jsonify

app = Flask(__name__)
users = []
auto_id = 1

@app.route('/')
def index():
    return "Welcome to the User Management API"

@app.route('/register', methods=['POST'])
def register():
    global auto_id
    data = request.get_json()

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message' : 'missing required fields'}), 400
    
    for user in users:
        if user['email'] == data['email']:
            return jsonify({'message' : 'email already exists'}), 400

    user = {
        'id' : auto_id,
        'username' : data.get('username'),
        'email' : data.get('email'),
        'phone' : data.get('phone'),
        'password' : data.get('password')
    }

    users.append(user)
    auto_id += 1
    return jsonify({'message' : 'user registered succesfully', 'user_id' : user[id]}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or data.get('email') or not data.get('password'):
        return jsonify({'message' : 'email and password required'}), 400
    
    for user in users:
        if user['email'] == data['email'] and user['password'] == data['password']:
            return jsonify({'message' : 'login successfull', 'user_id' : user['id'], 'username' : user['username']}), 200
    
    return jsonify({'message' : 'invalid email or password'}), 401

@app.route('/users', methods=['GET'])
def get_users():
    for user in users:
        if user in users:
            return jsonify(users), 200
        else:
            return jsonify({'message' : 'no users found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
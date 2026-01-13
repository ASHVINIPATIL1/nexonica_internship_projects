from flask import Flask, request,jsonify
app = Flask(__name__)
employees = []
auto_id =1

@app.route('/add_emp', methods=['POST'])
def add_emp():
    global auto_id
    data = request.get_json()
    emp = {
        'id': auto_id,
        'name': data.get('name'),
        'email': data.get('email'),
        'salary': data.get('salary')
    }
    employees.append(emp)
    auto_id += 1
    return jsonify ({'message': 'Employee added successfully', 'employee': emp})

@app.route('/get_emp', methods=['GET'])
def get_emp():
    return employees        

if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=5000, debug=True)
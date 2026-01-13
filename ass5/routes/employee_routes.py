from flask import Blueprint, request, jsonify
from models.employee import db, Employee

employee_bp = Blueprint("employee_bp", __name__)

# -------------------------
# GET all employees
# -------------------------
@employee_bp.route("/employees", methods=["GET"])
def get_employees():
    employees = Employee.query.all()

    result = []
    for emp in employees:
        result.append({
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "salary": emp.salary
        })

    return jsonify(result), 200


# -------------------------
# POST new employee
# -------------------------
@employee_bp.route("/employees", methods=["POST"])
def add_employee():
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    email = data.get("email")
    salary = data.get("salary")

    if not name or not email or not salary:
        return jsonify({"error": "All fields are required"}), 400

    new_employee = Employee(
        name=name,
        email=email,
        salary=salary
    )

    db.session.add(new_employee)
    db.session.commit()

    return jsonify({
        "message": "Employee added successfully",
        "employee": {
            "id": new_employee.id,
            "name": new_employee.name,
            "email": new_employee.email,
            "salary": new_employee.salary
        }
    }), 201

from flask import Flask, jsonify

app = Flask(__name__)

employees = [
    {"id": 1, "name": "Rahul", "department": "IT"},
    {"id": 2, "name": "Priya", "department": "HR"},
    {"id": 3, "name": "Amit", "department": "Finance"}
]


@app.route("/")
def home():
    return jsonify({"status": "Employee API is running - Jenkins webhook test successful!"})


@app.route("/health")
def health():
    return jsonify({"status": "UP"}), 200


@app.route("/employees")
def get_employees():
    return jsonify(employees), 200


@app.route("/employees/<int:employee_id>")
def get_employee(employee_id):
    employee = next(
        (emp for emp in employees if emp["id"] == employee_id),
        None
    )

    if employee:
        return jsonify(employee), 200

    return jsonify({"error": "Employee not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

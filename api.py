"""
REST API for the mechanic shop app.

Reads DATABASE_URL from the environment so you can point this at SQLite
today and Postgres later with zero code changes:

    # SQLite (default, good for testing)
    python3 api.py

    # Postgres later
    export DATABASE_URL="postgresql://user:password@localhost:5432/mechanic_shop"
    python3 api.py

Serves the frontend (static/index.html, style.css, app.js) and exposes
JSON endpoints under /api/*.
"""
import os
from datetime import date

from flask import Flask, jsonify, request, send_from_directory
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker

# NOTE: this imports from "Final" to match the schema file already in your
# project. If you ever rename that file, update this import to match.
from Final import Customer, Employees, Appointments, NeededParts, Invoice, Parts, Base, get_engine, VALID_STATUSES

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///finalchat.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app = Flask(__name__, static_folder="static", static_url_path="")
engine = get_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_session():
    return Session()





# ---------------------------------------------------------------------------
# Lightweight migration: `Base.metadata.create_all` only creates tables that
# don't exist yet, it never alters an existing table. The Customer model
# grew new optional vehicle-detail columns, so on an existing finalchat.db
# we add them here if they're missing. Safe to run every time.
# ---------------------------------------------------------------------------

def ensure_customer_vehicle_columns():
    inspector = inspect(engine)
    existing_cols = {c["name"] for c in inspector.get_columns("Customer")}
    new_columns = {
        "vehicle_year": "INTEGER",
        "vehicle_make": "VARCHAR",
        "vehicle_model": "VARCHAR",
        "vehicle_color": "VARCHAR",
        "license_plate": "VARCHAR",
        "vin": "VARCHAR",
    }
    missing = {name: coltype for name, coltype in new_columns.items() if name not in existing_cols}
    if not missing:
        return
    with engine.begin() as conn:
        for name, coltype in missing.items():
            conn.execute(text(f'ALTER TABLE "Customer" ADD COLUMN {name} {coltype}'))
    print(f"Migrated Customer table: added {', '.join(missing)}.")


ensure_customer_vehicle_columns()


# ---------------------------------------------------------------------------
# Static frontend
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

@app.route("/api/employees", methods=["GET"])
def get_employees():
    session = get_session()
    try:
        employees = session.query(Employees).all()
        return jsonify([{
            "id": e.Employee_ID,
            "first_name": e.f_name,
            "last_name": e.L_name,
            "labor_hours": e.labor_hours,
            "hourly_rate": float(e.hourly_rate),
        } for e in employees])
    finally:
        session.close()


@app.route("/api/employees", methods=["POST"])
def add_employee():
    data = request.get_json(force=True)
    for field in ("first_name", "last_name"):
        if not data.get(field, "").strip():
            return jsonify({"error": f"{field} is required"}), 400

    session = get_session()
    try:
        employee = Employees(
            f_name=data["first_name"].strip(),
            L_name=data["last_name"].strip(),
            labor_hours=int(data.get("labor_hours") or 0),
            hourly_rate=float(data.get("hourly_rate") or 50.0),
        )
        session.add(employee)
        session.commit()
        return jsonify({"id": employee.Employee_ID}), 201
    except (ValueError, TypeError):
        return jsonify({"error": "labor_hours and hourly_rate must be numbers"}), 400
    finally:
        session.close()


@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    session = get_session()
    try:
        employee = session.query(Employees).filter(Employees.Employee_ID == employee_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
        session.delete(employee)
        session.commit()
        return jsonify({"deleted": employee_id})
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

def _customer_to_dict(c):
    return {
        "id": c.customer_ID,
        "first_name": c.C_f_name,
        "last_name": c.C_l_name,
        "email": c.email,
        "automobile_type": c.Automobile_type,
        "vehicle_year": c.vehicle_year,
        "vehicle_make": c.vehicle_make,
        "vehicle_model": c.vehicle_model,
        "vehicle_color": c.vehicle_color,
        "license_plate": c.license_plate,
        "vin": c.vin,
    }


@app.route("/api/customers", methods=["GET"])
def get_customers():
    session = get_session()
    try:
        search = request.args.get("search", "").strip().lower()
        customers = session.query(Customer).all()
        if search:
            customers = [
                c for c in customers
                if search in c.C_f_name.lower()
                or search in c.C_l_name.lower()
                or search in c.email.lower()
                or (c.license_plate and search in c.license_plate.lower())
                or (c.vehicle_make and search in c.vehicle_make.lower())
                or (c.vehicle_model and search in c.vehicle_model.lower())
            ]
        return jsonify([_customer_to_dict(c) for c in customers])
    finally:
        session.close()


@app.route("/api/customers", methods=["POST"])
def add_customer():
    data = request.get_json(force=True)
    required = ("first_name", "last_name", "email", "automobile_type")
    missing = [f for f in required if not data.get(f, "").strip()]
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    session = get_session()
    try:
        vehicle_year = data.get("vehicle_year")
        if vehicle_year not in (None, ""):
            try:
                vehicle_year = int(vehicle_year)
            except (ValueError, TypeError):
                return jsonify({"error": "vehicle_year must be a whole number"}), 400
        else:
            vehicle_year = None

        customer = Customer(
            C_f_name=data["first_name"].strip(),
            C_l_name=data["last_name"].strip(),
            email=data["email"].strip(),
            Automobile_type=data["automobile_type"].strip(),
            vehicle_year=vehicle_year,
            vehicle_make=(data.get("vehicle_make") or "").strip() or None,
            vehicle_model=(data.get("vehicle_model") or "").strip() or None,
            vehicle_color=(data.get("vehicle_color") or "").strip() or None,
            license_plate=(data.get("license_plate") or "").strip() or None,
            vin=(data.get("vin") or "").strip() or None,
        )
        session.add(customer)
        session.commit()
        return jsonify({"id": customer.customer_ID}), 201
    finally:
        session.close()


@app.route("/api/customers/<int:customer_id>", methods=["PATCH"])
def update_customer(customer_id):
    data = request.get_json(force=True)
    session = get_session()
    try:
        customer = session.query(Customer).filter(Customer.customer_ID == customer_id).first()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        string_fields = {
            "first_name": "C_f_name",
            "last_name": "C_l_name",
            "email": "email",
            "automobile_type": "Automobile_type",
        }
        for field, attr in string_fields.items():
            if field in data:
                value = (data.get(field) or "").strip()
                if not value:
                    return jsonify({"error": f"{field} can't be empty"}), 400
                setattr(customer, attr, value)

        optional_string_fields = {
            "vehicle_make": "vehicle_make",
            "vehicle_model": "vehicle_model",
            "vehicle_color": "vehicle_color",
            "license_plate": "license_plate",
            "vin": "vin",
        }
        for field, attr in optional_string_fields.items():
            if field in data:
                setattr(customer, attr, (data.get(field) or "").strip() or None)

        if "vehicle_year" in data:
            vehicle_year = data.get("vehicle_year")
            if vehicle_year in (None, ""):
                customer.vehicle_year = None
            else:
                try:
                    customer.vehicle_year = int(vehicle_year)
                except (ValueError, TypeError):
                    return jsonify({"error": "vehicle_year must be a whole number"}), 400

        session.commit()
        return jsonify(_customer_to_dict(customer))
    finally:
        session.close()


@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    session = get_session()
    try:
        customer = session.query(Customer).filter(Customer.customer_ID == customer_id).first()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        session.delete(customer)
        session.commit()
        return jsonify({"deleted": customer_id})
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------

DEFAULT_PARTS = [
    {"Part_name": "Oil Filter", "part_price": 10},
    {"Part_name": "Air Filter", "part_price": 15},
    {"Part_name": "Spark Plug", "part_price": 8},
    {"Part_name": "Brake Pad", "part_price": 40},
    {"Part_name": "Battery", "part_price": 120},
    {"Part_name": "Alternator", "part_price": 150},
    {"Part_name": "Radiator", "part_price": 200},
    {"Part_name": "Fuel Pump", "part_price": 180},
    {"Part_name": "Timing Belt", "part_price": 70},
    {"Part_name": "Windshield Wiper", "part_price": 25},
]


def seed_parts_if_empty():
    session = get_session()
    try:
        if session.query(Parts).count() == 0:
            for p in DEFAULT_PARTS:
                session.add(Parts(Part_name=p["Part_name"], part_price=p["part_price"]))
            session.commit()
    finally:
        session.close()


@app.route("/api/parts", methods=["GET"])
def get_parts():
    session = get_session()
    try:
        parts = session.query(Parts).all()
        return jsonify([{
            "id": p.part_id,
            "name": p.Part_name,
            "price": float(p.part_price),
        } for p in parts])
    finally:
        session.close()


@app.route("/api/parts", methods=["POST"])
def add_part():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    try:
        price = float(data.get("price"))
    except (TypeError, ValueError):
        return jsonify({"error": "price must be a number"}), 400
    if price < 0:
        return jsonify({"error": "price can't be negative"}), 400

    session = get_session()
    try:
        if session.query(Parts).filter(Parts.Part_name == name).first():
            return jsonify({"error": f"A part named '{name}' already exists"}), 409
        part = Parts(Part_name=name, part_price=price)
        session.add(part)
        session.commit()
        return jsonify({"id": part.part_id, "name": part.Part_name, "price": float(part.part_price)}), 201
    finally:
        session.close()


@app.route("/api/parts/<int:part_id>", methods=["PATCH"])
def update_part(part_id):
    data = request.get_json(force=True)
    session = get_session()
    try:
        part = session.query(Parts).filter(Parts.part_id == part_id).first()
        if not part:
            return jsonify({"error": "Part not found"}), 404

        if "name" in data:
            name = (data.get("name") or "").strip()
            if not name:
                return jsonify({"error": "name can't be empty"}), 400
            existing = session.query(Parts).filter(Parts.Part_name == name, Parts.part_id != part_id).first()
            if existing:
                return jsonify({"error": f"A part named '{name}' already exists"}), 409
            part.Part_name = name

        if "price" in data:
            try:
                price = float(data.get("price"))
            except (TypeError, ValueError):
                return jsonify({"error": "price must be a number"}), 400
            if price < 0:
                return jsonify({"error": "price can't be negative"}), 400
            part.part_price = price

        session.commit()
        return jsonify({"id": part.part_id, "name": part.Part_name, "price": float(part.part_price)})
    finally:
        session.close()


@app.route("/api/parts/<int:part_id>", methods=["DELETE"])
def delete_part(part_id):
    session = get_session()
    try:
        part = session.query(Parts).filter(Parts.part_id == part_id).first()
        if not part:
            return jsonify({"error": "Part not found"}), 404
        session.delete(part)
        session.commit()
        return jsonify({"deleted": part_id})
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Appointments (+ auto-generated invoice)
# ---------------------------------------------------------------------------

@app.route("/api/appointments", methods=["GET"])
def get_appointments():
    session = get_session()
    try:
        appointments = session.query(Appointments).all()
        result = []
        for a in appointments:
            result.append({
                "id": a.appointment_id,
                "customer_id": a.customer_id,
                "customer_name": f"{a.customer.C_f_name} {a.customer.C_l_name}",
                "employee_id": a.EmployeeID,
                "employee_name": f"{a.employee.f_name} {a.employee.L_name}",
                "status": a.Status,
                "date": a.Date.isoformat(),
                "labor_hours_billed": a.labor_hours_billed,
            })
        return jsonify(result)
    finally:
        session.close()


@app.route("/api/appointments", methods=["POST"])
def add_appointment():
    data = request.get_json(force=True)
    required = ("customer_id", "employee_id", "status", "date", "labor_hours_billed")
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    if data["status"] not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of {VALID_STATUSES}"}), 400

    try:
        appt_date = date.fromisoformat(data["date"])
    except ValueError:
        return jsonify({"error": "date must be in YYYY-MM-DD format"}), 400

    session = get_session()
    try:
        customer = session.query(Customer).filter(Customer.customer_ID == data["customer_id"]).first()
        if not customer:
            return jsonify({"error": "customer_id not found"}), 404
        employee = session.query(Employees).filter(Employees.Employee_ID == data["employee_id"]).first()
        if not employee:
            return jsonify({"error": "employee_id not found"}), 404

        labor_hours_billed = int(data["labor_hours_billed"])

        appointment = Appointments(
            customer_id=customer.customer_ID,
            Status=data["status"],
            EmployeeID=employee.Employee_ID,
            Date=appt_date,
            labor_hours_billed=labor_hours_billed,
        )
        session.add(appointment)
        session.flush()  # get appointment_id before commit

        parts_cost = 0.0
        for item in data.get("parts", []):
            part = session.query(Parts).filter(Parts.part_id == item["part_id"]).first()
            if not part:
                session.rollback()
                return jsonify({"error": f"part_id {item['part_id']} not found"}), 404
            qty = int(item.get("quantity", 1))
            session.add(NeededParts(part_id=part.part_id, appoinment_id=appointment.appointment_id, quantity=qty))
            parts_cost += float(part.part_price) * qty

        labor_cost = float(employee.hourly_rate) * labor_hours_billed
        total_cost = parts_cost + labor_cost

        invoice = Invoice(
            appioment_id=appointment.appointment_id,
            customer_id=customer.customer_ID,
            parts_cost=parts_cost,
            labor_cost=labor_cost,
            TotalCost=total_cost,
        )
        session.add(invoice)

        employee.labor_hours += labor_hours_billed
        session.commit()

        return jsonify({
            "appointment_id": appointment.appointment_id,
            "invoice_total": total_cost,
        }), 201
    except (ValueError, TypeError) as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@app.route("/api/appointments/<int:appointment_id>", methods=["PATCH"])
def update_appointment_status(appointment_id):
    data = request.get_json(force=True)
    new_status = data.get("status")
    if new_status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of {VALID_STATUSES}"}), 400

    session = get_session()
    try:
        appointment = session.query(Appointments).filter(Appointments.appointment_id == appointment_id).first()
        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404
        appointment.Status = new_status
        session.commit()
        return jsonify({"id": appointment_id, "status": new_status})
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

@app.route("/api/invoices", methods=["GET"])
def get_invoices():
    session = get_session()
    try:
        invoices = session.query(Invoice).all()
        return jsonify([{
            "appointment_id": inv.appioment_id,
            "customer_id": inv.customer_id,
            "customer_name": f"{inv.customer.C_f_name} {inv.customer.C_l_name}",
            "parts_cost": float(inv.parts_cost),
            "labor_cost": float(inv.labor_cost),
            "total_cost": float(inv.TotalCost),
            "paid": bool(inv.paid),
        } for inv in invoices])
    finally:
        session.close()


@app.route("/api/invoices/<int:appointment_id>", methods=["GET"])
def get_invoice_detail(appointment_id):
    session = get_session()
    try:
        invoice = session.query(Invoice).filter(Invoice.appioment_id == appointment_id).first()
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
        appointment = session.query(Appointments).filter(Appointments.appointment_id == appointment_id).one()
        needed = session.query(NeededParts).filter(NeededParts.appoinment_id == appointment_id).all()

        return jsonify({
            "appointment_id": appointment_id,
            "customer_name": f"{invoice.customer.C_f_name} {invoice.customer.C_l_name}",
            "employee_name": f"{appointment.employee.f_name} {appointment.employee.L_name}",
            "date": appointment.Date.isoformat(),
            "status": appointment.Status,
            "parts": [{
                "name": np.part.Part_name,
                "quantity": np.quantity,
                "unit_price": float(np.part.part_price),
                "subtotal": float(np.part.part_price) * np.quantity,
            } for np in needed],
            "labor_hours_billed": appointment.labor_hours_billed,
            "hourly_rate": float(appointment.employee.hourly_rate),
            "parts_cost": float(invoice.parts_cost),
            "labor_cost": float(invoice.labor_cost),
            "total_cost": float(invoice.TotalCost),
            "paid": bool(invoice.paid),
        })
    finally:
        session.close()


@app.route("/api/invoices/<int:appointment_id>", methods=["PATCH"])
def mark_invoice_paid(appointment_id):
    session = get_session()
    try:
        invoice = session.query(Invoice).filter(Invoice.appioment_id == appointment_id).first()
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
        invoice.paid = 1
        session.commit()
        return jsonify({"appointment_id": appointment_id, "paid": True})
    finally:
        session.close()


if __name__ == "__main__":
    seed_parts_if_empty()
    app.run(debug=True, port=5000)
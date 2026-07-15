from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datetime import date

from Final import Customer, Employees, Appointments, NeededParts, Invoice, Parts, Base, get_engine, VALID_STATUSES

engine = get_engine()
Base.metadata.create_all(engine)  # creates tables on first run, no-op if they already exist
Session = sessionmaker(bind=engine)
session = Session()

DEFAULT_PARTS = [
    {'Part_name': 'Oil Filter', 'part_price': 10},
    {'Part_name': 'Air Filter', 'part_price': 15},
    {'Part_name': 'Spark Plug', 'part_price': 8},
    {'Part_name': 'Brake Pad', 'part_price': 40},
    {'Part_name': 'Battery', 'part_price': 120},
    {'Part_name': 'Alternator', 'part_price': 150},
    {'Part_name': 'Radiator', 'part_price': 200},
    {'Part_name': 'Fuel Pump', 'part_price': 180},
    {'Part_name': 'Timing Belt', 'part_price': 70},
    {'Part_name': 'Windshield Wiper', 'part_price': 25},
]


def seed_parts():
    """Only inserts default parts that don't already exist, so re-running is safe."""
    existing_names = {p.Part_name for p in session.query(Parts.Part_name).all()}
    added = 0
    for part in DEFAULT_PARTS:
        if part['Part_name'] not in existing_names:
            session.add(Parts(Part_name=part['Part_name'], part_price=part['part_price']))
            added += 1
    if added:
        session.commit()
        print(f"Seeded {added} new part(s).")


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def prompt_int(message, allow_blank=False):
    while True:
        raw = input(message).strip()
        if allow_blank and raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number.")


def prompt_float(message, default=None):
    while True:
        raw = input(message).strip()
        if raw == "" and default is not None:
            return default
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number.")


def prompt_nonempty(message):
    while True:
        raw = input(message).strip()
        if raw:
            return raw
        print("This field can't be empty.")


def prompt_date(message):
    while True:
        raw = input(message).strip()
        try:
            return date.fromisoformat(raw)
        except ValueError:
            print("Please use YYYY-MM-DD format.")


def prompt_choice(message, options):
    options_display = "/".join(options)
    while True:
        raw = input(f"{message} ({options_display}): ").strip()
        for opt in options:
            if raw.lower() == opt.lower():
                return opt
        print(f"Please choose one of: {options_display}")


def prompt_existing_id(message, valid_ids):
    """Keeps asking until the user gives an ID that's actually in valid_ids."""
    while True:
        val = prompt_int(message)
        if val in valid_ids:
            return val
        print("That ID doesn't exist. Please pick one from the list above.")


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

def add_employee():
    f_name = prompt_nonempty("Enter the first name of the employee: ")
    l_name = prompt_nonempty("Enter the last name of the employee: ")
    labor_hours = prompt_int("Enter starting logged labor hours (0 if new): ")
    hourly_rate = prompt_float("Enter hourly rate (default $50): ", default=50.00)
    new_employee = Employees(f_name=f_name, L_name=l_name, labor_hours=labor_hours, hourly_rate=hourly_rate)
    session.add(new_employee)
    session.commit()
    print(f"Employee added successfully! (ID: {new_employee.Employee_ID})")


def list_employees():
    employees = session.query(Employees).all()
    if not employees:
        print("No employees on file yet.")
        return employees
    print(f'{"ID":<6}{"Name":<25}{"Rate/hr":<10}{"Logged Hrs":<12}')
    print('-' * 53)
    for e in employees:
        print(f'{e.Employee_ID:<6}{e.f_name + " " + e.L_name:<25}${float(e.hourly_rate):<9.2f}{e.labor_hours:<12}')
    return employees


def delete_employee():
    employees = list_employees()
    if not employees:
        return
    emp_id = prompt_existing_id("Enter the Employee ID to delete: ", {e.Employee_ID for e in employees})
    emp = session.query(Employees).filter(Employees.Employee_ID == emp_id).one()
    confirm = input(f"Delete {emp.f_name} {emp.L_name}? This also deletes their appointments/invoices. (y/n): ")
    if confirm.lower() == 'y':
        session.delete(emp)
        session.commit()
        print("Employee deleted.")


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

def add_customer():
    f_name = prompt_nonempty("Enter the first name of the customer: ")
    l_name = prompt_nonempty("Enter the last name of the customer: ")
    email = prompt_nonempty("Enter the email of the customer: ")
    automobile_type = prompt_nonempty("Enter the automobile type of the customer: ")
    new_customer = Customer(C_f_name=f_name, C_l_name=l_name, email=email, Automobile_type=automobile_type)
    session.add(new_customer)
    session.commit()
    print(f"Customer added successfully! (ID: {new_customer.customer_ID})")
    return new_customer.customer_ID


def list_customers():
    customers = session.query(Customer).all()
    if not customers:
        print("No customers on file yet.")
        return customers
    print(f'{"ID":<6}{"Name":<25}{"Email":<28}{"Vehicle":<15}')
    print('-' * 74)
    for c in customers:
        print(f'{c.customer_ID:<6}{c.C_f_name + " " + c.C_l_name:<25}{c.email:<28}{c.Automobile_type:<15}')
    return customers


def search_customers():
    term = prompt_nonempty("Search by name or email (partial match ok): ").lower()
    matches = [
        c for c in session.query(Customer).all()
        if term in c.C_f_name.lower() or term in c.C_l_name.lower() or term in c.email.lower()
    ]
    if not matches:
        print("No matches found.")
        return []
    print(f'{"ID":<6}{"Name":<25}{"Email":<28}{"Vehicle":<15}')
    print('-' * 74)
    for c in matches:
        print(f'{c.customer_ID:<6}{c.C_f_name + " " + c.C_l_name:<25}{c.email:<28}{c.Automobile_type:<15}')
    return matches


def delete_customer():
    customers = list_customers()
    if not customers:
        return
    cust_id = prompt_existing_id("Enter the Customer ID to delete: ", {c.customer_ID for c in customers})
    cust = session.query(Customer).filter(Customer.customer_ID == cust_id).one()
    confirm = input(f"Delete {cust.C_f_name} {cust.C_l_name}? This also deletes their appointments/invoices. (y/n): ")
    if confirm.lower() == 'y':
        session.delete(cust)
        session.commit()
        print("Customer deleted.")


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------

def list_parts():
    parts = session.query(Parts).all()
    print(f'{"Part ID":<10}{"Name":<25}{"Price":<10}')
    print('-' * 45)
    for part in parts:
        print(f'{part.part_id:<10}{part.Part_name:<25}${float(part.part_price):<10.2f}')
    return parts


def choose_parts(appointment_id):
    parts = list_parts()
    valid_ids = {p.part_id for p in parts}
    chosen = {}  # part_id -> quantity
    while True:
        raw = input("Enter the Part ID to add (or 'done' to finish): ").strip()
        if raw.lower() == 'done':
            break
        try:
            part_id = int(raw)
        except ValueError:
            print("Please enter a numeric Part ID or 'done'.")
            continue
        if part_id not in valid_ids:
            print("Invalid Part ID. Please try again.")
            continue
        qty = prompt_int(f"Quantity for part {part_id} (default 1): ", allow_blank=True) or 1
        chosen[part_id] = chosen.get(part_id, 0) + qty

    for part_id, qty in chosen.items():
        session.add(NeededParts(part_id=part_id, appoinment_id=appointment_id, quantity=qty))
    if chosen:
        session.commit()
        print("Parts added to the appointment successfully!")
    return chosen


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

def create_invoice(appointment_id, customer_id, chosen_parts, labor_hours, hourly_rate):
    parts_cost = 0.0
    for part_id, qty in chosen_parts.items():
        part = session.query(Parts).filter(Parts.part_id == part_id).one()
        parts_cost += float(part.part_price) * qty

    labor_cost = float(hourly_rate) * labor_hours
    total_cost = parts_cost + labor_cost

    new_invoice = Invoice(
        appioment_id=appointment_id,
        customer_id=customer_id,
        parts_cost=parts_cost,
        labor_cost=labor_cost,
        TotalCost=total_cost,
    )
    session.add(new_invoice)
    session.commit()
    print(f"Invoice created! Parts: ${parts_cost:.2f} + Labor: ${labor_cost:.2f} = ${total_cost:.2f}")


def list_invoices():
    invoices = session.query(Invoice).all()
    if not invoices:
        print("No invoices yet.")
        return invoices
    print(f'{"Cust ID":<10}{"Customer Name":<25}{"Total":<10}{"Paid":<6}')
    print('-' * 51)
    for invoice in invoices:
        customer = session.query(Customer).filter(Customer.customer_ID == invoice.customer_id).one()
        paid_label = "Yes" if invoice.paid else "No"
        print(f'{invoice.customer_id:<10}{customer.C_f_name + " " + customer.C_l_name:<25}${float(invoice.TotalCost):<9.2f}{paid_label:<6}')
    return invoices


def mark_invoice_paid():
    invoices = list_invoices()
    if not invoices:
        return
    appt_id = prompt_int("Enter the Appointment ID of the invoice to mark paid: ")
    invoice = session.query(Invoice).filter(Invoice.appioment_id == appt_id).first()
    if not invoice:
        print("No invoice found for that appointment.")
        return
    invoice.paid = 1
    session.commit()
    print("Invoice marked as paid.")


def print_invoice(appointment_id):
    invoice = session.query(Invoice).filter(Invoice.appioment_id == appointment_id).first()
    if not invoice:
        print("No invoice found for that appointment.")
        return
    customer = session.query(Customer).filter(Customer.customer_ID == invoice.customer_id).one()
    appointment = session.query(Appointments).filter(Appointments.appointment_id == appointment_id).one()
    employee = session.query(Employees).filter(Employees.Employee_ID == appointment.EmployeeID).one()
    needed = session.query(NeededParts).filter(NeededParts.appoinment_id == appointment_id).all()

    print("\nInvoice Details:")
    print(f"Customer: {customer.C_f_name} {customer.C_l_name}")
    print(f"Employee: {employee.f_name} {employee.L_name}")
    print(f"Appointment Date: {appointment.Date}   Status: {appointment.Status}")
    print(f"\n{'Part Name':<25}{'Qty':<6}{'Price':<10}{'Subtotal':<10}")
    print('-' * 51)
    for np in needed:
        part = session.query(Parts).filter(Parts.part_id == np.part_id).one()
        subtotal = float(part.part_price) * np.quantity
        print(f'{part.Part_name:<25}{np.quantity:<6}${float(part.part_price):<9.2f}${subtotal:<9.2f}')
    print(f"\nLabor: {appointment.labor_hours_billed} hr(s) @ ${float(employee.hourly_rate):.2f}/hr = ${float(invoice.labor_cost):.2f}")
    print(f"Parts total: ${float(invoice.parts_cost):.2f}")
    print(f"TOTAL: ${float(invoice.TotalCost):.2f}")
    print(f"Paid: {'Yes' if invoice.paid else 'No'}\n")


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------

def set_up_appointment():
    print("1. Add a new customer")
    print("2. Use an existing customer")
    print("3. Search for a customer")
    choice = input("Enter your choice: ").strip()

    if choice == '1':
        customer_id = add_customer()
    elif choice == '2':
        customers = list_customers()
        if not customers:
            return
        customer_id = prompt_existing_id("Enter the existing customer ID: ", {c.customer_ID for c in customers})
    elif choice == '3':
        matches = search_customers()
        if not matches:
            return
        customer_id = prompt_existing_id("Enter the customer ID from the results: ", {c.customer_ID for c in matches})
    else:
        print("Invalid choice. Returning to main menu.")
        return

    status = prompt_choice("Enter the status of the appointment", VALID_STATUSES)

    employees = list_employees()
    if not employees:
        print("You need at least one employee before booking an appointment.")
        return
    employee_id = prompt_existing_id("Enter the employee ID: ", {e.Employee_ID for e in employees})
    employee = session.query(Employees).filter(Employees.Employee_ID == employee_id).one()

    appointment_date = prompt_date("Enter the date of the appointment (YYYY-MM-DD): ")
    labor_hours_billed = prompt_int("Enter labor hours to bill for this job: ")

    new_appointment = Appointments(
        customer_id=customer_id,
        Status=status,
        EmployeeID=employee_id,
        Date=appointment_date,
        labor_hours_billed=labor_hours_billed,
    )
    session.add(new_appointment)
    session.commit()
    print(f"Appointment set up successfully! (ID: {new_appointment.appointment_id})")

    chosen_parts = choose_parts(new_appointment.appointment_id)
    create_invoice(new_appointment.appointment_id, customer_id, chosen_parts, labor_hours_billed, employee.hourly_rate)

    # Track hours on the employee record too
    employee.labor_hours += labor_hours_billed
    session.commit()


def update_appointment_status():
    appts = session.query(Appointments).all()
    if not appts:
        print("No appointments yet.")
        return
    print(f'{"ID":<6}{"Customer":<10}{"Status":<15}{"Date":<12}')
    print('-' * 43)
    for a in appts:
        print(f'{a.appointment_id:<6}{a.customer_id:<10}{a.Status:<15}{str(a.Date):<12}')
    appt_id = prompt_existing_id("Enter the Appointment ID to update: ", {a.appointment_id for a in appts})
    new_status = prompt_choice("New status", VALID_STATUSES)
    appt = session.query(Appointments).filter(Appointments.appointment_id == appt_id).one()
    appt.Status = new_status
    session.commit()
    print("Status updated.")


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

def main():
    seed_parts()
    menu = {
        '1': ("Add an employee", add_employee),
        '2': ("Delete an employee", delete_employee),
        '3': ("Set up an appointment", set_up_appointment),
        '4': ("Update appointment status", update_appointment_status),
        '5': ("Print an invoice", None),  # handled specially below
        '6': ("Mark an invoice as paid", mark_invoice_paid),
        '7': ("Search customers", search_customers),
        '8': ("Delete a customer", delete_customer),
        '9': ("Exit", None),
    }

    while True:
        print("\nPlease choose an option:")
        for key, (label, _) in menu.items():
            print(f"{key}. {label}")
        choice = input("Enter your choice: ").strip()

        if choice not in menu:
            print("Invalid choice. Please try again.")
            continue

        if choice == '5':
            invoices = list_invoices()
            if not invoices:
                continue
            customer_id = prompt_int("Enter the customer ID to print the invoice: ")
            invoice = session.query(Invoice).filter(Invoice.customer_id == customer_id).first()
            if not invoice:
                print("No invoice found for that customer.")
                continue
            print_invoice(invoice.appioment_id)
        elif choice == '9':
            print("Exiting the program.")
            break
        else:
            menu[choice][1]()


if __name__ == '__main__':
    main()
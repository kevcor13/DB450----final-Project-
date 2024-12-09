from sqlalchemy.orm import sessionmaker
from Final import Customer, Employees, Appointments, NeededParts, Invoice
from sqlalchemy import create_engine, func
import logging
#logging.basicConfig()
#logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
import random 
from datetime import date

# creates connection to DataBase
engine = create_engine('sqlite:///finalchat.db')
Session = sessionmaker(bind=engine)
session = Session()
###########################################################################
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Final import Parts

# List of commonly needed parts
parts = [
    {'Part_name': 'Oil Filter', 'part_price': 10},
    {'Part_name': 'Air Filter', 'part_price': 15},
    {'Part_name': 'Spark Plug', 'part_price': 8},
    {'Part_name': 'Brake Pad', 'part_price': 40},
    {'Part_name': 'Battery', 'part_price': 120},
    {'Part_name': 'Alternator', 'part_price': 150},
    {'Part_name': 'Radiator', 'part_price': 200},
    {'Part_name': 'Fuel Pump', 'part_price': 180},
    {'Part_name': 'Timing Belt', 'part_price': 70},
    {'Part_name': 'Windshield Wiper', 'part_price': 25}
]

# Add parts to the database
for part in parts:
    new_part = Parts(Part_name=part['Part_name'], part_price=part['part_price'])
    session.add(new_part)

session.commit()
print("Parts added successfully!")

#########################################################################################

SERVICE_FEE = 100

def add_employee():
    f_name = input("Enter the first name of the employee: ")
    l_name = input("Enter the last name of the employee: ")
    labor_hours = int(input("Enter the labor hours: "))
    new_employee = Employees(f_name=f_name, L_name=l_name, labor_hours=labor_hours)
    session.add(new_employee)
    session.commit()
    print("Employee added successfully!")

def add_customer():
    f_name = input("Enter the first name of the customer: ")
    l_name = input("Enter the last name of the customer: ")
    email = input("Enter the email of the customer: ")
    automobile_type = input("Enter the automobile type of the customer: ")
    new_customer = Customer(C_f_name=f_name, C_l_name=l_name, email=email, Automobile_type=automobile_type)
    session.add(new_customer)
    session.commit()
    print("Customer added successfully!")
    return new_customer.customer_ID

def list_parts():
    parts = session.query(Parts).all()
    print(f'{"Part ID":<10}{"Name":<25}{"Price":<10}')
    print('-' * 45)
    for part in parts:
        print(f'{part.part_id:<10}{part.Part_name:<25}${part.part_price:<10}')
    return parts

def choose_parts(appointment_id):
    parts = list_parts()
    chosen_parts = []
    while True:
        part_id = input("Enter the Part ID to add to the appointment (or 'done' to finish): ")
        if part_id.lower() == 'done':
            break
        part_id = int(part_id)
        if any(part.part_id == part_id for part in parts):
            chosen_parts.append(part_id)
        else:
            print("Invalid Part ID. Please try again.")
    
    for part_id in chosen_parts:
        new_needed_part = NeededParts(part_id=part_id, appoinment_id=appointment_id)
        session.add(new_needed_part)
    session.commit()
    print("Parts added to the appointment successfully!")
    return chosen_parts

def create_invoice(appointment_id, customer_id, chosen_parts):
    total_cost = SERVICE_FEE
    for part_id in chosen_parts:
        part = session.query(Parts).filter(Parts.part_id == part_id).one()
        total_cost += part.part_price

    new_invoice = Invoice(
        appioment_id=appointment_id,
        customer_id=customer_id,
        TotalCost=total_cost
    )
    session.add(new_invoice)
    session.commit()
    print("Invoice created successfully!")

def list_invoices():
    invoices = session.query(Invoice).all()
    print(f'{"Customer ID":<15}{"Customer Name":<30}')
    print('-' * 45)
    for invoice in invoices:
        customer = session.query(Customer).filter(Customer.customer_ID == invoice.customer_id).one()
        print(f'{invoice.customer_id:<15}{customer.C_f_name} {customer.C_l_name}')
    return invoices



def print_invoice(appointment_id):
    invoice = session.query(Invoice).filter(Invoice.appioment_id == appointment_id).one()
    customer = session.query(Customer).filter(Customer.customer_ID == invoice.customer_id).one()
    appointment = session.query(Appointments).filter(Appointments.appointment_id == appointment_id).one()
    employee = session.query(Employees).filter(Employees.Employee_ID == appointment.EmployeeID).one()
    parts = session.query(NeededParts).filter(NeededParts.appoinment_id == appointment_id).all()

    print("\nInvoice Details:")
    print(f"Customer: {customer.C_f_name} {customer.C_l_name}")
    print(f"Employee: {employee.f_name} {employee.L_name}")
    print(f"{'Part Name':<25}{'Price':<10}")
    print('-' * 35)
    for needed_part in parts:
        part = session.query(Parts).filter(Parts.part_id == needed_part.part_id).one()
        print(f'{part.Part_name:<25}${part.part_price:<10}')
    print(f"\nService Fee: ${SERVICE_FEE}")
    print(f"Total Cost: ${invoice.TotalCost}\n")

def list_customers():
    customers = session.query(Customer).all()
    print(f'{"Customer ID":<15}{"Customer Name":<30}')
    for customer in customers:
        print(f'{customer.customer_ID:<15}{customer.C_f_name} {customer.C_l_name}')
    return customers

def list_employees():
    employees = session.query(Employees).all()
    print(f'{"Employee ID":<15}{"Employee Name":<30}')
    print('-' * 45)
    for employee in employees:
        print(f'{employee.Employee_ID:<15}{employee.f_name} {employee.L_name}')
    return employees



def set_up_appointment():
    print("1. Add a new customer")
    print("2. Use an existing customer")
    choice = input("Enter your choice: ")

    if choice == '1':
        customer_id = add_customer()
    elif choice == '2':
        list_customers()
        customer_id = int(input("Enter the existing customer ID: "))
    else:
        print("Invalid choice. Returning to main menu.")
        return

    status = input("Enter the status of the appointment: ")

    # Listing current employees with their IDs
    list_employees()
    employee_id = int(input("Enter the employee ID: "))

    date_str = input("Enter the date of the appointment (YYYY-MM-DD): ")
    appointment_date = date.fromisoformat(date_str)
    new_appointment = Appointments(
        customer_id=customer_id,
        Status=status,
        EmployeeID=employee_id,
        Date=appointment_date
    )
    session.add(new_appointment)
    session.commit()
    print("Appointment set up successfully!")

    chosen_parts = choose_parts(new_appointment.appointment_id)
    create_invoice(new_appointment.appointment_id, customer_id, chosen_parts)
    



def main():
    while True:
        print("\nPlease choose an option:")
        print("1. Add an employee")
        print("2. Set up an appointment")
        print("3. Print an invoice")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            add_employee()
        elif choice == '2':
            set_up_appointment()
        elif choice == '3':
            invoices = list_invoices()
            customer_id = int(input("Enter the customer ID to print the invoice: "))
            print("\n" * 10)  # Adding gap between the list and the input
            invoice = session.query(Invoice).filter(Invoice.customer_id == customer_id).one()
            print_invoice(invoice.appioment_id)
        elif choice == '4':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")



if __name__ == '__main__':
    main()


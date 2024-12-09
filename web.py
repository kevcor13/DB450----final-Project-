from sqlalchemy.orm import sessionmaker
from Final import Customer, Employees, Appointments, Invoice
from sqlalchemy import create_engine, func
import logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
import random 
from datetime import date

# creates connection to DataBase
engine = create_engine('sqlite:///finalchat.db')
Session = sessionmaker(bind=engine)
session = Session()

def main_menu():
    print("Welcome to you Database")
    print("1. Make appointment")
    print("2. Add employee ")
    print("3. get invoice")
    
    choice = input("Enter choice: ")

    if choice == "1":
        ## chech if the customer is new or not ##
        answer = input("new client (yes or no): ")
        ## if new make add him to database ##
        if answer == "yes":
             make_appointment()
        ## else go straight to making appointment ##
        else:
            c_id = input("what is customers number: ")
            i = input("which enployee has worked on this (enter number): ")
            e_id = int(i)
            add_appointment(c_id, e_id)
    elif choice == "2":
        add_employee()
    elif choice == "3":
        get_invoice()
        print("")
    else:
        print("invalid option. please select a valid option")


def add_employee():
    f_name = input("Enter first name: ").strip()
    L_name = input("Enter Last name: ").strip()
    s_labor_hrs = input("Enter the amount of labor hours: ").strip()
    labor_hours = int(s_labor_hrs)
    employeeID = random.randint(1,1000)
    employee = Employees(Employee_ID = employeeID,f_name=f_name, L_name=L_name, labor_hours=labor_hours)
    session.add(employee)
    session.commit()
    print(f"employee has been added ")


def make_appointment():
    C_f_name = input("Enter client first name: ").strip()
    C_l_name = input("Enter client last name: ").strip()
    email = input("Email: ")
    Automobile_type = input("Enter make and model: ")
    #customer_ID = random.randint(1,1000)
    customer = Customer(C_f_name=C_f_name, C_l_name=C_l_name,email=email,Automobile_type=Automobile_type)
    session.add(customer)
    session.commit()
    print(f"Customer {customer.customer_ID} added")
    add_appointment(customer.customer_ID,Employees.Employee_ID)

    
def add_appointment(customer_id, employee_id):
    print(f'{employee_id}')
    appointment_id = random.randint(1,1000)
    print("choose status:")
    status = input("Not started, In progress, Complete: ")
    ## get the current date of it was scheduled ##
    i = date.today()
    ## put it into right format##
    current_date = i.strftime("%Y-%m-%d")

    appointment = Appointments(customer_id=customer_id, Status=status, EmployeeID=employee_id, Date=current_date )
    session.add(appointment)
    session.commit()
    print("appointment was made")
    create_invoice(appointment.appointment_id, appointment.customer_id)

def create_invoice(appointment_id, customer_id):
    p = input("Enter a price: ")
    price = int(p)
    invoice = Invoice(appioment_id=appointment_id, customer_id=customer_id, TotalCost=price)
    session.add(invoice)
    session.commit()
    print("invoice was made")

def get_invoice():
    o = input("Enter appointment ID: ")
    appoioment_id = int(o)
    invoice = session.query(Invoice).filter_by(appioment_id=appoioment_id).first()
    if invoice:
         print(f"\n ----Invoice for {invoice.appioment_id}")
         print(f"customer name :{invoice.customer_id} ")
         print(f"Total cost: {invoice.TotalCost}")
    else:
        print("problem getting invoice")


if __name__ == "__main__":
    main_menu()

# Mechanic Shop Database 
A full-featured database system built with **Python** and **SQLAlchemy** to help manage a mechanic shop’s daily operations—tracking customers, employees, appointments, parts used, and generating invoices.

## Overview/Features 
This project is a small command-line information system for an auto shop. It allows for storing data information, tracking invoices in a locla SQLite database (finalchat.db) via SQLAlchemy models and provides a basic menu

This command-line application provides tools for:
- Add and manage customers and employees
- Managing customer and employee records
- Relational links between customers, appointments, employees, and parts
- Scheduling service appointments
- Automatically generating service invoices
- Viewing historical data in a structured format

It’s designed to simulate a real-world mechanic shop’s backend operations with a focus on data consistency.

## Programming Languages used 
- Python
- SQLite
- SQLAlchemy


## Data models
* Parts - common part names
* employees - staff members with tracked labor hours
* Customers - customer tracking with personal data
* Appointments - track scheduled appointments
* Invocies - keeping track of work/hours for a job with invoices

## Usage
Once we run the script we will see a menu like the one below with the given options: 
<img width="285" height="82" alt="Screenshot 2025-12-10 at 3 58 08 PM" src="https://github.com/user-attachments/assets/916db0b8-8e89-4a37-9d9f-787e56758e49" />

1) Add an employee
   * First name
   * Last name
   * Labor hours
This stores the employee in the Employees table which can be seen/used later

2) Set up Appointment
   * Choose ( Add new customer / Choose existing customer )
   * Enter Appointment Status - (Scheduled/In Progres/Completed)
   * Pick an employee (Employees will be listed)
   * Enter Appointment Date - (in specific format)
   * Choose parts needed for the appointment (With parts ID/Prices, that are shown on screen)
   * Invoice is automatically created

3) Print Invoice
   * Enter customer ID
   * It will print an invoice showing:
       * Customer name
       * Employee name
       * List of parts and prices
       * Service Fee
       * Total cost


## SetUp Instructions
Prerequisites 
* pythosn 3.10+

1) Clone the repository
2) Install Dependencies
- pip install sqlalchemy
3) Run the program
- python main.py

## Example 

1) Add Employee 
<img width="325" height="136" alt="Screenshot 2025-12-10 at 4 11 52 PM" src="https://github.com/user-attachments/assets/49a72169-f521-4038-a6fa-2c9d08bd9ee3" />

2) Set up Appointment
<img width="440" height="407" alt="Screenshot 2025-12-10 at 4 16 08 PM" src="https://github.com/user-attachments/assets/bbbfb517-fb53-4f09-b967-9795acf7ca7d" />
<img width="516" height="675" alt="Screenshot 2025-12-10 at 4 16 47 PM" src="https://github.com/user-attachments/assets/1834de0f-9253-4c69-a86d-149f506f1125" />

3) Print invoice
<img width="351" height="463" alt="Screenshot 2025-12-10 at 4 17 16 PM" src="https://github.com/user-attachments/assets/27da46a6-a138-4c81-b0eb-c723749e709e" />

## Author 

Author: Kevin Cordero 
Email: kevincordero11.KC@gmail.com



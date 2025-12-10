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

Please choose an option:
1. Add an employee
2. Set up an appointment
3. Print an invoice
4. Exit
Enter your choice: 2
1. Add a new customer
2. Use an existing customer
Enter your choice: 2
Customer ID    Customer Name                 
817            Andrea Zuniga
818            Kevin Cordero
819            Kevin Cordero
820            jorge clas
821            carlos truro
822            andrea zuniga
823            dan clim
824            kelly yung
Enter the existing customer ID: 818
Enter the status of the appointment: In Progress
Employee ID    Employee Name                 
---------------------------------------------
131            kadcgfkds Vsdchsdcquez
121            Javn Vqz
68             kevin cordero
220            Omar Cordero
Enter the employee ID: 68
Enter the date of the appointment (YYYY-MM-DD): 2025-12-10
Appointment set up successfully!
Part ID   Name                     Price     
---------------------------------------------
1         Oil Filter               $10        
2         Air Filter               $15        
3         Spark Plug               $8         
4         Brake Pad                $40        
5         Battery                  $120       
6         Alternator               $150       
7         Radiator                 $200       
8         Fuel Pump                $180       
9         Timing Belt              $70        
10        Windshield Wiper         $25        
11        Oil Filter               $10        
12        Air Filter               $15        
13        Spark Plug               $8         
14        Brake Pad                $40        
15        Battery                  $120       
16        Alternator               $150       
17        Radiator                 $200       
18        Fuel Pump                $180       
19        Timing Belt              $70        
20        Windshield Wiper         $25        
21        Oil Filter               $10        
22        Air Filter               $15        
23        Spark Plug               $8         
24        Brake Pad                $40        
25        Battery                  $120       
26        Alternator               $150       
27        Radiator                 $200       
28        Fuel Pump                $180       
29        Timing Belt              $70        
30        Windshield Wiper         $25        
31        Oil Filter               $10        
32        Air Filter               $15        
33        Spark Plug               $8         
34        Brake Pad                $40        
35        Battery                  $120       
36        Alternator               $150       
37        Radiator                 $200       
38        Fuel Pump                $180       
39        Timing Belt              $70        
40        Windshield Wiper         $25        
Enter the Part ID to add to the appointment (or 'done' to finish): 10
Enter the Part ID to add to the appointment (or 'done' to finish): 13 
Enter the Part ID to add to the appointment (or 'done' to finish): 40
Enter the Part ID to add to the appointment (or 'done' to finish): done
Parts added to the appointment successfully!
Invoice created successfully!

3) Print invoice
   Please choose an option:
1. Add an employee
2. Set up an appointment
3. Print an invoice
4. Exit
Enter your choice: 3
Customer ID    Customer Name                 
---------------------------------------------
822            andrea zuniga
819            Kevin Cordero
818            Kevin Cordero
Enter the customer ID to print the invoice: 819












Invoice Details:
Customer: Kevin Cordero
Employee: kevin cordero
Part Name                Price     
-----------------------------------

Service Fee: $100
Total Cost: $700


## Author 

Author: Kevin Cordero 
Email: kevincordero11.KC@gmail.com



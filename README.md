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

## SetUp Instructions
Prerequisites 
* pythosn 3.10+

1) Clone the repository
2) Install Dependencies
- pip install sqlalchemy
3) Run the program
- python main.py

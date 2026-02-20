# AGENT.md

## Purpose
This project is a CLI mechanic shop system using SQLAlchemy + SQLite. It manages:
- employees
- customers
- appointments
- parts used per appointment
- invoice totals

Main files:
- `Final.py`: ORM models and table creation
- `web.py`: CLI workflow and business logic
- `finalchat.db`: SQLite database file
- `README.md`: user-facing overview

## How The Project Runs
1. `web.py` imports models from `Final.py`.
2. `Final.py` defines SQLAlchemy models and runs `Base.metadata.create_all(engine)`.
3. `web.py` creates a DB session and seeds parts at startup (currently always inserts the same 10 parts each run).
4. The `main()` menu in `web.py` handles user actions:
   - add employee
   - set up appointment
   - print invoice

Run command:
- `python web.py`

## Data Model (Current Live Schema)
Tables in `finalchat.db`:
- `Parts(part_id, Part_name, part_price)`
- `Employees(Employee_ID, f_name, L_name, labor_hours)`
- `Customer(customer_ID, C_f_name, C_l_name, email, Automobile_type)`
- `Appointments(appointment_id, customer_id, Status, EmployeeID, Date)`
- `NeededParts(part_id, appoinment_id)`
- `Invoice(appioment_id, customer_id, TotalCost)`

Important naming quirks (do not "fix" without coordinated code+DB migration):
- `NeededParts.appoinment_id` is misspelled in code/schema.
- `Invoice.appioment_id` is misspelled in code/schema.
- These are actively used in queries and relationships.

## Key Logic In `web.py`
- `add_employee()` inserts row in `Employees`.
- `add_customer()` inserts row in `Customer` and returns `customer_ID`.
- `set_up_appointment()`:
  - picks/creates customer
  - picks employee
  - creates `Appointments` row
  - collects part IDs via `choose_parts()`
  - generates invoice via `create_invoice()`
- `create_invoice()`:
  - starts with `SERVICE_FEE = 100`
  - adds selected part prices
  - writes total into `Invoice`
- `print_invoice()` joins appointment, customer, employee, and needed parts for output.

## Modification Guide

### 1) Adding a new field to a model
Example: add phone number to customer.
1. Add column in `Final.py` model class.
2. Handle value in related CLI functions in `web.py`.
3. Migrate DB:
   - for this project size, easiest is recreate DB in dev, or
   - run explicit SQL migration for existing data.
4. Update any printed table views and README docs.

### 2) Changing invoice math
- Edit `SERVICE_FEE` and/or `create_invoice()` in `web.py`.
- Keep all totals as integers unless you intentionally migrate to decimals.
- Re-test appointment flow and invoice print flow.

### 3) Adding menu actions
- Add a new option in `main()`.
- Implement function above `main()`.
- Reuse session queries (`session.query(...)`) and commit only when needed.

### 4) Preventing duplicate parts seed data
Current behavior: every run inserts the same parts again.
Safer approach:
- before seeding, check if `Parts` already has rows.
- only insert defaults when count is zero.

### 5) Fixing naming typos safely
Do not rename only in Python code. Use a migration plan:
1. create new columns/tables with corrected names
2. backfill data
3. update ORM + queries
4. validate reads/writes
5. remove old names

## Known Risks / Current Issues
- Startup seeding duplicates `Parts` entries on every run.
- Some schema types are inconsistent (example: IDs showing as `VARCHAR` in live DB where code expects integers).
- `Date` column is string-based in schema; input uses ISO format and should remain consistent (`YYYY-MM-DD`).
- There is limited input validation (non-numeric IDs or invalid references can crash).

## Safe Workflow For Future Edits
1. Read `Final.py` and `web.py` together before changing one side.
2. If schema changes are needed, decide migration strategy first.
3. Make small changes and test full menu flow:
   - add employee
   - set appointment with parts
   - print invoice
4. Keep naming consistent with existing DB unless performing a full migration.
5. Update README when behavior changes.

## Suggested Immediate Improvements
- add a seeding guard for `Parts`
- add input validation and error handling (`try/except` around integer parsing and `.one()` calls)
- use SQLAlchemy `Date` type for appointment date
- standardize ID column types and naming via migration

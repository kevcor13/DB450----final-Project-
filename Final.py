from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, Date, Numeric, CheckConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Allowed appointment statuses (used for a CHECK constraint + CLI validation)
VALID_STATUSES = ("Scheduled", "In Progress", "Completed", "Cancelled")


class Parts(Base):
    __tablename__ = 'Parts'
    part_id = Column(Integer, primary_key=True, autoincrement=True)
    Part_name = Column(String, nullable=False, unique=True)
    part_price = Column(Numeric(10, 2), nullable=False)

    needed_parts = relationship('NeededParts', back_populates='part', cascade="all, delete-orphan")


class Employees(Base):
    __tablename__ = 'Employees'
    Employee_ID = Column(Integer, primary_key=True, autoincrement=True)
    f_name = Column(String, nullable=False)
    L_name = Column(String, nullable=False)
    labor_hours = Column(Integer, nullable=False, default=0)
    hourly_rate = Column(Numeric(10, 2), nullable=False, default=50.00)

    appointments = relationship('Appointments', back_populates='employee', cascade="all, delete-orphan")


class Customer(Base):
    __tablename__ = 'Customer'
    customer_ID = Column(Integer, primary_key=True, autoincrement=True)
    C_f_name = Column(String, nullable=False)
    C_l_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    Automobile_type = Column(String, nullable=False)

    # Extra vehicle detail — all optional so existing rows / older callers
    # that only set Automobile_type keep working.
    vehicle_year = Column(Integer, nullable=True)
    vehicle_make = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    vehicle_color = Column(String, nullable=True)
    license_plate = Column(String, nullable=True)
    vin = Column(String, nullable=True)

    appointments = relationship('Appointments', back_populates='customer', cascade="all, delete-orphan")


class Appointments(Base):
    __tablename__ = 'Appointments'
    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('Customer.customer_ID'), nullable=False)
    Status = Column(String, nullable=False, default="Scheduled")
    EmployeeID = Column(Integer, ForeignKey('Employees.Employee_ID'), nullable=False)
    Date = Column(Date, nullable=False)
    labor_hours_billed = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        CheckConstraint(f"Status IN {VALID_STATUSES}", name="valid_status"),
    )

    customer = relationship('Customer', back_populates='appointments')
    employee = relationship('Employees', back_populates='appointments')
    needed_parts = relationship('NeededParts', back_populates='appointment', cascade="all, delete-orphan")
    invoice = relationship('Invoice', back_populates='appointment', uselist=False, cascade="all, delete-orphan")


class NeededParts(Base):
    __tablename__ = 'NeededParts'
    part_id = Column(Integer, ForeignKey('Parts.part_id'), primary_key=True)
    appoinment_id = Column(Integer, ForeignKey('Appointments.appointment_id'), primary_key=True)
    quantity = Column(Integer, nullable=False, default=1)

    part = relationship('Parts', back_populates='needed_parts')
    appointment = relationship('Appointments', back_populates='needed_parts')


class Invoice(Base):
    __tablename__ = 'Invoice'
    appioment_id = Column(Integer, ForeignKey('Appointments.appointment_id'), primary_key=True)
    customer_id = Column(Integer, ForeignKey('Customer.customer_ID'), nullable=False)
    parts_cost = Column(Numeric(10, 2), nullable=False, default=0)
    labor_cost = Column(Numeric(10, 2), nullable=False, default=0)
    TotalCost = Column(Numeric(10, 2), nullable=False)
    paid = Column(Integer, nullable=False, default=0)  # 0 = unpaid, 1 = paid

    customer = relationship('Customer')
    appointment = relationship('Appointments', back_populates='invoice')


def get_engine(db_path='sqlite:///finalchat.db'):
    return create_engine(db_path)


if __name__ == '__main__':
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Tables created (or already exist).")
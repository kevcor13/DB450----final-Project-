from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

# Define a base class for the models
Base = declarative_base()

# Define a User model
class Parts(Base):
    __tablename__ = 'Parts'
    part_id = Column(Integer, primary_key=True, autoincrement=True)
    Part_name = Column(String, nullable=False)
    part_price = Column(Integer, nullable=False)


# Employees table
class Employees(Base):
    __tablename__ = 'Employees'
    Employee_ID = Column(Integer, primary_key=True, autoincrement=True)
    f_name = Column(String, nullable=False)
    L_name = Column(String, nullable=False)
    labor_hours = Column(Integer, nullable=False)


# Customer table
class Customer(Base):
    __tablename__ = 'Customer'
    customer_ID = Column(Integer, primary_key=True, autoincrement=True)
    C_f_name = Column(String, nullable=False)
    C_l_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    Automobile_type = Column(String, nullable=False)


# Appointments table
class Appointments(Base):
    __tablename__ = 'Appointments'
    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('Customer.customer_ID'), nullable=False)
    Status = Column(String, nullable=False)
    EmployeeID = Column(Integer, ForeignKey('Employees.Employee_ID'), nullable=False)
    Date = Column(String, nullable=False)

    # Relationships
    customer = relationship('Customer', back_populates='appointments')
    employee = relationship('Employees', back_populates='appointments')


# NeededParts table
class NeededParts(Base):
    __tablename__ = 'NeededParts'
    part_id = Column(Integer, ForeignKey('Parts.part_id'), primary_key=True)
    appoinment_id = Column(Integer, ForeignKey('Appointments.appointment_id'), primary_key=True)

    # Relationships
    part = relationship('Parts', back_populates='needed_parts')
    appointment = relationship('Appointments', back_populates='needed_parts')


# Invoice table
class Invoice(Base):
    __tablename__ = 'Invoice'
    appioment_id = Column(Integer, ForeignKey('Appointments.appointment_id'), primary_key=True)
    customer_id = Column(Integer, ForeignKey('Customer.customer_ID'), nullable=False)
    TotalCost = Column(Integer, nullable=False)

    # Relationships
    customer = relationship('Customer')



# Adding back_populates relationships
Customer.appointments = relationship('Appointments', back_populates='customer', cascade="all, delete-orphan")
Employees.appointments = relationship('Appointments', back_populates='employee', cascade="all, delete-orphan")
Parts.needed_parts = relationship('NeededParts', back_populates='part', cascade="all, delete-orphan")
Appointments.needed_parts = relationship('NeededParts', back_populates='appointment', cascade="all, delete-orphan")
# Create a database engine
engine = create_engine('sqlite:///finalchat.db')

# Create all tables
Base.metadata.create_all(engine)

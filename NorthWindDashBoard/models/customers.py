from datetime import datetime
from typing import Optional
import reflex as rx
from sqlalchemy import LargeBinary
import sqlmodel


class Customers(rx.Model, table=True):  
  customer_id: Optional[int] = sqlmodel.Field(default=None, primary_key=True)
  company_name :str
  contact_name :str
  contact_title :str
  address:str
  city :str
  region :str
  postal_code :str
  country :str
  phone :str
  fax :str


class Employee(rx.Model, table=True):
    __tablename__ = 'employees'

    employee_id : Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    last_name :str
    first_name :str
    title : str #Column(String(30))
    title_of_courtesy:str #= Column(String(25))
    birth_date :str
    hire_date:str
    address:str
    city :str
    region :str
    postal_code :str
    country :str
    home_phone :str
    extension :str
    photo :bytes = sqlmodel.Field(sa_column=LargeBinary)
    #notes = Column(Text)
    #reports_to = Column(ForeignKey('employees.employee_id'))
    #photo_path = Column(String(255))

    #parent = relationship('Employee', remote_side=[employee_id])
    #territorys = relationship('Territory', secondary='employee_territories')


class Region(rx.Model, table=True):
    __tablename__ = 'region'

    region_id : Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    region_description:str # = Column(String(60), nullable=False)


class Shipper(rx.Model, table=True):
    __tablename__ = 'shippers'

    shipper_id : Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    company_name :str
    phone :str


class Supplier(rx.Model, table=True):
    __tablename__ = 'suppliers'

    supplier_id : Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    company_name :str
    contact_name :str
    contact_title :str
    address :str
    city :str
    region:str
    postal_code :str
    country :str
    phone:str
    fax :str
    homepage :str


class UsState(rx.Model, table=True):
    __tablename__ = 'us_states'

    state_id  : Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    state_name :str
    state_abbr:str
    state_region:str


class Order(rx.Model, table=True):
    __tablename__ = 'orders'

    order_id : Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    customer_id :int
    employee_id :int
    order_date : datetime
    required_date : datetime
    shipped_date : datetime
    ship_via :int
    freight :float
    ship_name :str
    ship_address:str
    ship_city :str
    ship_region :str
    ship_postal_code :str
    ship_country :str



class Product(rx.Model, table=True):
    __tablename__ = 'products'

    product_id : Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    product_name :str
    supplier_id :int
    category_id :int
    quantity_per_unit:str
    unit_price:float
    units_in_stock:int
    units_on_order:int
    reorder_level :int
    discontinued: int




class Territory(rx.Model, table=True):
    __tablename__ = 'territories'

    territory_id : Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    territory_description :str
    region_id :int



class OrderDetail(rx.Model, table=True):
    __tablename__ = 'order_details'

    order_id : Optional[int] = sqlmodel.Field(default=None, primary_key=True)
    product_id :int
    unit_price :float
    quantity :int
    discount:float

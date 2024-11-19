import reflex as rx
from ..models.customers import Employee
from ..templates.template import template
class EmployeeState(rx.State):
    employees:list[Employee]=[]

    def load_employees(self):
        with rx.session() as session:
           self.employees = session.exec(
                Employee.select()
            ).all() 


@template(route="/employees", title="Employees",on_load=EmployeeState.load_employees)
def main_table():
    return rx.fragment(
        rx.flex(         
         rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("Name"),
                    _header_cell("Birth Date"),
                    _header_cell("Hire Date"),  
                    _header_cell("Title")
                 
                ),
            ),
            rx.table.body(rx.foreach(EmployeeState.employees, show_employee)),
            variant="surface",
            size="3",
            width="100%"            
        ),
    ))

def show_employee(emp:Employee) -> rx.Component:
 return rx.table.row(
        rx.table.cell(emp.first_name + " " + emp.last_name),
        rx.table.cell(emp.birth_date),
        rx.table.cell(emp.hire_date),
        rx.table.cell(emp.title)
       
       
    )
def _header_cell(text: str):
    return rx.table.column_header_cell(
        rx.hstack(            
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )
     
    
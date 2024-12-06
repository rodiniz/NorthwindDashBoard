import reflex as rx
from ..models.customers import Employee
from ..templates.template import template
from datetime import datetime

class EmployeeState(rx.State):
    employees: list[Employee] = []
    show_modal: bool = False
    employee_id: int = 0
    first_name: str = ""
    last_name: str = ""
    title: str = ""
    birth_date: str = ""
    hire_date: str = ""

    def load_employees(self):
        with rx.session() as session:
            self.employees = session.exec(
                Employee.select()
            ).all()

    def toggle_modal(self):   
        self.reset_form()
        self.show_modal = not self.show_modal

    def reset_form(self):
        self.employee_id = 0
        self.first_name = ""
        self.last_name = ""
        self.title = ""
        self.birth_date = ""
        self.hire_date = ""

    def create_or_update_employee(self, form:dict):
        
        with rx.session() as session:
            if self.employee_id:
                # Update existing employee
                employee = session.get(Employee, self.employee_id)
                if employee:
                    employee.first_name = form["first_name"]
                    employee.last_name = form["last_name"]
                    employee.title = form["title"]
                    employee.birth_date = datetime.strptime(form["birth_date"], "%Y-%m-%d").date()
                    employee.hire_date = datetime.strptime(form["hire_date"], "%Y-%m-%d").date()
            else:
                # Create new employee
                employee = Employee(
                    first_name=form["first_name"],
                    last_name=form["last_name"],
                    title=form["title"],
                    birth_date=datetime.strptime(form["birth_date"], "%Y-%m-%d").date(),
                    hire_date=datetime.strptime(form["hire_date"], "%Y-%m-%d").date(),
                )
                session.add(employee)
            session.commit()
            
        self.show_modal = False
        # Reload employees
        self.load_employees()

    def edit_employee(self, employee: Employee):
        self.employee_id = employee.id
        self.first_name = employee.first_name
        self.last_name = employee.last_name
        self.title = employee.title
        self.birth_date = employee.birth_date.strftime("%Y-%m-%d")
        self.hire_date = employee.hire_date.strftime("%Y-%m-%d")
        self.show_modal = True

  

def create_employee_modal():
   return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=26),
                rx.text("Add Employee", size="4"),
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Add New User",
            ),
            rx.dialog.description(
                "Fill the form with the user's info",
            ),
            rx.form(
                rx.flex(
                    rx.input(
                        placeholder="First Name", name="first_name",
                        required=True
                    ),
                      rx.input(
                        placeholder="Last Name", name="last_name",
                        required=True
                    ),
                    rx.input(
                        placeholder="",
                        name="birth_date",
                        type="date",
                    ),
                     rx.input(
                        placeholder="",
                        name="hire_date",
                        type="date",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                color_scheme="gray",
                            ),
                        ),
                        rx.dialog.close(
                            rx.button(
                                "Save", type="submit"
                            ),
                        ),
                        spacing="3",
                        justify="end",
                    ),
                    direction="column",
                    spacing="4",
                ),
                on_submit=EmployeeState.create_or_update_employee,
                reset_on_submit=True,
            ),
            max_width="450px",
        ),
    )

@template(route="/employees", title="Employees",on_load=EmployeeState.load_employees)
def main_table():
    return rx.fragment(
        rx.flex(
            rx.button(
                "New Employee",
                on_click=EmployeeState.toggle_modal,
                color_scheme="blue",
                margin_bottom="4",
            ),
            create_employee_modal(),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        _header_cell("Name"),
                        _header_cell("Birth Date"),
                        _header_cell("Hire Date"),  
                        _header_cell("Title"),
                        _header_cell("Actions")
                    ),
                ),
                rx.table.body(rx.foreach(EmployeeState.employees, show_employee)),
                variant="surface",
                size="3",
                width="100%"            
            ),
        ),
    )

def show_employee(emp:Employee) -> rx.Component:
    return rx.table.row(
        rx.table.cell(emp.first_name + " " + emp.last_name),
        rx.table.cell(emp.birth_date),
        rx.table.cell(emp.hire_date),
        rx.table.cell(emp.title),
        rx.table.cell(
            rx.button(
                "Edit",
                on_click=lambda: EmployeeState.edit_employee(emp),
                color_scheme="blue",
            )
        )
    )

def _header_cell(text: str):
    return rx.table.column_header_cell(
        rx.hstack(            
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )
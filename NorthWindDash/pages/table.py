"""The table page."""

from ..templates import template
from ..backend.table_state import TableState


import reflex as rx


@template(route="/about", title="About", on_load=TableState.load_entries)
def table() -> rx.Component:
    """The table page.

    Returns:
        The UI for the table page.
    """
    return rx.vstack(
        rx.heading("About", size="5"),
        rx.text("This is the about page.", size="4"),
        rx.markdown("""
        # NorthWind Dashboard
        
        A modern, interactive dashboard application built with Reflex for analyzing the NorthWind database.
        
        ## Features
        
        - **Interactive Data Tables**: View and analyze NorthWind database information
        - **Modern UI Components**: Including sidebar navigation and responsive navbar
        - **Data Visualization**: Charts and graphs for data analysis
        - **Responsive Design**: Works seamlessly on desktop and mobile devices
        
        ## Technology Stack
        
        - **Backend**: Python with Reflex framework
        - **Database**: SQLAlchemy with Alembic migrations
        - **Frontend**: Reflex components for modern UI
        - **Styling**: Custom styles and base stylesheets
        
        ## Source code
        You can find the source code for this application on [GitHub](https://github.com/rodiniz/NorthWindDashBoard).
        """),
        spacing="8",
        width="100%",
    )

import reflex as rx
import os
database_url=os.getenv('database_url')
config = rx.Config(
    app_name="NorthWindDashBoard",
    db_url=database_url

)
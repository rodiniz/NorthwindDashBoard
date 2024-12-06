from pydantic import Field
import reflex as rx


class Categories(rx.Model, table=True):
   CategoryID: int = Field(primary_key=True)  # Primary Key
   CategoryName: str = Field(max_length=15, nullable=False)  # Category name with a character limit
   Description: str = Field(max_length=255)  # Optional description of the category
   Picture: bytes = Field(nullable=True)  # Picture as binary data, can be null~


  
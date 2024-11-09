"""The overview page of the app."""

import reflex as rx
from ..templates import template
from ..views.filters import filters
from ..views.stats_cards import stats_cards
from ..views.charts import (    
    revenue_chart,
    orders_chart,
    orders_table,
    StatsState,
)

from ..components.card import card
import datetime


def _time_data() -> rx.Component:
    return rx.hstack(
        rx.tooltip(
            rx.icon("info", size=20),
            content=f"{(datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%b %d, %Y')} - {datetime.datetime.now().strftime('%b %d, %Y')}",
        ),
        rx.text("Last 30 days", size="4", weight="medium"),
        align="center",
        spacing="2",
        display=["none", "none", "flex"],
    )


def tab_content_header() -> rx.Component:
    return rx.hstack(
        _time_data(),       
        align="center",
        width="100%",
        spacing="4",
    )

@template(route="/", title="Overview", on_load=StatsState.load_data)
def index() -> rx.Component:
    """The overview page.

    Returns:
        The UI for the overview page.
    """
    return rx.vstack(
        filters(),
        stats_cards(),
        card(
            rx.hstack(                
                rx.segmented_control.root(                   
                    rx.segmented_control.item("Revenue", value="revenue"),
                    rx.segmented_control.item("Orders", value="orders"),
                    margin_bottom="1.5em",
                    default_value=StatsState.selected_tab,
                    on_change=StatsState.set_selected_tab,
                ),
                width="100%",
                justify="between",
            ),           
            rx.match(
                StatsState.selected_tab,               
                ("revenue", revenue_chart()),
                ("orders", orders_chart()),
            ),
        ),
        card(
                rx.hstack(
                    rx.hstack(
                        rx.icon("user-round-search", size=20),
                        rx.text("Orders", size="4", weight="medium"),
                        rx.text("Order date", size="4", weight="small"),
                        rx.select(                            
                            StatsState.order_dates,
                            value=StatsState.order_date_selected,
                            size="3",
                            width="170px",
                            on_change= StatsState.order_id_change        
                        ),
                        rx.spinner(size="3",loading=StatsState.loading_orders),
                        align="center",
                        spacing="2",
                    ),                    
                    align="center",
                    width="100%",
                    justify="between",
                ),
                orders_table(),
            ),            
            gap="1rem",
            grid_template_columns=[
                "1fr",
                "repeat(1, 1fr)",
                "repeat(2, 1fr)",
                "repeat(2, 1fr)",
                "repeat(2, 1fr)",
            ],
            width="100%"     
    )

import reflex as rx

from NorthWindDashBoard.views.charts import StatsState
from .. import styles
def filters() -> rx.Component:
    return  rx.hstack(
        rx.card(
            rx.box(
                rx.heading("Filters"),
                rx.text("Year and month"),
                rx.select(
                    StatsState.order_dates,
                    value=StatsState.order_date_selected,
                    size="3",
                    width="130px",
                    on_change= StatsState.on_change        
                ),
                width="100%"
            ),
            width="100%",
            size="3",
            box_shadow=styles.box_shadow_style,
        )
    )
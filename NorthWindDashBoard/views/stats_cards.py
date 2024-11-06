import reflex as rx

from NorthWindDashBoard.views.charts import StatsState
from .. import styles


from reflex.components.radix.themes.base import LiteralAccentColor


def stats_card( 
    stat_name: str,
    value:int,   
    icon: str,
    icon_color: LiteralAccentColor,
    extra_char: str = ""    
) -> rx.Component:

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.icon(tag=icon, size=34),
                    color_scheme=icon_color,
                    radius="full",
                    padding="0.7rem",
                ),
                rx.vstack(
                    rx.heading(
                        f"{extra_char} {value:,}",
                        size="6",
                        weight="bold",
                    ),
                    rx.text(stat_name, size="4", weight="medium"),
                    spacing="1",
                    height="100%",
                    align_items="start",
                    width="100%",
                ),
                height="100%",
                spacing="4",
                align="center",
                width="100%",
            ),
           
            spacing="3",
        ),
        size="3",
        width="100%",
        box_shadow=styles.box_shadow_style,
    )

def stats_cards() -> rx.Component:
    return rx.grid(
        stats_card(
            stat_name="Users",         
            icon="users",
            icon_color="blue",
            value=StatsState.users_count
           
        ),
        stats_card(
            stat_name="Sales",               
            icon="dollar-sign",
            icon_color="green",
            value=StatsState.total_sales         
        ),
        stats_card(
            stat_name="Orders",          
            icon="shopping-cart",
            icon_color="purple",
            value=StatsState.orders_count
        ),
        gap="1rem",
        grid_template_columns=[
            "1fr",
            "repeat(1, 1fr)",
            "repeat(2, 1fr)",
            "repeat(3, 1fr)",
            "repeat(3, 1fr)",
        ],
        width="100%",
    )

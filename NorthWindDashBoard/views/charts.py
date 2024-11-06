import reflex as rx
from sqlalchemy import func
import pandas as pd
from reflex.components.radix.themes.base import (
    LiteralAccentColor,
)

from ..models.customers import Customers, Order


class StatsState(rx.State):
    area_toggle: bool = True
    selected_tab: str = "revenue"
    timeframe: str = "Monthly"
    users_data = []
    revenue_data = []
    orders_data = []
    device_data = []
    yearly_device_data = []
    users_count:int
    total_sales:float
    orders_count:int
    order_dates:list[str]=[]
    order_date_selected:str=""
    df_merged:pd.DataFrame=None
        
    def toggle_areachart(self):
        self.area_toggle = not self.area_toggle

    def load_data(self):      
       
        with rx.session() as session:
                self.users_count = session.exec(func.count(Customers.customer_id)).scalar()                
                df_orders = pd.read_sql('select * from orders',session.connection())
                df_orders['YearMonth']= pd.to_datetime(df_orders['order_date']).dt.strftime('%Y-%m')
                self.order_dates=df_orders['YearMonth'].unique().tolist()
                self.order_date_selected=df_orders.iloc[0]['YearMonth']
                self.load_by_date()
                
    def on_change(self,ev):
         self.order_date_selected=ev
         self.load_by_date()
        
    def load_by_date(self):
            with rx.session() as session:
                if self.df_merged is None:
                    df_orders = pd.read_sql('select * from orders',session.connection())
                    df = pd.read_sql('select * from order_details',session.connection())
                    self.df_merged= df.merge(df_orders)           

                self.df_merged['YearMonth']= pd.to_datetime(self.df_merged['order_date']).dt.strftime('%Y-%m')

                value= self.order_date_selected    
                df_filtered=self.df_merged.query("YearMonth==@value").copy()

                df_filtered['final_price']= df_filtered['unit_price'] * df_filtered['quantity']
                self.total_sales= df_filtered['final_price'].sum()             

                         
                self.orders_count=  len(df_filtered.groupby('order_id'))
                
                df_filtered['order_date']=df_filtered['order_date'].astype(str)
                # Step 5: Group by year-month and day, and sum the order amounts (Freight in this example)
                result = df_filtered.groupby(['order_date'])['final_price'].sum().reset_index()               
               
                result = result.rename(columns={
                    'final_price': 'revenue'                   
                })
                self.revenue_data=result.to_dict(orient='records')

                orders_result= df_filtered.groupby(['order_date'])['order_id'].count().reset_index()
                # number_of_orders
                orders_result = orders_result.rename(columns={
                    'order_id': 'number_of_orders'                   
                })
                self.orders_data=orders_result.to_dict(orient='records')      
                #print(orders_result.head())
                

                
def area_toggle() -> rx.Component:
    return rx.cond(
        StatsState.area_toggle,
        rx.icon_button(
            rx.icon("area-chart"),
            size="2",
            cursor="pointer",
            variant="surface",
            on_click=StatsState.toggle_areachart,
        ),
        rx.icon_button(
            rx.icon("bar-chart-3"),
            size="2",
            cursor="pointer",
            variant="surface",
            on_click=StatsState.toggle_areachart,
        ),
    )


def _create_gradient(color: LiteralAccentColor, id: str) -> rx.Component:
    return (
        rx.el.svg.defs(
            rx.el.svg.linear_gradient(
                rx.el.svg.stop(
                    stop_color=rx.color(color, 7), offset="5%", stop_opacity=0.8
                ),
                rx.el.svg.stop(stop_color=rx.color(color, 7), offset="95%", stop_opacity=0),
                x1=0,
                x2=0,
                y1=0,
                y2=1,
                id=id,
            ),
        ),
    )


def _custom_tooltip(color: LiteralAccentColor) -> rx.Component:
    return (
        rx.recharts.graphing_tooltip(
            separator=" : ",
            content_style={
                "backgroundColor": rx.color("gray", 1),
                "borderRadius": "var(--radius-2)",
                "borderWidth": "1px",
                "borderColor": rx.color(color, 7),
                "padding": "0.5rem",
                "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
            },
            is_animation_active=True,
        ),
    )




def revenue_chart() -> rx.Component:
    return rx.cond(
            StatsState.area_toggle,
                rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="revenue",
                ),           
                rx.recharts.x_axis(data_key="order_date"),
                rx.recharts.y_axis(),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                data=StatsState.revenue_data,
                width="100%",
                height=300,
            )
        )
    


def orders_chart() -> rx.Component:
      return rx.cond(
            StatsState.area_toggle,
                rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="number_of_orders"
                    
                ),           
                rx.recharts.x_axis(data_key="order_date"),
                rx.recharts.y_axis(),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                data=StatsState.orders_data,
                width="100%",
                height=300,
            )
        )


def pie_chart() -> rx.Component:
    return rx.cond(
        StatsState.timeframe == "Yearly",
        rx.recharts.pie_chart(
            rx.recharts.pie(
                data=StatsState.yearly_device_data,
                data_key="value",
                name_key="name",
                cx="50%",
                cy="50%",
                padding_angle=1,
                inner_radius="70",
                outer_radius="100",
                label=True,
            ),
            rx.recharts.legend(),
            height=300,
        ),
        rx.recharts.pie_chart(
            rx.recharts.pie(
                data=StatsState.device_data,
                data_key="value",
                name_key="name",
                cx="50%",
                cy="50%",
                padding_angle=1,
                inner_radius="70",
                outer_radius="100",
                label=True,
            ),
            rx.recharts.legend(),
            height=300,
        ),
    )


def timeframe_select() -> rx.Component:
    return rx.select(
        ["Monthly", "Yearly"],
        default_value="Monthly",
        value=StatsState.timeframe,
        variant="surface",
        on_change=StatsState.set_timeframe,
    )

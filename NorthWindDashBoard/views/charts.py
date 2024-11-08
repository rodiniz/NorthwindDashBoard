import reflex as rx
from sqlalchemy import func
import pandas as pd
from reflex.components.radix.themes.base import (
    LiteralAccentColor,
)
from reflex_ag_grid import ag_grid

from ..models.customers import Customers, Order


class StatsState(rx.State):
    area_toggle: bool = True
    selected_tab: str = "revenue"
    timeframe: str = "Monthly"
    users_data = []
    revenue_data = []
    orders_data = []    
    users_count:int
    total_sales:float
    orders_count:int
    order_dates:list[str]=[]
    order_date_selected:str=""
    df_merged:pd.DataFrame=None

    order_ids:list[str]=[]
    order_id_selected:str=""
    orders_table_data:list[dict]
    df_orders:pd.DataFrame=None
    loading_data:bool=False
    loading_orders:bool=False
    df_order_details:pd.DataFrame=None  

    def toggle_areachart(self):
        self.area_toggle = not self.area_toggle

    def load_data(self):      
        self.loading_data=True       
        with rx.session() as session:
                self.users_count = session.exec(func.count(Customers.customer_id)).scalar()                
                df_orders = pd.read_sql("SELECT  * from orders",session.connection())
                df_orders['YearMonth']= pd.to_datetime(df_orders['order_date']).dt.strftime('%Y-%m')
                self.order_dates=df_orders['YearMonth'].unique().tolist()
                self.order_date_selected=df_orders.iloc[0]['YearMonth']
                self.load_by_date()
                self.loading_data=False
                yield
                
    def on_change(self,ev): 
         self.loading_data=True        
         self.order_date_selected=ev
         self.load_by_date()
         self.loading_data=False

    def order_id_change(self,ev):
       self.order_id_selected= ev
       self.load_orders_table()
        
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

                self.order_ids=df_filtered['order_id'].unique().tolist()
                order_id_value= self.order_ids[0]
                self.order_id_selected=order_id_value
                self.load_orders_table()
                #print(df_filtered.head())

        
    def load_orders_table(self):
        self.loading_orders=True        
        order_id= self.order_id_selected
        with rx.session() as session:
            #print(order_id)
            if self.df_order_details is None:
                self.df_order_details = pd.read_sql('SELECT od.order_id,p.product_name, od.quantity, od.unit_price, od.discount fROM order_details od join products p on od.product_id= p.product_id',session.connection())
            self.df_order_details['final_price']= self.df_order_details['unit_price'] * self.df_order_details['quantity']
            self.df_order_details['final_price'] = self.df_order_details['final_price'].apply(lambda x: "${:.1f}k".format((x/1000)))
            self.orders_table_data =self.df_order_details.query("order_id==@order_id").copy().to_dict(orient='records')          
            self.loading_orders=False
           
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


def revenue_chart() -> rx.Component:
    return rx.cond(
            StatsState.area_toggle,
            rx.recharts.bar_chart(
                rx.recharts.bar(
                    data_key="revenue",
                    stroke=rx.color("accent", 9),
                    fill=rx.color("accent", 8),
                ),
                rx.recharts.x_axis(data_key="order_date"),
                rx.recharts.y_axis(),
                rx.recharts.legend(),
                data=StatsState.revenue_data,              
                width="100%",
                height=250,
            ),
            
             
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

def orders_table():
    return ag_grid(
        id="ag_grid_basic_2",
        row_data=StatsState.orders_table_data,
        column_defs=[{"field": "product_name"},{"field": "quantity"}, {"field": "unit_price"}, {"field": "discount"},{"field":"final_price"}],
        width="100%",
        height="40vh",
    )    
import reflex as rx
from sqlalchemy import func
import pandas as pd
from reflex.components.radix.themes.base import (
    LiteralAccentColor,
)
from reflex_ag_grid import ag_grid

from ..models.customers import Customers


column_defs = [
    ag_grid.column_def(field="product_name", header_name="Product Name"),
    ag_grid.column_def(
        field="quantity", header_name="Quantity"
    ),
    ag_grid.column_def(
        field="unit_price_formated", header_name="Price"
    ),
    ag_grid.column_def(
        field="discount", header_name="Discount"
    ),
    ag_grid.column_def(
        field="final_price", header_name="Total"
    ),
    ag_grid.column_def(
        field="order_date", header_name="Order Date"
    ),
]

class StatsState(rx.State):
    area_toggle: bool = True
    selected_tab: str = "revenue"
    timeframe: str = "Monthly"    
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




    def load_data_frames(self):
      with rx.session() as session:
        self.users_count = session.exec(func.count(Customers.customer_id)).scalar()                
        self.df_orders = pd.read_sql("SELECT  * from orders",session.connection())
        df = pd.read_sql('select * from order_details',session.connection())
        self.df_merged= df.merge(self.df_orders)
        self.df_order_details = pd.read_sql('SELECT o.order_date, od.order_id,p.product_name, od.quantity, od.unit_price, od.discount '
                                            ' fROM order_details od join products p on od.product_id= p.product_id'\
                                            ' join orders o on od.order_id = o.order_id',session.connection())       

    def toggle_areachart(self):
        self.area_toggle = not self.area_toggle

    def load_data(self):
        self.load_data_frames()
        
        self.df_orders['YearMonth']= pd.to_datetime(self.df_orders['order_date']).dt.strftime('%Y-%m')
        self.order_dates=self.df_orders['YearMonth'].unique().tolist()
        self.order_date_selected=self.df_orders.iloc[0]['YearMonth']      
        self.loading_data=True       
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
        self.df_merged['YearMonth']= pd.to_datetime(self.df_merged['order_date']).dt.strftime('%Y-%m')

        value= self.order_date_selected    
        df_filtered=self.df_merged.query("YearMonth==@value").copy()

        df_filtered['final_price']= df_filtered['unit_price'] * df_filtered['quantity']
        self.total_sales= self.formatCurrency(df_filtered['final_price'].sum())       

                    
        self.orders_count=  len(df_filtered.groupby('order_id'))
        
        df_filtered['order_date']=df_filtered['order_date'].astype(str)
       
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
               
    def formatCurrency(self,curr):     
            return"{:.1f}k".format(curr/1000)
        
    def load_orders_table(self):
        self.loading_orders=True        
        order_id= self.order_id_selected
        self.df_order_details['final_price']= self.df_order_details['unit_price'] * self.df_order_details['quantity']
        self.df_order_details['unit_price_formated'] = self.df_order_details['unit_price'].apply(lambda x: "${:.1f}".format((x)))
        self.df_order_details['final_price'] = self.df_order_details['final_price'].apply(lambda x: "${:.1f}".format((x)))
        self.orders_table_data =self.df_order_details.query("order_id==@order_id").copy().to_dict(orient='records')          
        self.loading_orders=False
           



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
                rx.recharts.graphing_tooltip(),
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
        column_defs=column_defs,
        width="100%",
        height="40vh",
    )    
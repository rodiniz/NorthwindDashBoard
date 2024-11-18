import reflex as rx
from sqlalchemy import func
import pandas as pd
from reflex.components.radix.themes.base import (
    LiteralAccentColor,
)
from reflex_ag_grid import ag_grid

from ..models.customers import Customers


column_defs = [
     ag_grid.column_def(field="order_id", header_name="Order Id",rowGroup= True),
     ag_grid.column_def(field="product_name", header_name="Product Name"),
     ag_grid.column_def(field="quantity", header_name="Quantity"),
     ag_grid.column_def(field="unit_price_formated", header_name="Price"),
     ag_grid.column_def(field="discount", header_name="Discount"),
     ag_grid.column_def(field="final_price", header_name="Total"),
  
]

class StatsState(rx.State):
    area_toggle: bool = True
    selected_tab: str = "revenue"       
    revenue_data = []
    orders_data = []    
    users_count:int
    total_sales:float
    orders_count:int
    order_months:list[str]=[]
    order_month_selected:str=""
    df_merged:pd.DataFrame=None

    order_dates:list[str]=[]
    order_date_selected:str=""
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
        self.order_months=self.df_orders['YearMonth'].unique().tolist()
        self.order_month_selected=self.df_orders.iloc[0]['YearMonth']      
        self.loading_data=True       
        self.load_by_date()
        self.loading_data=False
        yield
                
    def on_change(self,ev): 
         self.loading_data=True        
         self.order_month_selected=ev
         self.load_by_date()
         self.loading_data=False

    def order_id_change(self,ev):
       self.order_date_selected= ev
       self.load_orders_table()
        
    def _prepare_filtered_data(self):
        """Prepare and filter the data for the selected month."""
        self.df_merged['YearMonth'] = pd.to_datetime(self.df_merged['order_date']).dt.strftime('%Y-%m')
        df_filtered = self.df_merged.query("YearMonth==@self.order_month_selected").copy()
        df_filtered['final_price'] = df_filtered['unit_price'] * df_filtered['quantity']
        df_filtered['order_date'] = df_filtered['order_date'].astype(str)
        return df_filtered

    def _calculate_revenue_data(self, df_filtered):
        """Calculate revenue data grouped by order date."""
        result = df_filtered.groupby(['order_date'])['final_price'].sum().reset_index()
        result = result.rename(columns={'final_price': 'revenue'})
        return result.to_dict(orient='records')

    def _calculate_orders_data(self, df_filtered):
        """Calculate unique orders count data grouped by order date."""
        orders_result = df_filtered.groupby(['order_date'])['order_id'].nunique().reset_index()
        orders_result = orders_result.rename(columns={'order_id': 'number_of_orders'})
        return orders_result.to_dict(orient='records')

    def _update_summary_stats(self, df_filtered):
        """Update summary statistics."""
        self.total_sales = self.formatCurrency(df_filtered['final_price'].sum())
        self.orders_count = len(df_filtered.groupby('order_id'))
        self.order_dates = df_filtered['order_date'].unique().tolist()
        self.order_date_selected = self.order_dates[0]

    def load_by_date(self):
        """Load and process data by date."""
        df_filtered = self._prepare_filtered_data()
        self.revenue_data = self._calculate_revenue_data(df_filtered)
        self.orders_data = self._calculate_orders_data(df_filtered)
        self._update_summary_stats(df_filtered)
        self.load_orders_table()
               
    def formatCurrency(self,curr):     
            return"{:.1f}k".format(curr/1000)
        
    def load_orders_table(self):
        self.loading_orders=True        
        order_date= self.order_date_selected
        self.df_order_details['final_price']= self.df_order_details['unit_price'] * self.df_order_details['quantity']
        self.df_order_details['unit_price_formated'] = self.df_order_details['unit_price'].apply(lambda x: "${:.1f}".format((x)))
        self.df_order_details['final_price'] = self.df_order_details['final_price'].apply(lambda x: "${:.1f}".format((x)))
        self.df_order_details['order_date'] = pd.to_datetime(self.df_order_details['order_date'])
        filtered_df = self.df_order_details[self.df_order_details['order_date'] == order_date]
        self.orders_table_data =filtered_df.to_dict(orient='records')          
        self.loading_orders=False

    def _prepare_combined_data(self):
        """Prepare data for the combination chart by merging revenue and orders data."""
        revenue_df = pd.DataFrame(self.revenue_data)
        orders_df = pd.DataFrame(self.orders_data)
        combined_data = pd.merge(revenue_df, orders_df, on='order_date')
        return combined_data.to_dict('records')

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

def line_chart() -> rx.Component:
    """Line chart showing both revenue and orders over time."""
    return rx.recharts.line_chart(
        rx.recharts.line(
            data_key="revenue",
            stroke=rx.color("accent", 9),
            name="Revenue"
        ),
        rx.recharts.line(
            data_key="number_of_orders",
            stroke=rx.color("accent", 6),
            name="Orders"
        ),
        rx.recharts.x_axis(data_key="order_date"),
        rx.recharts.y_axis(),
        rx.recharts.legend(),
        rx.recharts.graphing_tooltip(),
        data=StatsState.revenue_data,
        width="100%",
        height=300,
    )

def bar_chart() -> rx.Component:
    """Bar chart showing revenue and orders side by side."""
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="revenue",
            fill=rx.color("accent", 9),
            name="Revenue"
        ),
        rx.recharts.bar(
            data_key="number_of_orders",
            fill=rx.color("accent", 6),
            name="Orders"
        ),
        rx.recharts.x_axis(data_key="order_date"),
        rx.recharts.y_axis(),
        rx.recharts.legend(),
        rx.recharts.graphing_tooltip(),
        data=StatsState._prepare_combined_data(StatsState),
        width="100%",
        height=300,
    )

def combination_chart() -> rx.Component:
    """Combination chart showing revenue as bars and orders as a line."""
    return rx.recharts.composed_chart(
        rx.recharts.bar(
            data_key="revenue",
            fill=rx.color("accent", 9),
            name="Revenue"
        ),
        rx.recharts.line(
            data_key="number_of_orders",
            stroke=rx.color("accent", 6),
            name="Orders",
            y_axis_id="right"
        ),
        rx.recharts.x_axis(data_key="order_date"),
        rx.recharts.y_axis(),
        rx.recharts.y_axis(
            y_axis_id="right",
            orientation="right"
        ),
        rx.recharts.legend(),
        rx.recharts.graphing_tooltip(),
        data=StatsState._prepare_combined_data(StatsState),
        width="100%",
        height=300,
    )
import numpy as np
import pandas as pd

monthly_category_sql = ''' 
select to_char(order_date, 'YYYY-MM') as month,
       product_category,
	   sum(order_amount) as total_sales,
	   count(order_id) as order_count
from orders
group by 1,2;
'''

monthly_sql = '''
select date_trunc('month', order_date) as month,
       sum(order_amount) as total_sales,
	   count(order_id) as order_count
from orders
group by month; 
'''
top3_customers_sql = '''
select customer_id,
sum(order_amount) as sum_amount
from orders
group by customer_id
order by sum_amount desc
limit 3;
'''

def load_marketing_csv(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df['month'] = pd.to_datetime(df['month'], errors='coerce')
    return df
def clean_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = df_raw.copy()
    df['channel'] = df['channel'].astype(str).str.strip()
    channel_map = {
     'google ads': 'Google Ads',
     'googleads': 'Google Ads',
     'google ad': 'Google Ads',
     'facebook': 'Facebook',
     'instagram': 'Instagram',
     'tiktok': 'TikTok',
     'tik tok': 'TikTok',
     'youtube': 'YouTube',
     'you tube': 'YouTube'
    }
    df['channel_std'] = df['channel'].str.lower().map(channel_map).fillna(df['channel'].str.title())
    def parse_spend(x):
        if pd.isna(x):
            return np.nan
        if x in ['','na','missing','null','none']:
            return np.nan
        try:
            return float(x)
        except:
            return np.nan
    df['spend_amount_num'] = df['spend_amount'].apply(parse_spend)
    df['negativ_spend_flag'] = df['spend_amount_num'] < 0
    df.loc[df['negativ_spend_flag'], 'spend_amount_num'] = np.nan
    clean = df[['month','channel_std','spend_amount_num','negativ_spend_flag']].rename(columns={'channel_std':'channel','spend_amount_num':'spend_amount'})
    clean['month'] = pd.to_datetime(clean['month']).dt.to_period('M').dt.to_timestamp()
    return clean
csv_path = 'marketing_spend.csv'
df = clean_data(load_marketing_csv(csv_path))
print(df)
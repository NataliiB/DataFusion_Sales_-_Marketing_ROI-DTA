import pandas as pd
import numpy as np

def clean_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Очищення маркетингових даних та обробка аномалій через NaN"""
    df = df_raw.copy()
    
    # Стандартизація назв каналів
    df['channel'] = df['channel'].astype(str).str.strip()
    channel_map = {
        'google ads': 'Google Ads', 'googleads': 'Google Ads', 'google ad': 'Google Ads',
        'facebook': 'Facebook', 'instagram': 'Instagram',
        'tiktok': 'TikTok', 'tik tok': 'TikTok',
        'youtube': 'YouTube', 'you tube': 'YouTube'
    }
    df['channel_std'] = (
        df['channel'].str.lower().map(channel_map)
        .fillna(df['channel'].str.title())
    )
    
    # Перетворення витрат на числа
    if df['spend_amount'].dtype == 'object':
        df['spend_amount'] = df['spend_amount'].astype(str).str.replace(',', '.')
    df['spend_amount'] = pd.to_numeric(df['spend_amount'], errors='coerce')
    
    # ОБРОБКА АНОМАЛІЙ (як у вчительки)
    # Замінюємо від'ємні значення на NaN
    df.loc[df['spend_amount'] < 0, 'spend_amount'] = np.nan
    
    # Форматування дати
    df['month'] = pd.to_datetime(df['month']).dt.to_period('M').dt.to_timestamp()
    return df

def agg_sales_monthly(df_orders_raw: pd.DataFrame) -> pd.DataFrame:
    """Агрегація продажів з БД по місяцях"""
    df = df_orders_raw.copy()
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['month'] = df['order_date'].dt.to_period('M').dt.to_timestamp()
    
    return df.groupby('month', as_index=False).agg(
        total_sales=('order_amount', 'sum'),
        order_count=('order_id', 'count')
    )

def calculate_monthly_roi(sales_marketing: pd.DataFrame) -> pd.DataFrame:
    """Розрахунок ROI з урахуванням NaN"""
    df = sales_marketing.copy()
    df['roi'] = np.where(
        df['total_spend'] > 0,
        df['total_sales'] / df['total_spend'],
        np.nan
    )
    return df[['month', 'total_sales', 'total_spend', 'roi']]

def roi_quality_notes(marketing_clean: pd.DataFrame):
    """Нотатки про якість даних"""
    notes = [
        "Виявлено від’ємні витрати для Google Ads; виправлено на NaN для коректного ROI.",
        "Стандартизацію назв каналів виконано (YouTube/Google Ads)."
    ]
    return notes

def extra_presentation_tables(sales_marketing: pd.DataFrame, marketing_clean: pd.DataFrame):
    """Підготовка детальних звітів"""
    channel_pivot = (marketing_clean
                     .pivot_table(index="month", columns="channel_std", values="spend_amount", aggfunc="sum")
                     .reset_index())
    # Merge за допомогою sales_marketing (там вже є загальні суми)
    overview = sales_marketing.merge(channel_pivot, on="month", how="left")
    return {"overview": overview}
def build_top3_customers(orders_df: pd.DataFrame) -> pd.DataFrame:
    """Визначає топ-3 клієнтів за сумою витрат"""
    top3 = (
        orders_df.groupby("customer_id", as_index=False)
        .agg(
            orders_count=("order_id", "count"), 
            total_spent=("order_amount", "sum")
        )
        .sort_values("total_spent", ascending=False)
        .head(3)
    )
    return top3
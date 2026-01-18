import pandas as pd
from db_sql import init_db, get_engine
from viz import plot_analytics
# Імпортуємо логічні блоки обробки даних із нашого модуля утиліт
from utils import (
    clean_data, 
    agg_sales_monthly, 
    calculate_monthly_roi, 
    roi_quality_notes, 
    extra_presentation_tables,
    build_top3_customers  # Додали функцію для аналізу VIP-клієнтів
)

def main():
    # --- ЕТАП 1: ЕКСТРАКЦІЯ (Отримання даних із джерел) ---
    # Ініціалізуємо базу даних та створюємо підключення (Engine)
    init_db('orders.sql')
    engine = get_engine()
    
    # Завантажуємо дані про продажі з SQL-бази та маркетинг із CSV-файлу
    df_orders = pd.read_sql("SELECT * FROM orders", engine)
    df_marketing_raw = pd.read_csv('marketing_spend.csv', encoding='cp1251')

    # --- ЕТАП 2: ТРАНСФОРМАЦІЯ ТА ОЧИЩЕННЯ (Data Cleaning) ---
    # Очищуємо маркетингові дані (виправляємо назви каналів, типи даних та аномалії)
    df_marketing_clean = clean_data(df_marketing_raw)
    
    # Агрегуємо продажі по місяцях (рахуємо загальний виторг та кількість замовлень)
    sales_monthly = agg_sales_monthly(df_orders)
    
    # Групуємо загальні маркетингові витрати за місяць для порівняльного аналізу
    marketing_monthly = df_marketing_clean.groupby('month', as_index=False).agg(
        total_spend=('spend_amount', 'sum')
    )

    # --- ЕТАП 3: ІНТЕГРАЦІЯ ТА ОБЧИСЛЕННЯ (Merging & ROI) ---
    # Об'єднуємо таблиці продажів та витрат в одну фінальну структуру за ключем 'month'
    final_merged_df = pd.merge(sales_monthly, marketing_monthly, on='month', how='left')
    
    # Заповнюємо нулями місяці, де не було витрат на рекламу, щоб уникнути помилок у розрахунках
    final_merged_df['total_spend'] = final_merged_df['total_spend'].fillna(0)
    
    # Розраховуємо показник ROI (окупність) та зберігаємо результат у файл
    df_roi = calculate_monthly_roi(final_merged_df)
    df_roi.to_csv('monthly_roi.csv', index=False)

    # --- ЕТАП 4: ПОГЛИБЛЕНИЙ АНАЛІЗ ТА ЗВІТНІСТЬ ---
    # Перевіряємо якість вхідних даних (фіксуємо виправлені аномалії для звіту)
    notes = roi_quality_notes(df_marketing_clean)
    print("\n--- НОТАТКИ ЩОДО ЯКОСТІ ДАНИХ (Data Quality Log) ---", *notes, sep="\n- ")

    # Готуємо детальну таблицю з розподілом витрат по кожному маркетинговому каналу
    detailed_data = extra_presentation_tables(final_merged_df, df_marketing_clean)
    detailed_data["overview"].to_csv('detailed_report.csv', index=False)

    # Аналізуємо клієнтську базу: визначаємо Топ-3 найприбутковіших клієнтів
    top_customers = build_top3_customers(df_orders)
    top_customers.to_csv('top_customers.csv', index=False, encoding='utf-8-sig')
    print("\n--- ТОП-3 VIP КЛІЄНТИ ---")
    print(top_customers)

    # --- ЕТАП 5: ВІЗУАЛІЗАЦІЯ (Data Presentation) ---
    # Виводимо підсумкову таблицю в консоль та будуємо графік динаміки
    print("\n--- ФІНАЛЬНА ТАБЛИЦЯ ДЛЯ ЗВІТУ (Sales vs Marketing) ---")
    print(final_merged_df)
    
    # Побудова та збереження комбінованого графіка (Bar + Line chart)
    plot_analytics(final_merged_df, df_marketing_clean)
    
    return final_merged_df

if __name__ == "__main__":
    main()
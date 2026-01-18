import matplotlib.pyplot as plt
import pandas as pd

def plot_analytics(final_df, df_marketing_clean):
    # 1. Підготовка даних: Робимо копію, щоб не зіпсувати оригінал
    df_m = df_marketing_clean.copy()
    df_f = final_df.copy()

    # 2. Форматування місяців (прибираємо 00:00:00)
    # Перетворюємо об'єкт дати на рядок формату "Рік-Місяць"
    df_f['month_label'] = df_f['month'].dt.strftime('%Y-%m')
    
    # Готуємо Pivot для стовпчиків
    marketing_pivot = df_m.pivot_table(
        index='month', 
        columns='channel_std', 
        values='spend_amount', 
        aggfunc='sum'
    ).fillna(0)
    
    # Для осі X у стовпчиках теж робимо гарні підписи
    marketing_pivot.index = marketing_pivot.index.strftime('%Y-%m')

    # 3. Налаштування графічного вікна
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Малюємо витрати по каналах (Stacked Bar)
    # Параметр zorder=2 кладе стовпчики за лінію
    marketing_pivot.plot(kind='bar', stacked=True, ax=ax1, alpha=0.7, zorder=2)
    
    ax1.set_ylabel('Маркетингові витрати (₴)', fontsize=12, fontweight='bold', color='#2c3e50')
    ax1.set_xlabel('Місяць', fontsize=12)
    ax1.legend(title='Маркетингові канали', loc='upper left', bbox_to_anchor=(1.05, 1))

    # 4. Створюємо другу вісь Y для лінії продажів
    ax2 = ax1.twinx()
    
    # Малюємо лінію (zorder=3 кладе її поверх стовпчиків)
    ax2.plot(df_f['month_label'], df_f['total_sales'], 
             color='red', marker='o', markersize=8, linewidth=3, 
             label='Сума продажів (₴)', zorder=3)
    
    ax2.set_ylabel('Загальні продажі (₴)', color='red', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right')

    # 5. Фінальне оформлення
    plt.title('Аналіз зв\'язку маркетингових витрат та продажів (2025)', fontsize=15, pad=20)
    ax1.grid(axis='y', linestyle='--', alpha=0.4, zorder=1)
    
    # Повертаємо підписи місяців для кращого читання
    ax1.tick_params(axis='x', rotation=45)

    # 6. Збереження файлу
    plt.tight_layout()
    plt.savefig('final_marketing_report_2025.png', dpi=300, bbox_inches='tight')
    plt.show()
import sqlite3

#створюємо нову базу
conn = sqlite3.connect('shop.db')
cur = conn.cursor()

with open('orders_sqlite.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

cur.executescript(sql_script)

cur.execute('''
            select * from orders limit 5;
''')
print(cur.fetchall())

conn.commit()
conn.close()
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# إعداد قاعدة البيانات المحلية وإنشاء الجدول إذا لم يكن موجوداً
def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            location TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# تنفيذ دالة الإنشاء عند بدء التشغيل
init_db()

@app.route('/', methods=['GET'])
def index():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # البحث لو المستخدم بحث عن شيء
    search_query = request.args.get('search', '')
    if search_query:
        cursor.execute("SELECT * FROM inventory WHERE name LIKE ? OR category LIKE ?", 
                       ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute("SELECT * FROM inventory")
        
    items = cursor.fetchall()
    
    # حساب الإحصائيات للوحة التحكم (Dashboard)
    cursor.execute("SELECT COUNT(*), SUM(quantity) FROM inventory")
    stats = cursor.fetchone()
    total_products = stats[0] if stats[0] else 0
    total_quantity = stats[1] if stats[1] else 0
    
    # حساب المنتجات التي تعاني من نقص في المخزون (الكمية <= 5)
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE quantity <= 5")
    low_stock_count = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('index.html', items=items, total_products=total_products, 
                           total_quantity=total_quantity, low_stock_count=low_stock_count)

@app.route('/add', methods=['POST'])
def add_item():
    name = request.form['name']
    category = request.form['category']
    quantity = request.form['quantity']
    location = request.form['location']
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventory (name, category, quantity, location) VALUES (?, ?, ?, ?)",
                   (name, category, quantity, location))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == 'main':
    app.run(debug=True, port=5000)
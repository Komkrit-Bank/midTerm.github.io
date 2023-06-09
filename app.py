from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
import json

app = Flask(__name__)

conn = sqlite3.connect('product.db')
cur = conn.cursor()

# def extract_data(data_df):
#     data_cat = [row[1][3] for row in data_df.iterrows()]
#     data_col = data_df.columns.to_list()[1:]
#     data_body = []

#     for row in data_df.iterrows():
#         data_body.append(dict(zip(data_col, row[1][1:])))

#     complete_data = dict(zip(data_key, data_body))
#     return complete_data

def update_sql(type, conn, task, id):
    if type == 'product':
        sql = f''' UPDATE product
                    SET product_name = ? ,
                        product_price = ? ,
                        product_cat = ?,
                        product_review = ?,
                        color = ?,
                        material = ?,
                        offer = ?,
                        product_detail = ?,
                        product_img = ?
                    WHERE product_id = {id}'''
    else:
        return
    
    cur.execute(sql, task)
    conn.commit()

default_cart = 0
cart_list = []
on_cart = []
items_show = []
total_price = 0


def filter_data(column, con):
    cur.execute(f'SELECT * FROM product WHERE {column} = ?', (con,))
    data = cur.fetchall()
    return data

def oncartList(cart_list):
    global on_cart
    global items_show
    on_cart = cart_list
    items = [item['product_id'] for item in on_cart ]
    items_qty = {id: items.count(id) for id in items}
    item_key = set(items)

    items_show = {}
    for key in item_key:
        for item in on_cart:
            if key == item['product_id']:
                items_show[key] = item
                items_show[key]['qty'] = items_qty[key]
            else:
                continue
    items_show = [items_show[key] for key in item_key]
    # return on_cart, 

product_df = pd.read_csv(r'src\productData.csv', encoding= 'utf8')
product_df = product_df.fillna('null')
rows = [tuple(row[1].to_list()) for row in product_df.iterrows()]
product_col = product_df.columns.to_list()
product_dict = [dict(zip(product_col, item)) for item in rows]

with open('./src/productData.json', 'w') as file:
    json.dump(product_dict, file, indent= 4)

for row in rows:
    update_sql('product', conn, row[1:], row[0])
# Use executemany() to insert multiple records at a time

@app.route('/', methods=['GET', 'POST'])
def index():
    global product_dict
    cart = default_cart
    products = rows
    category = 'console'
    review = request.form.get('review_select')
    return render_template('index.html', review= review, products= products, category= category, cart= cart, prodict= product_dict)

@app.route('/product/<int:id>')
def product(id):
    pro_detail = product_df[product_df['product_id'] == id].iloc[0, :][1:].to_dict()
    return render_template('product.html', pro_detail= pro_detail,cart= len(cart_list), product_id= id)

@app.route('/product-list', methods= ['GET'])
def product_list():
    return product_dict

@app.route('/orderlist/<int:id>', methods=['GET'])
def orderlist(id):
    if request.method == 'GET':
        global default_cart
        pro_detail = product_df[product_df['product_id'] == id].iloc[0, :].to_dict()
        cart_list.append(pro_detail)
        default_cart = len(cart_list)
        
    return redirect('/')

@app.route('/cart')
def oncart():
    oncartList(cart_list)
    global total_price
    total_price = sum([item['product_price'] for item in on_cart])
    if default_cart == 0:
        return redirect('/')
    else:    
        return render_template('cart.html',oncart= items_show,cart= len(on_cart), total= '{:,}'.format(total_price))

@app.route('/search', methods = ['GET', 'POST'])
def search():
    key = request.form['data-search']
    return redirect(f'/search/{key}')

@app.route('/search/<string:keyword>')
def searchResult(keyword):
    result_search = [item for item in product_dict if keyword.lower() in item['product_name'].lower()]
    oncartList(cart_list)
    if len(result_search) == 1:
        return redirect('/product/{}'.format(result_search[0]['product_id']))
    else:
        return render_template('search.html', cart= len(on_cart), products= result_search, number= len(result_search))

@app.route('/delete/<int:id>')
def delete(id):
    global default_cart
    on_cart.pop(on_cart.index([item for item in on_cart if item['product_id'] == id][0]))
    default_cart = len(on_cart)
    if default_cart == 0:
        return redirect('/')
    else:
        return redirect('/cart')

@app.route('/cusinfo', methods= ['GET', 'POST'])
def cusinfo():
    print('Hello World')
    return redirect('/payment')

@app.route('/information', methods= ['GET', 'POST'])
def information():
    oncartList(cart_list)
    if default_cart == 0:
        return redirect('/')
    else:
        return render_template('information.html', cart= len(on_cart))

@app.route('/getCardInfo', methods= ['GET'])
def getCardInfo():
    return redirect('/confirmation')

@app.route('/confirmation')
def confirmation():
    oncartList(cart_list)
    if default_cart == 0:
        return redirect('/')
    else:
        return render_template('confirmation.html', oncart= items_show, cart= len(on_cart), total = '{:,}'.format(total_price))
        
@app.route('/payment')
def payment():
    oncartList(cart_list)
    return render_template('payment.html', oncart= items_show, cart= len(on_cart),total = '{:,}'.format(total_price))

if __name__ == '__main__':
    app.run(debug= True)
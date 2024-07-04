from flask import render_template, request, redirect, url_for, session, jsonify
from app import app
import requests
import re

CART_LINK = 'https://fakestoreapi.com/carts/7'

def normalize_text(text):
    # text normalization
    text_stripped = re.sub(r'[^\w\s]','', text) 
    return text_stripped.lower()

def calculate_relevance(search_words, product):
    relevance = 0
    title = normalize_text(product['title'])
    description = normalize_text(product['description'])

    for word in search_words:
        if word in title:
            relevance +=1
        if word in description:
            relevance +=1
    return relevance


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET','POST']) # gets login page and posts a request from this to our api if it returns a 200 code then we are loggin in and authenticated if nto then it returns an error deisplayed on screp
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username-email')
        password = request.form.get('password')
        
        # Authenticate with Fake Store API
        try:
            response = requests.post('https://fakestoreapi.com/auth/login', 
                                     json={'username': username, 'password': password})
            
            if response.status_code == 200:
                # Authentication successful
                token = response.json()['token']
                session['user_token'] = token

                # establishing cart to be used for user throughout their logged in session - clears when they leave since fakestoreapi isnt a real commericalized server
                cart_response = requests.get(CART_LINK)
                if 'cart' not in session and cart_response.status_code == 200:
                    session['cart'] = cart_response.json()
                    #  ref marking


                return redirect(url_for('dashboard'))
            else:
                # Authentication failed
                error = 'Not a valid user or password'
        except requests.RequestException as e:
            # Handle any errors in the request
            error = 'An error occurred. Please try again later.'
            print(f"Error during login: {e}")  # Log the error for debugging

    return render_template('login.html', error=error)

@app.context_processor
def inject_user():
    is_logged_in = 'user_token' in session
    return dict(is_logged_in=is_logged_in)


"""for dev purposes """
@app.route('/user_data', methods=['GET']) # type: ignore
def print_users():
    response = requests.get('https://fakestoreapi.com/users')

    if response.status_code == 200:
        users = response.json()

        return users

@app.route('/product_data', methods=['GET']) # type: ignore
def print_prodcuts():
    response = requests.get('https://fakestoreapi.com/products')

    if response.status_code == 200:
        products = response.json()

        return products
    
@app.route('/cart_data', methods=['GET']) # type: ignore
def print_cart():
    return session['cart']

"""for dev purposes"""

 

@app.route('/dashboard')
def dashboard():
    if 'user_token' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/dashboard', methods=['GET', 'POST']) # type: ignore
def logout():
    if request.method == 'POST':
        if 'user_token' in session:
            session.pop('user_token', None)
            return redirect('/')
        


@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        data = request.json
        product_id = data.get('product_id')
        
        if 'cart' not in session:
            session['cart'] = {'products': []}
        
        # Check if the product is already in the cart
        product_in_cart = next((item for item in session['cart']['products'] if item['productId'] == product_id), None)
        
        if product_in_cart:
            product_in_cart['quantity'] += 1
        else:
            session['cart']['products'].append({'productId': product_id, 'quantity': 1})
        
        session.modified = True
        
        return jsonify({'success': True, 'message': 'Product added to cart'})
    
    elif request.method == 'GET':
        try:
            response = requests.get('https://fakestoreapi.com/products')
            if response.status_code == 200:
                all_products = response.json()

                search_query = request.args.get('search', '').lower()

                if search_query:
                    search_words = [normalize_text(word) for word in search_query.split()]
                    
                    # Exclusion list for filtering
                    exclusion_list = ['women'] if 'men' in search_words else []

                    filtered_products = []
                    for product in all_products:
                        if any(exclusion in normalize_text(product['title']) or 
                               exclusion in normalize_text(product['description']) for exclusion in exclusion_list):
                            continue
                        
                        relevance = calculate_relevance(search_words, product)
                        if relevance > 0:
                            filtered_products.append((product, relevance))

                    # Sort products by relevance
                    filtered_products.sort(key=lambda x: x[1], reverse=True)
                    sorted_products = [product for product, _ in filtered_products]

                    return render_template('products-searched.html', products=sorted_products)
                
                else:
                    return render_template('products-searched.html', products=all_products)
            else:
                return "Failed to fetch products", 500
        except requests.RequestException as e:
            print(f"Error fetching products: {e}")
            return "An error occurred while fetching products", 500

    return "Method not allowed", 405
    
    
@app.route('/cart', methods=['GET', 'POST'])
def load_cart():

    # Check if user is logged in
    if 'user_token' not in session:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.json
        product_id = data.get('product_id')

        # Check if the product is even in the cart
        product_index = next((index for (index, item) in enumerate(session['cart']['products']) if item['productId'] == product_id), None)

        if product_index is not None:
            if session['cart']['products'][product_index]['quantity'] > 1:
                session['cart']['products'][product_index]['quantity'] -= 1
            else:
                session['cart']['products'].pop(product_index)

            session.modified = True

            return "True"


    
    try:
        if session['cart']:
            cart_products = load_cart_products(session['cart'])
            return render_template('cart.html', products=cart_products)
        else:
            return redirect(url_for('login')) # temp for dev purposes
        
        
    except requests.RequestException as e:
        print(f"Error fetching cart: {e}")
        return "An error occurred while fetching cart", 500

def load_cart_products(cart):
    try:
        response = requests.get('https://fakestoreapi.com/products')
        if response.status_code == 200:
            all_products = response.json()
            cart_products = []
            for item in cart['products']:
                product = next((p for p in all_products if p['id'] == item['productId']), None)
                if product:
                    product['quantity'] = item['quantity']
                    cart_products.append(product)
            return cart_products
        else:
            print("Failed to fetch products")
            return []
    except requests.RequestException as e:
        print(f"Error fetching products: {e}")
        return []


if __name__ == '__main__':
    app.run(debug=True)
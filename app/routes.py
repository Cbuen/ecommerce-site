from flask import render_template, request, redirect, url_for, session, jsonify
from app import app
import requests

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

                if 'cart' not in session:
                    cart_response = requests.get('https://fakestoreapi.com/carts/1')
                    if cart_response.status_code == 200:
                        session['cart'] = cart_response.json


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
    response = requests.get('https://fakestoreapi.com/carts/1')

    if response.status_code == 200:
        carts = response.json()

        return carts
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
        

@app.route('/products-searched')
def products():
    try:
        response = requests.get('https://fakestoreapi.com/products')
        if response.status_code == 200:
            products = response.json()
            return render_template('products-searched.html', products=products)
        else:
            return "Failed to fetch products", 500
    except requests.RequestException as e:
        print(f"Error fetching products: {e}")
        return "An error occurred while fetching products", 500
    

@app.route('/cart')
def load_cart():

    # Check if user is logged in
    if 'user_token' not in session:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))
    
    try:
        response = requests.get('https://fakestoreapi.com/carts/1')
        if response.status_code == 200:
            cart = response.json()
            cart_products = load_cart_products(cart)
            return render_template('cart.html', cart=cart, products=cart_products)
        else:
            return "Failed to fetch cart", 500
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
from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)

API_URL = 'http://localhost:3000/users'

@app.route('/')
def index():
    response = requests.get(API_URL)
    users = response.json()
    return render_template('index.html', users=users)

@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        response = requests.post(API_URL, json={'name': name, 'email': email})
        if response.status_code == 201:
            return redirect(url_for('index'))
        else:
            return 'Error: ' + response.text
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        response = requests.put(f'{API_URL}/{id}', json={'name': name, 'email': email})
        if response.status_code == 200:
            return redirect(url_for('index'))
        else:
            return 'Error: ' + response.text
    
    response = requests.get(f'{API_URL}/{id}')
    print(response)
    user = response.json()
    return render_template('edit.html', user=user)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_user(id):
    response = requests.delete(f'{API_URL}/{id}')
    if response.status_code == 200:
        return redirect(url_for('index'))
    else:
        return 'Error: ' + response.text

if __name__ == '__main__':
    app.run(debug=True)


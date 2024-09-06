from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'
db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)


def create_tables():
    with app.app_context():
        db.create_all()


@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.json
    username = data['username']
    password = data['password']
    role = data.get('role', 'user')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='User registered successfully'), 201


@app.route('/users/login', methods=['POST'])
def login_user():
    data = request.json
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        access_token = create_access_token(identity={'username': user.username, 'role': user.role})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message='Invalid credentials'), 401


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/admin', methods=['GET'])
@jwt_required()
def admin_only():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify(message='Admins only!'), 403
    return jsonify(message='Welcome, admin!'), 200


@app.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify(message='Admins only!'), 403

    users = User.query.all()
    users_list = [
        {
            'id': user.id,
            'username': user.username,
            'password': str(user.password)[2:-1:],
            'role': user.role
        }
        for user in users
    ]
    return jsonify(users=users_list), 200


@app.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()

    if current_user['role'] != 'admin':
        return jsonify(message='Admins only!'), 403

    user_to_delete = User.query.get(user_id)

    if not user_to_delete:
        return jsonify(message='User not found'), 404

    db.session.delete(user_to_delete)
    db.session.commit()

    return jsonify(message=f'User {user_to_delete.username} deleted successfully'), 200


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)

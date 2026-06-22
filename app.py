from flask import Flask, render_template
from flask import request, redirect
from flask import url_for, flash
from flask import send_file

from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail, Message

from flask_wtf.csrf import CSRFProtect

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from itsdangerous import URLSafeTimedSerializer

from dotenv import load_dotenv

from datetime import datetime, date

import pandas as pd

import random
import io
import os

# ======================
# LOAD ENV
# ======================

load_dotenv()

# ======================
# APP CONFIG
# ======================

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY'
)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///expenses.db'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ======================
# MAIL CONFIG
# ======================

app.config['MAIL_SERVER'] = 'smtp.gmail.com'

app.config['MAIL_PORT'] = 587

app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = os.getenv(
    'MAIL_USERNAME'
)

app.config['MAIL_PASSWORD'] = os.getenv(
    'MAIL_PASSWORD'
)

app.config['MAIL_DEFAULT_SENDER'] = (
    os.getenv('MAIL_USERNAME')
)

# ======================
# INITIALIZE
# ======================

db = SQLAlchemy(app)

mail = Mail(app)

#csrf = CSRFProtect(app)

serializer = URLSafeTimedSerializer(
    app.config['SECRET_KEY']
)

# ======================
# MODELS
# ======================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(300),
        nullable=False
    )

    verified = db.Column(
        db.Boolean,
        default=False
    )

    otp = db.Column(
        db.String(10)
    )


class Expense(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    description = db.Column(
        db.String(200),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    currency = db.Column(
        db.String(10),
        default='USD'
    )

# ======================
# CREATE DATABASE
# ======================

with app.app_context():
    db.create_all()

# ======================
# CATEGORIES
# ======================

CATEGORIES = [
    'Food',
    'Transport',
    'Entertainment',
    'Utilities',
    'Rent',
    'Other'
]

# ======================
# HOME
# ======================

@app.route('/')
def index():

    expenses = Expense.query.order_by(
        Expense.date.desc()
    ).all()

    total = round(
        sum(e.amount for e in expenses),
        2
    )

    return render_template(
        'index.html',

        expenses=expenses,

        total=total,

        categories=CATEGORIES,

        today=date.today().isoformat()
    )

# ======================
# ADD EXPENSE
# ======================

@app.route('/add', methods=['POST'])
def add():

    description = request.form.get(
        'description'
    )

    amount = float(
        request.form.get('amount')
    )

    category = request.form.get(
        'category'
    )

    date_value = datetime.strptime(
        request.form.get('date'),
        '%Y-%m-%d'
    ).date()

    expense = Expense(
        description=description,
        amount=amount,
        category=category,
        date=date_value
    )

    db.session.add(expense)

    db.session.commit()

    flash(
        'Expense Added!',
        'success'
    )

    return redirect(
        url_for('index')
    )

# ======================
# DELETE EXPENSE
# ======================

@app.route('/delete/<int:id>',
methods=['POST'])

def delete(id):

    expense = Expense.query.get_or_404(id)

    db.session.delete(expense)

    db.session.commit()

    flash(
        'Expense Deleted!',
        'success'
    )

    return redirect(
        url_for('index')
    )

# ======================
# EDIT EXPENSE
# ======================

@app.route('/edit/<int:id>',
methods=['GET', 'POST'])

def edit(id):

    expense = Expense.query.get_or_404(id)

    if request.method == 'POST':

        expense.description = request.form.get(
            'description'
        )

        expense.amount = float(
            request.form.get('amount')
        )

        expense.category = request.form.get(
            'category'
        )

        expense.date = datetime.strptime(
            request.form.get('date'),
            '%Y-%m-%d'
        ).date()

        db.session.commit()

        flash(
            'Expense Updated!',
            'success'
        )

        return redirect(
            url_for('index')
        )

    return render_template(
        'edit.html',

        expense=expense,

        categories=CATEGORIES
    )

# ======================
# SIGNUP
# ======================

@app.route('/signup',
methods=['GET', 'POST'])

def signup():

    if request.method == 'POST':

        name = request.form.get('name')

        email = request.form.get('email')

        password = request.form.get('password')

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                'Email already exists!',
                'error'
            )

            return redirect(
                url_for('signup')
            )

        hashed_password = generate_password_hash(
            password
        )

        otp = str(
            random.randint(100000, 999999)
        )

        user = User(
            name=name,
            email=email,
            password=hashed_password,
            otp=otp
        )

        db.session.add(user)

        db.session.commit()

        print("OTP:", otp)

        flash(
            'OTP generated in terminal!',
            'success'
        )

        return redirect(
            url_for(
                'verify_email',
                user_id=user.id
            )
        )

    return render_template(
        'signup.html'
    )

# ======================
# VERIFY EMAIL
# ======================

@app.route('/verify/<int:user_id>',
methods=['GET', 'POST'])

def verify_email(user_id):

    user = User.query.get_or_404(
        user_id
    )

    if request.method == 'POST':

        otp = request.form.get('otp')

        if otp == user.otp:

            user.verified = True

            user.otp = None

            db.session.commit()

            flash(
                'Account Verified!',
                'success'
            )

            return redirect(
                url_for('login')
            )

        else:

            flash(
                'Invalid OTP!',
                'error'
            )

    return render_template(
        'verify.html'
    )

# ======================
# LOGIN
# ======================

@app.route('/login',
methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        email = request.form.get(
            'email'
        )

        password = request.form.get(
            'password'
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                'User not found!',
                'error'
            )

            return redirect(
                url_for('login')
            )

        if not user.verified:

            flash(
                'Verify your email first!',
                'error'
            )

            return redirect(
                url_for('login')
            )

        if check_password_hash(
            user.password,
            password
        ):

            flash(
                'Login Successful!',
                'success'
            )

            return redirect(
                url_for('index')
            )

        else:

            flash(
                'Invalid Password!',
                'error'
            )

    return render_template(
        'login.html'
    )

# ======================
# FORGOT PASSWORD
# ======================

@app.route('/forgot-password',
methods=['GET', 'POST'])

def forgot_password():

    if request.method == 'POST':

        email = request.form.get(
            'email'
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                'Email not found!',
                'error'
            )

            return redirect(
                url_for('forgot_password')
            )

        token = serializer.dumps(
            email,
            salt='reset-password'
        )

        reset_link = url_for(
            'reset_password',
            token=token,
            _external=True
        )

        print(
            "Reset Link:",
            reset_link
        )

        flash(
            'Reset link generated in terminal!',
            'success'
        )

    return render_template(
        'forgot_password.html'
    )

# ======================
# RESET PASSWORD
# ======================

@app.route('/reset-password/<token>',
methods=['GET', 'POST'])

def reset_password(token):

    try:

        email = serializer.loads(
            token,
            salt='reset-password',
            max_age=300
        )

    except:

        flash(
            'Reset link expired!',
            'error'
        )

        return redirect(
            url_for('forgot_password')
        )

    user = User.query.filter_by(
        email=email
    ).first()

    if request.method == 'POST':

        new_password = request.form.get(
            'password'
        )

        user.password = generate_password_hash(
            new_password
        )

        db.session.commit()

        flash(
            'Password reset successful!',
            'success'
        )

        return redirect(
            url_for('login')
        )

    return render_template(
        'reset_password.html'
    )

# ======================
# ADMIN DASHBOARD
# ======================

@app.route('/admin')
def admin_dashboard():

    total_users = User.query.count()

    total_transactions = Expense.query.count()

    total_revenue = db.session.query(
        db.func.sum(Expense.amount)
    ).scalar() or 0

    most_active_users = db.session.query(
        User.name,
        db.func.count(Expense.id)
    ).join(
        Expense,
        User.id == Expense.id
    ).group_by(
        User.id
    ).all()

    return render_template(
        'admin.html',

        total_users=total_users,

        total_transactions=total_transactions,

        total_revenue=round(
            float(total_revenue),
            2
        ),

        most_active_users=most_active_users
    )

# ======================
# RUN APP
# ======================

if __name__ == '__main__':

    app.run(debug=True)
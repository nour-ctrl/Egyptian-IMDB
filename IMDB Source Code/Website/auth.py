from flask import Blueprint, render_template, request, flash, Flask
from flask_mysqldb import MySQL 



auth = Blueprint ('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

# @auth.route('/home', methods=['GET', 'POST'])
# def home():
#     return render_template("home.html")

@auth.route('/logout')
def logout():
    return render_template("logout.html")

@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    return render_template("sign_up.html")
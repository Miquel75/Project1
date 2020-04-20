import os

from flask import Flask, render_template, request, session, redirect,url_for,g
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

app = Flask(__name__)
app.secret_key = "secretkey"

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

users = db.execute("SELECT * FROM users")


@app.route("/")
def index():
    #ici il faudra mettre un template qui permet de choisir entre login et Register, index2.html=register et login.html=login
    return render_template("index.html")
   

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == 'POST':

    # Get form information.
        username = request.form.get( "username")
        firstname = request.form.get("firstname")
        lastname = request.form.get ("lastname")
        email = request.form.get ("email")
        country = request.form.get("country")
        password = request.form.get("password") 
        password2 = request.form.get("password2") 
        #check username
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0:
            return render_template("error.html", message="This username is already taken, choose another one !")
        
        #check username and password are not empty
        if not username :
            return render_template("error.html", message="You have to choose a Username !")
        if not password :
            return render_template("error.html", message="You have to choose a Password !")
        #check username at least 3 characters and password at least 6
        if len(username)<3 : 
            return render_template("error.html", message="Username should be at least 3 characters !")
        if len(password)<6 : 
            return render_template("error.html", message="Password should be at least 6 characters !")
        if password2 != password : 
            return render_template("error.html", message="Passwords are not the same")

        # insert a user
        db.execute("INSERT INTO users (username, firstname, lastname, email, country, password) VALUES (:username, :firstname, :lastname, :email, :country, :password)",
                {"username": username, "firstname" : firstname, "lastname" : lastname, "email" : email, "country" : country, "password": password})
        db.commit()
        
    
        return render_template("success.html")
    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        session.pop('user_id', None) #remove user_id if there is one already inside the session

    #check username exist
    username = request.form.get( "username")
    password = request.form.get("password") 

    user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    user_id=db.execute("SELECT id FROM users WHERE username = :username", {"username": username}).fetchone()

    if user and user.password==password:
        session['user_id'] = user.id
        return redirect(url_for("user_id"))
   
    return render_template("login.html")

@app.route("/user_id")
def user_id():
    if "user_id" in session:
        user_id = session["user_id"]
        return f"<h1>  {user_id} </h1>"
    else : 
        if "user_id" in session:
            return redirect(url_for("user_id"))
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))
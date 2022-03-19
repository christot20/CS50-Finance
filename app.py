import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(uri)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#db.execute("ALTER TABLE holdings ALTER COLUMN price TEXT NOT NULL")
#db.execute("DROP TABLE holdings")
# db.execute("DROP TABLE indexinfo")
# db.execute("UPDATE users SET cash = 10000.00")
#db.execute("CREATE TABLE holdings (id INTEGER NOT NULL, symbol TEXT NOT NULL, name TEXT NOT NULL, shares INTEGER, price TEXT NOT NULL, total INTEGER, time TEXT NOT NULL)")
# db.execute("CREATE TABLE indexinfo (id INTEGER NOT NULL, symbol TEXT NOT NULL, name TEXT NOT NULL, totalshares INTEGER, currentprice INTEGER, realtotal INTEGER)")
#used to reset db

#db.execute("CREATE TABLE holdings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, symbol TEXT NOT NULL, name TEXT NOT NULL, price INTEGER, total INTEGER)")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    #stock = lookup(quote)                                                       #use this for price and shit
    arrtotal = []
    id = session["user_id"]
    entries = db.execute("SELECT * FROM indexinfo WHERE id = ?", id)         #change the total and price numbers to actual price of stock at that time (use lookup and make total equal to lookupprice*shares)
    for index in range(len(entries)):
        realprice = lookup(entries[index]['symbol'])
        #print(realprice)                              #formatting works
        #print(entries[index]['totalshares'])
        entries[index]['currentprice'] = usd(realprice['price'])
        print(float(realprice['price']))
        entries[index]['realtotal'] = float(entries[index]['totalshares'])*float(realprice['price'])
        arrtotal.append(entries[index]['realtotal'])
        db.execute("UPDATE indexinfo SET realtotal = ? WHERE id = ? AND symbol = ?", entries[index]['realtotal'], id, entries[index]['symbol'])

    cash = db.execute("SELECT cash FROM users WHERE id = ?", id)                                            #CASH IS CORRECT AND TOTAL FOR EACH STOCK IS CORRECT, fix total equation
    #print(cash, "sus")
    value = [sub['cash'] for sub in cash]
    money = usd(value[0])
    # print(entries[index]['realtotal'])
    # print(money)

    #totalentry = db.execute("SELECT realtotal FROM indexinfo WHERE id = ?", id)
    #valuetotal = [sub['realtotal'] for sub in totalentry]   #total is adding
    valuetotal = arrtotal

    #print(valuetotal)
    #valuetotal = [float(x) for x in valuetotal]
    #value = Decimal(sub(r'[^\d.]', '', money))
    for i in range(len(valuetotal)):
        dollars = float(valuetotal[i]) #ended here to replace currency to float, this thing is fucking crazy :o
        valuetotal[i] = dollars                                 #check if total and all other numbers work when changing price on market open and work on sell
        #print(value)                                           #i also changed layout.html from container fluid to container
    #print(valuetotal)
    print(valuetotal)
    print(float(sum(valuetotal)))
    print(float(value[0]))
    total = float(sum(valuetotal)) + float(value[0])
    total = usd(total)
    #dollar_dec = float(dollars[1:])
    #total =

    # stock_symbol = stock['symbol']
    # symbols = db.execute("SELECT symbol FROM holdings WHERE id = ?", id)
    # knownSymbols = [sub['symbol'] for sub in symbols]
    # if stock_symbol in knownSymbols:
    #     shares = db.execute("SELECT SUM(shares) FROM holdings WHERE id = ? AND symbol = ?", id, stock_symbol)
    #     true_shares = [sub['SUM(shares)'] for sub in shares]
    #     new_shares = float(true_shares) + float(number)
    #     db.execute("UPDATE holdings SET shares = ? WHERE id = ? AND symbol = ?", new_shares, id, stock_symbol)

    return render_template("index.html", entries=entries, money=money, total=total)
    #return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        elif not request.form.get("shares"):
            return apology("must provide shares", 403)

        quote = request.form.get("symbol")
        number = request.form.get("shares")
        stock = lookup(quote)
        number = str(number)
        if number.isnumeric() == False:
            return apology("please enter a valid number of shares")
        for i in range(len(number)):
            if number[i] == "." :
                return apology("fractional shares not allowed")
            i += 1
        number = float(number)
        if stock == None:
            return apology("symbol doesn't exist")
        elif number < 1:
             return apology("must buy at least 1 share")

        #number = float(number)
        stock_price = stock['price']
        precost = stock_price*number
        cost = format(precost, '.2f')
        id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", id)
        value = [sub['cash'] for sub in cash]
        if float(value[0]) < float(cost):
            return apology("not enough cash")

        # stock_symbol = stock['symbol']
        # symbols = db.execute("SELECT symbol FROM holdings WHERE id = ?", id)
        # knownSymbols = [sub['symbol'] for sub in symbols]
        # if stock_symbol in knownSymbols:
        #     shares = db.execute("SELECT SUM(shares) FROM holdings WHERE id = ? AND symbol = ?", id, stock_symbol)
        #     true_shares = [sub['SUM(shares)'] for sub in shares]
        #     new_shares = float(true_shares) + float(number)
        #     db.execute("UPDATE holdings SET shares = ? WHERE id = ? AND symbol = ?", new_shares, id, stock_symbol)
        # else:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        # stock_price = float(format(stock_price, '.2f'))
        # cost = float(cost)
        # funds = round(float(funds), 2)
        # funds = float(funds)
        db.execute("INSERT INTO holdings (id, symbol, name, shares, price, total, time) VALUES(?, ?, ?, ?, ?, ?, ?)", id, stock['symbol'], stock['name'], number, usd(stock_price), float(cost), dt_string)

        stock_symbol = stock['symbol']
        symbols = db.execute("SELECT symbol FROM indexinfo WHERE id = ?", id)
        knownSymbols = [sub['symbol'] for sub in symbols]
        if stock_symbol in knownSymbols:
            shares = db.execute("SELECT totalshares FROM indexinfo WHERE id = ? AND symbol = ?", id, stock_symbol)
            true_shares = [sub['totalshares'] for sub in shares]
            new_shares = float(true_shares[0]) + float(number)
            db.execute("UPDATE indexinfo SET totalshares = ? WHERE id = ? AND symbol = ?", new_shares, id, stock_symbol)
        else:
            db.execute("INSERT INTO indexinfo (id, symbol, name, totalshares, currentprice, realtotal) VALUES(?, ?, ?, ?, ?, ?)", id, stock['symbol'], stock['name'], number, stock_price, float(cost))

        # sum = db.execute("SELECT SUM(total) FROM holdings WHERE id = ?", id)
        # truetotal = [sub['SUM(total)'] for sub in sum]
        truetotal = float(precost)
        print(truetotal)
        print(value[0])
        new_cash = float(value[0]) - float(truetotal)         #try to do something where if the price of a certian stock is the same price when u buy it u
        print(new_cash)

        #insert new_cash in table here (value for whatever id its associated with) replace the cash of one table to other
        #probably want to kill off the db when changes are made
        #print(new_cash)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, id)

        return redirect("/")
    else:
        return render_template("buy.html")
    #return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    id = session["user_id"]
    table = db.execute("SELECT * FROM holdings WHERE id = ?", id)
    return render_template("history.html", table=table)
    #return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        quote = request.form.get("symbol")
        stock = lookup(quote)
        if stock == None:
            return apology("symbol doesn't exist")
        return render_template("quoted.html", stock=stock)
    else:
        return render_template("quote.html")
    #return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    required_chars = ["!","@","#","$","%","^","&","*","(",")","-","+","?","_",".","=",",","<",">","/","'","|"]
    required_nums = ["0","1","2","3","4","5","6","7","8","9"]
    if request.method == "POST":
        user_name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif password != confirmation:
            return apology("passwords must match", 400)
        elif len(rows) == 1:
            return apology("username already taken", 400)
        elif len(password) >= 8:
            if any(letter in password for letter in required_chars):
                if any(letter in password for letter in required_nums):
                    db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", user_name, generate_password_hash(password))
                    return redirect("/")
                else:
                    return apology("password must have special char and num", 400)
            else:
                return apology("password must have special char and num", 400)
        else:
            return apology("password must be 8 characters or greater", 400)

    else:
        return render_template("register.html")
    #return apology("TODO")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock""" #just slapped buy function on here have fun
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        elif not request.form.get("shares"):
            return apology("must provide shares", 403)

        quote = request.form.get("symbol")
        number = request.form.get("shares")
        id = session["user_id"]
        stock = lookup(quote)

        number = str(number)
        if number.isnumeric() == False:
            return apology("please enter a valid number of shares")
        for i in range(len(number)):
            if number[i] == "." :
                return apology("fractional shares not allowed")
            i += 1
        number = float(number)


        stock_symbol = stock['symbol']
        symbols = db.execute("SELECT symbol FROM indexinfo WHERE id = ?", id)
        knownSymbols = [sub['symbol'] for sub in symbols]
        amount = db.execute("SELECT totalshares FROM indexinfo WHERE id = ? AND symbol = ?", id, quote)
        trueamount = [sub['totalshares'] for sub in amount]


        if quote not in knownSymbols:
            return apology("symbol doesn't exist")
        elif number < 1:
             return apology("must buy at least 1 share")
        elif number > float(trueamount[0]):
             return apology("you don't own that many shares")

        number = -abs(number)
        stock_price = stock['price']
        precost = stock_price*number
        cost = format(precost, '.2f')
        cash = db.execute("SELECT cash FROM users WHERE id = ?", id)
        value = [sub['cash'] for sub in cash]
        # if float(value[0]) < float(cost):
        #     return apology("not enough cash")


        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        db.execute("INSERT INTO holdings (id, symbol, name, shares, price, total, time) VALUES(?, ?, ?, ?, ?, ?, ?)", id, stock['symbol'], stock['name'], number, usd(stock_price), float(cost), dt_string)

        # if stock_symbol in knownSymbols:
        shares = db.execute("SELECT totalshares FROM indexinfo WHERE id = ? AND symbol = ?", id, stock_symbol)
        true_shares = [sub['totalshares'] for sub in shares]
        new_shares = float(true_shares[0]) + float(number)
        if new_shares == 0:
            db.execute("DELETE FROM indexinfo WHERE id = ? AND symbol = ?", id, stock_symbol)
        else:
            db.execute("UPDATE indexinfo SET totalshares = ? WHERE id = ? AND symbol = ?", new_shares, id, stock_symbol)
        # else:
        #     db.execute("INSERT INTO indexinfo (id, symbol, name, totalshares, currentprice, realtotal) VALUES(?, ?, ?, ?, ?, ?)", id, stock['symbol'], stock['name'], number, stock_price, cost)

        truetotal = abs(float(precost))
        print(truetotal)
        print(value[0])
        new_cash = float(value[0]) + float(truetotal)
        print(new_cash)

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, id)

        return redirect("/")
    else:
        #stock_symbol = stock['symbol']
        id = session["user_id"]
        symbols = db.execute("SELECT symbol FROM indexinfo WHERE id = ?", id)
        knownSymbols = [sub['symbol'] for sub in symbols]
        return render_template("sell.html", knownSymbols=knownSymbols)
    #return apology("TODO")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        if not request.form.get("funds"):
            return apology("must provide amount of funds", 403)

        funds = request.form.get("funds")
        id = session["user_id"]

        # if funds[0] == "-" :
        #     if funds[1:].isnumeric() == False:
        #         return apology("please enter a valid number of dollars")

        # if funds.isnumeric() == False:
        #     return apology("please enter a valid number of dollars")

        funds = round(float(funds), 2)
        funds = float(funds)
        if funds <= 0:
            return apology("enter a valid amount to deposit", 403)
        # elif funds.isnumeric() == False:
        #     return apology("please enter a valid number")

        cash = db.execute("SELECT cash FROM users WHERE id = ?", id)
        value = [sub['cash'] for sub in cash]

        new_cash = float(value[0]) + float(funds)
        #print(new_cash)

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, id)

        return redirect("/")
    else:
        return render_template("add.html")
    #return apology("TODO")


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    if request.method == "POST":
        if not request.form.get("funds"):
            return apology("must provide amount of funds", 403)

        funds = request.form.get("funds")
        id = session["user_id"]

        # if funds[0] == "-" :
        #     if funds[1:].isnumeric() == False:
        #         return apology("please enter a valid number of dollars")

        # if funds.isnumeric() == False:
        #     return apology("please enter a valid number of dollars")

        funds = round(float(funds), 2)
        funds = float(funds)

        cash = db.execute("SELECT cash FROM users WHERE id = ?", id)
        value = [sub['cash'] for sub in cash]

        if funds <= 0:
            return apology("enter a valid amount to deposit", 403)
        elif funds > float(value[0]):
            return apology("cannot withdraw more cash than present", 403)
        # elif funds.isnumeric() == False:
        #     return apology("please enter a valid number")

        print(value[0])
        print(funds)
        new_cash = float(value[0]) - float(funds)
        print(new_cash)

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, id)

        return redirect("/")
    else:
        return render_template("remove.html")
    #return apology("TODO")
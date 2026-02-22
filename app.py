from datetime import datetime
import os, sqlite3
from flask import Flask,render_template,request,redirect,session

BASE_DIR=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__,
template_folder=os.path.join(BASE_DIR,"templates"),
static_folder=os.path.join(BASE_DIR,"static"))

app.secret_key="secret123"

def get_db():
    return sqlite3.connect(os.path.join(BASE_DIR,"gas.db"))

# ---------------- CREATE TABLES ----------------
con=get_db()
cur=con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
username TEXT,
email TEXT,
password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bookings(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
phone TEXT,
address TEXT,
city TEXT,
cylinder TEXT,
company TEXT,
quantity INTEGER,
date TEXT,
time TEXT,
slot TEXT,
payment TEXT,
status TEXT
)
""")
con.commit()


con=get_db()
cur=con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS hazard_history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
type TEXT,
scenario TEXT,
action TEXT,
time TEXT
)
""")

con.commit()
con.close()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return redirect("/welcome")
    
    
@app.route("/welcome")
def welcome():
    return render_template("welcome.html")
    
# -------- REGISTER --------
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form["name"]
        username=request.form["username"]
        email=request.form["email"]
        password=request.form["password"]

        con=get_db()
        cur=con.cursor()
        cur.execute("""
        INSERT INTO users(name,username,email,password)
        VALUES(?,?,?,?)
        """,(name,username,email,password))
        con.commit()
        con.close()

        return redirect("/login")

    return render_template("register.html")

# -------- LOGIN --------
@app.route("/login",methods=["GET","POST"])
def login():
    error=None

    if request.method=="POST":
        identity=request.form["identity"]
        password=request.form["password"]

        con=get_db()
        cur=con.cursor()

        cur.execute("""
        SELECT * FROM users
        WHERE (email=? OR username=?) AND password=?
        """,(identity,identity,password))

        user=cur.fetchone()
        con.close()

        if user:
            session["user"]=user[1]
            return redirect("/dashboard")
        else:
            error="Invalid login details"

    return render_template("login.html",error=error)

# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html",name=session["user"])
    
    
    
    
@app.route("/booking", methods=["GET","POST"])
def booking():

    if request.method=="POST":

        name = request.form["name"]
        phone = request.form["phone"]
        address = request.form["address"]
        city = request.form["city"]
        cylinder = request.form["cylinder"]
        company = request.form["company"]
        qty = request.form["quantity"]
        payment = request.form["payment"]

        con = get_db()
        cur = con.cursor()

        cur.execute("""
        INSERT INTO bookings
        (name,phone,address,city,cylinder,company,quantity,payment,status,time)
        VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))
        """,(name,phone,address,city,cylinder,company,qty,payment,"Pending"))

        con.commit()
        con.close()

        return redirect("/history")

    return render_template("index.html")
            
@app.route("/history")
def history():
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM bookings ORDER BY id DESC")
    data = cur.fetchall()

    con.close()

    return render_template("history.html", bookings=data)
    
@app.route("/cancel/<int:id>", methods=["POST"])
def cancel(id):
    con = get_db()
    cur = con.cursor()

    cur.execute("""
        DELETE FROM bookings
        WHERE id=?
    """, (id,))

    con.commit()
    con.close()

    return redirect("/history")     
    
    
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    phone = request.form["phone"]
    address = request.form["address"]
    city = request.form["city"]
    cylinder = request.form["cylinder"]
    company = request.form["company"]
    qty = request.form["quantity"]
    payment = request.form["payment"]

    con = get_db()
    cur = con.cursor()

    cur.execute("""
    INSERT INTO bookings
    (name, phone, address, city, cylinder, company, quantity, payment, date)
    VALUES (?,?,?,?,?,?,?,?,?)
    """,
    (name, phone, address, city, cylinder, company, qty, payment,
     datetime.now().strftime("%d-%m-%Y %H:%M"))
    )

    con.commit()
    con.close()

    return redirect("/history")
        
@app.route("/tips")
def tips():
    return render_template("tips.html")


@app.route("/emergency")
def emergency():
    return render_template("emergency.html")    
# ---------- HAZARD MODULE ----------

@app.route("/hazard")
def hazard():
    return render_template("hazard.html")


@app.route("/hazard/<type>")
def hazard_scenarios(type):
    return render_template("scenarios.html", type=type)


@app.route("/hazard/<type>/check", methods=["POST"])
def hazard_check(type):
    scenario = request.form["scenario"]
    level = request.form["level"]

    action = ""

    if type == "gas":
        action = "Turn off gas, open windows, do NOT use switches"
        color = "brown"

    elif type == "smoke":
        action = "Move away, cut power, call fire support"
        color = "gray"

    else:
        action = "Switch off appliances, improve ventilation"
        color = "orange"

    # save history
    con = get_db()
    cur = con.cursor()
    cur.execute("""
    INSERT INTO hazard_history(type,scenario,action,time)
    VALUES(?,?,?,datetime('now'))
    """,(type,scenario,action))
    con.commit()
    con.close()

    return render_template("alert.html",
            type=type,
            scenario=scenario,
            action=action,
            color=color)
            
            
              
                                                        
@app.route("/hazard-history")
def hazard_history():
    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM hazard_history ORDER BY id DESC")
    data = cur.fetchall()

    con.close()
    return render_template("hazard_history.html", data=data)         
    
@app.route("/hazard/gas")
def gas():
    return render_template("gas.html")

@app.route("/hazard/smoke")
def smoke():
    return render_template("smoke.html")

@app.route("/hazard/heat")
def heat():
    return render_template("heat.html")       
    
@app.route("/resolved", methods=["POST"])
def resolved():
    return render_template("safe.html")
    
                                                                                                                                                  
# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -------- FORGOT --------
@app.route("/forgot",methods=["GET","POST"])
def forgot():
    msg=None

    if request.method=="POST":
        email=request.form["email"]
        newpass=request.form["password"]

        con=get_db()
        cur=con.cursor()
        cur.execute("""
        UPDATE users SET password=? WHERE email=?
        """,(newpass,email))
        con.commit()
        con.close()

        msg="Password updated successfully"

    return render_template("forgot.html",msg=msg)


if __name__=="__main__":
    app.run(debug=True)
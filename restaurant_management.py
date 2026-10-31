"""
RESTAURANT TABLE RESERVATION AND DINING SCHEDULE MANAGEMENT SYSTEM
Single-file starter project.

"""

import sys
from datetime import date
from flask import Flask, request, redirect, url_for, flash, render_template_string
import mysql.connector
from mysql.connector import Error

# -------------------- MYSQL CONFIGURATION --------------------

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "tejas1741" 
DATABASE_NAME = "restaurant_db"

app = Flask(__name__)
app.secret_key = "RestaurantApp_Tejas_2026@SecureKey#92"

# -------------------- DATABASE SETUP --------------------

def server_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )

def get_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DATABASE_NAME
    )

def setup_database():
    conn = server_connection()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
    cursor.close()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_tables (
            id INT AUTO_INCREMENT PRIMARY KEY,
            table_number INT NOT NULL UNIQUE,
            capacity INT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Available'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            table_id INT NOT NULL,
            reservation_date DATE NOT NULL,
            reservation_time TIME NOT NULL,
            guests INT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (table_id) REFERENCES restaurant_tables(id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM restaurant_tables")
    if cursor.fetchone()[0] == 0:
        starter_tables = [
            (1, 2), (2, 2), (3, 4), (4, 4),
            (5, 4), (6, 4), (7, 6), (8, 6),
            (9, 2), (10, 4), (11, 6), (12, 8)
        ]
        cursor.executemany(
            "INSERT INTO restaurant_tables (table_number, capacity) VALUES (%s, %s)",
            starter_tables
        )

    conn.commit()
    cursor.close()
    conn.close()

# -------------------- DASHBOARD HTML + CSS --------------------

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FoodieCorner | Restaurant Dashboard</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{box-sizing:border-box}
body{margin:0;background:#081326;color:#edf3ff;font-family:Inter,Arial,sans-serif;font-size:14px}
.shell{display:flex;min-height:100vh}
.sidebar{width:235px;background:#0c192d;border-right:1px solid #203451;padding:25px 14px;display:flex;flex-direction:column}
.brand{display:flex;gap:12px;align-items:center;padding:0 8px 35px}
.brand-icon{font-size:30px}.brand b{font-size:19px}
.brand small,.admin small{display:block;color:#91a5c6;font-size:10px;margin-top:5px}
nav{display:grid;gap:9px}
nav a{color:#c5d3eb;text-decoration:none;padding:13px;border-radius:9px;font-weight:600}
nav a:hover,nav a.active{background:#234bc0;color:white}
.side-note{margin-top:auto;text-align:center;border:1px solid #203451;border-radius:12px;padding:20px 12px;line-height:1.6}
.side-note div{font-size:28px}.side-note p{font-size:12px;color:#91a5c6}
main{width:calc(100% - 235px);max-width:1600px;padding:25px 28px;margin:auto}
header,.welcome,.panel-title{display:flex;justify-content:space-between;align-items:center}
header{border-bottom:1px solid #203451;padding-bottom:18px}
header small{display:block;color:#91a5c6;letter-spacing:2px}
header h1{font-size:23px;margin:5px 0}.admin{text-align:right}
.welcome{padding:22px 0}.welcome h2{margin:0 0 7px;font-size:21px}
.welcome p,.muted{color:#91a5c6}.welcome p{margin:0}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}
.stat{border-radius:12px;padding:20px;min-height:120px;display:flex;align-items:center;gap:15px}
.stat-icon{font-size:26px;background:#ffffff25;border-radius:50%;width:50px;height:50px;display:grid;place-items:center}
.stat p{margin:0 0 8px}.stat strong{font-size:27px}.stat small{display:block;margin-top:7px}
.purple{background:linear-gradient(120deg,#713ff0,#542bd2)}
.green{background:linear-gradient(120deg,#0da77f,#087e70)}
.blue{background:linear-gradient(120deg,#2387ed,#1458cb)}
.orange{background:linear-gradient(120deg,#ee922d,#d65c1d)}
.grid{display:grid;grid-template-columns:1.2fr 1fr;gap:18px}
.lower{margin-top:18px}
.panel{background:#101f37;border:1px solid #203451;border-radius:12px;padding:18px;min-width:0}
.panel-title{margin-bottom:17px}.panel-title h3{font-size:15px;margin:0}
.legend{font-size:10px;display:flex;gap:9px}
.floor{position:relative;display:grid;grid-template-columns:1fr 95px;gap:10px;min-height:285px;padding:17px;border:1px solid #31496d;border-radius:8px;background:#09172b}
.table-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;align-content:center}
.table{min-height:55px;border-radius:9px;display:flex;flex-direction:column;justify-content:center;align-items:center;color:white}
.table small{font-size:9px;margin-top:4px}
.table.available{background:#0fae82}.table.occupied{background:#e64e5c}.table.reserved{background:#efa92e;color:#17243b}
.kitchen{border:1px solid #2c4263;border-radius:8px;display:grid;place-items:center;color:#8ea6ca;font-weight:700}
.entrance{position:absolute;bottom:-8px;left:42%;background:#101f37;padding:0 12px;color:#91a5c6;font-size:10px}
.booking{display:grid;grid-template-columns:78px 1fr 90px 95px;gap:8px;align-items:center;padding:13px 0;border-bottom:1px solid #203451;font-size:11px}
.booking:last-child{border:0}.booking small{display:block;color:#91a5c6;margin-top:5px}
.time{background:#ffb632;color:#17243b;border-radius:20px;padding:8px 4px;text-align:center;font-weight:700}
select,input{width:100%;padding:9px;border:1px solid #31496b;border-radius:7px;background:#0b1930;color:white}
.booking select{font-size:10px}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px}
.form-grid label{font-size:11px;color:#a9bbd7}
.form-grid input,.form-grid select{display:block;margin-top:6px}
.form-grid button{grid-column:1/-1;padding:13px;background:#2864f0;color:white;border:0;border-radius:7px;font-weight:700;cursor:pointer}
.quick{display:flex;flex-direction:column;gap:11px}
.quick a{padding:17px;text-align:center;text-decoration:none;color:white;background:#245fe7;border-radius:8px;font-weight:700}
.quick a:nth-of-type(2){background:#078c75}.quick a:nth-of-type(3){background:#6841dc}
.quick p{text-align:center;color:#8299bd;font-size:11px;margin-top:auto;padding-top:15px}
.alert{padding:11px;border-radius:7px}.alert.success{background:#0d654e}.alert.error{background:#7b2b38}
@media(max-width:1100px){.stats{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}}
@media(max-width:700px){.sidebar{width:175px;min-width:175px;padding:15px 8px}.brand{padding-bottom:22px}.brand-icon{font-size:23px}.brand b{font-size:15px}.brand small{font-size:9px}.side-note{display:none}
nav a{font-size:11px;padding:11px 8px}main{width:calc(100% - 175px);padding:14px 10px}
.stats{grid-template-columns:1fr}.booking{grid-template-columns:1fr 1fr}.form-grid{grid-template-columns:1fr}
.floor{grid-template-columns:1fr 65px}.table-grid{gap:7px}}
</style>
</head>
<body>
<div class="shell">
<aside class="sidebar">
 <div class="brand"><span class="brand-icon">🍴</span><div><b>FoodieCorner</b><small>Good Food • Great Moments</small></div></div>
 <nav>
  <a class="{{ 'active' if active_page == 'dashboard' else '' }}" href="{{ url_for('dashboard') }}">▦ &nbsp; Dashboard</a>
  <a class="{{ 'active' if active_page == 'reservations' else '' }}" href="{{ url_for('reservations_page') }}">▣ &nbsp; Reservations</a>
  <a class="{{ 'active' if active_page == 'tables' else '' }}" href="{{ url_for('tables_page') }}">▤ &nbsp; Tables</a>
  <a class="{{ 'active' if active_page == 'schedule' else '' }}" href="{{ url_for('schedule_page') }}">◷ &nbsp; Dining Schedule</a>
 </nav>
 <div class="side-note"><div>♨</div><b>Better Bookings<br>Happier Guests</b><p>Manage tables, reservations and dining schedules in one place.</p></div>
</aside>
<main>
<header><div><small>RESTAURANT MANAGEMENT</small><h1>Dashboard</h1></div><div class="admin">● &nbsp; Admin<small>Restaurant Manager</small></div></header>
<section class="welcome"><div><h2>Welcome Back, Admin! 👋</h2><p>Here's what's happening at your restaurant today.</p></div><span>📅 &nbsp; {{ today }}</span></section>
{% with messages = get_flashed_messages(with_categories=true) %}
{% if messages %}{% for category,message in messages %}<p class="alert {{ category }}">{{ message }}</p>{% endfor %}{% endif %}{% endwith %}
<section class="stats">
 <article class="stat purple"><span class="stat-icon">▣</span><div><p>Total Reservations</p><strong>{{ total_reservations }}</strong><small>Today</small></div></article>
 <article class="stat green"><span class="stat-icon">▤</span><div><p>Tables Occupied</p><strong>{{ occupied_tables }} / {{ total_tables }}</strong><small>Live table status</small></div></article>
 <article class="stat blue"><span class="stat-icon">♟</span><div><p>Total Guests Today</p><strong>{{ total_guests }}</strong><small>Expected guests</small></div></article>
 <article class="stat orange"><span class="stat-icon">◷</span><div><p>Upcoming Bookings</p><strong>{{ upcoming|length }}</strong><small>Next reservations</small></div></article>
</section>
<section class="grid">
 <article class="panel" id="tables"><div class="panel-title"><h3>▤ &nbsp; Restaurant Table Layout</h3><div class="legend">🟢 Available &nbsp; 🔴 Occupied &nbsp; 🟠 Reserved</div></div>
  <div class="floor"><div class="table-grid">{% for t in tables %}<div class="table {{ t.display_status|lower }}"><b>T{{ t.table_number }}</b><small>{{ t.capacity }} seats</small></div>{% endfor %}</div><div class="kitchen">KITCHEN</div><div class="entrance">ENTRANCE</div></div>
 </article>
 <article class="panel" id="reservations"><div class="panel-title"><h3>▣ &nbsp; Upcoming Reservations</h3></div>
 {% if upcoming %}{% for item in upcoming %}
 <div class="booking"><span class="time">{{ item.display_time }}</span><div><b>{{ item.customer_name }}</b><small>{{ item.phone }}</small></div><div>Table T{{ item.table_number }}<small>{{ item.guests }} guests</small></div>
 <form method="POST" action="{{ url_for('update_status', reservation_id=item.id) }}"><select name="status" onchange="this.form.submit()">{% for s in statuses %}<option value="{{ s }}" {% if item.status==s %}selected{% endif %}>{{ s }}</option>{% endfor %}</select></form></div>
 {% endfor %}{% else %}<p class="muted">No upcoming reservations yet.</p>{% endif %}
 </article>
</section>
<section class="grid lower">
 <article class="panel" id="new-reservation"><div class="panel-title"><h3>＋ &nbsp; Create New Reservation</h3></div>
 <form class="form-grid" method="POST" action="{{ url_for('reserve') }}">
  <label>Customer name<input name="customer_name" placeholder="e.g. Rohan Sharma" required></label>
  <label>Phone number<input name="phone" type="tel" placeholder="Phone number" required></label>
  <label>Date<input name="reservation_date" type="date" min="{{ today_iso }}" required></label>
  <label>Time<input name="reservation_time" type="time" required></label>
  <label>Guests<input name="guests" type="number" min="1" max="8" value="2" required></label>
  <label>Table<select name="table_id" required><option value="">Choose table</option>{% for t in tables %}<option value="{{ t.id }}">T{{ t.table_number }} — {{ t.capacity }} seats</option>{% endfor %}</select></label>
  <button type="submit">＋ Create Reservation</button>
 </form></article>
 <article class="panel quick"><div class="panel-title"><h3>⚡ &nbsp; Quick Actions</h3></div><a href="{{ url_for('schedule_page') }}">＋ &nbsp; New Reservation</a><a href="{{ url_for('tables_page') }}">▤ &nbsp; Manage Tables</a><a href="{{ url_for('reservations_page') }}">◷ &nbsp; View Reservations</a><p>Good Food • Great People • Perfect Reservations</p></article>
</section>
</main></div>
</body></html>
"""

# -------------------- FLASK ROUTES --------------------

@app.route("/")
def dashboard():
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT COUNT(*) AS total FROM reservations
            WHERE reservation_date=CURDATE() AND status <> 'Cancelled'
        """)
        total_reservations = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) AS total FROM restaurant_tables WHERE status='Occupied'")
        occupied_tables = cur.fetchone()["total"]

        cur.execute("""
            SELECT COALESCE(SUM(guests),0) AS total FROM reservations
            WHERE reservation_date=CURDATE() AND status <> 'Cancelled'
        """)
        total_guests = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) AS total FROM restaurant_tables")
        total_tables = cur.fetchone()["total"]

        cur.execute("""
            SELECT r.id, r.customer_name, r.phone, rt.table_number,
                   r.guests, r.status,
                   TIME_FORMAT(r.reservation_time, '%h:%i %p') AS display_time
            FROM reservations r
            JOIN restaurant_tables rt ON r.table_id=rt.id
            WHERE r.reservation_date >= CURDATE() AND r.status <> 'Cancelled'
            ORDER BY r.reservation_date, r.reservation_time LIMIT 8
        """)
        upcoming = cur.fetchall()

        cur.execute("""
            SELECT rt.id, rt.table_number, rt.capacity,
            CASE WHEN EXISTS (
                SELECT 1 FROM reservations r
                WHERE r.table_id=rt.id AND r.reservation_date=CURDATE()
                AND r.status IN ('Pending','Confirmed','Seated')
            ) THEN 'Reserved' ELSE rt.status END AS display_status
            FROM restaurant_tables rt ORDER BY rt.table_number
        """)
        tables = cur.fetchall()

        cur.close()
        conn.close()

        return render_template_string(
            DASHBOARD_HTML,
            total_reservations=total_reservations,
            occupied_tables=occupied_tables,
            total_guests=total_guests,
            total_tables=total_tables,
            upcoming=upcoming,
            tables=tables,
            today=date.today().strftime("%d %b %Y"),
            today_iso=date.today().isoformat(),
            statuses=["Pending", "Confirmed", "Seated", "Completed", "Cancelled"],
            active_page="dashboard"
        )
    except Error as error:
        return (
            "<h2>Database connection error</h2>"
            "<p>Check MySQL is running and your password is correct in this file.</p>"
            f"<pre>{error}</pre>",
            500
        )

MANAGEMENT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FoodieCorner | {{ page_title }}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{box-sizing:border-box}body{margin:0;background:#081326;color:#edf3ff;font-family:Inter,Arial,sans-serif;font-size:14px}
.shell{display:flex;min-height:100vh}.sidebar{width:235px;min-width:235px;background:#0c192d;border-right:1px solid #203451;padding:25px 14px;display:flex;flex-direction:column}
.brand{display:flex;gap:12px;align-items:center;padding:0 8px 35px}.brand-icon{font-size:30px}.brand b{font-size:19px}.brand small,.admin small{display:block;color:#91a5c6;font-size:10px;margin-top:5px}
nav{display:grid;gap:9px}nav a{color:#c5d3eb;text-decoration:none;padding:13px;border-radius:9px;font-weight:600}nav a:hover,nav a.active{background:#234bc0;color:white}
.side-note{margin-top:auto;text-align:center;border:1px solid #203451;border-radius:12px;padding:20px 12px;line-height:1.6}.side-note div{font-size:28px}.side-note p{font-size:12px;color:#91a5c6}
main{width:calc(100% - 235px);max-width:1500px;padding:25px 28px;margin:auto}header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #203451;padding-bottom:18px}header small{display:block;color:#91a5c6;letter-spacing:2px}header h1{font-size:23px;margin:5px 0}.admin{text-align:right}
.panel{background:#101f37;border:1px solid #203451;border-radius:12px;padding:20px;margin-top:22px;overflow-x:auto}.muted{color:#91a5c6}.alert{padding:11px;border-radius:7px}.alert.success{background:#0d654e}.alert.error{background:#7b2b38}
table{width:100%;border-collapse:collapse;min-width:720px}th,td{text-align:left;padding:13px 10px;border-bottom:1px solid #203451}th{color:#91a5c6;font-size:12px}td{font-size:13px}select,input{width:100%;padding:9px;border:1px solid #31496b;border-radius:7px;background:#0b1930;color:white}button{padding:10px 14px;border:0;border-radius:7px;background:#2864f0;color:white;font-weight:700;cursor:pointer}button:hover{filter:brightness(1.12)}.status-form{display:flex;gap:7px;min-width:180px}.status-form select{min-width:115px}
.table-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px}.table-card{background:#0b1930;border:1px solid #31496b;border-radius:10px;padding:16px}.table-card h3{margin:0 0 7px}.table-card p{color:#91a5c6;margin:5px 0 12px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.form-grid label{color:#a9bbd7;font-size:12px}.form-grid input,.form-grid select{display:block;margin-top:6px}.form-grid button{grid-column:1/-1;padding:13px}
@media(max-width:700px){.sidebar{width:175px;min-width:175px;padding:15px 8px}.brand{padding-bottom:22px}.brand-icon{font-size:23px}.brand b{font-size:15px}.brand small{font-size:9px}.side-note{display:none}nav a{font-size:11px;padding:11px 8px}main{width:calc(100% - 175px);padding:14px 10px}.form-grid{grid-template-columns:1fr}}
</style></head><body><div class="shell"><aside class="sidebar">
<div class="brand"><span class="brand-icon">🍴</span><div><b>FoodieCorner</b><small>Good Food • Great Moments</small></div></div>
<nav>
<a class="{{ 'active' if active_page == 'dashboard' else '' }}" href="{{ url_for('dashboard') }}">▦ &nbsp; Dashboard</a>
<a class="{{ 'active' if active_page == 'reservations' else '' }}" href="{{ url_for('reservations_page') }}">▣ &nbsp; Reservations</a>
<a class="{{ 'active' if active_page == 'tables' else '' }}" href="{{ url_for('tables_page') }}">▤ &nbsp; Tables</a>
<a class="{{ 'active' if active_page == 'schedule' else '' }}" href="{{ url_for('schedule_page') }}">◷ &nbsp; Dining Schedule</a>
</nav><div class="side-note"><div>♨</div><b>Better Bookings<br>Happier Guests</b><p>Manage tables, reservations and dining schedules in one place.</p></div>
</aside><main><header><div><small>RESTAURANT MANAGEMENT</small><h1>{{ page_title }}</h1></div><div class="admin">● &nbsp; Admin<small>Restaurant Manager</small></div></header>
{% with messages = get_flashed_messages(with_categories=true) %}{% if messages %}{% for category,message in messages %}<p class="alert {{ category }}">{{ message }}</p>{% endfor %}{% endif %}{% endwith %}
{{ page_content|safe }}
</main></div></body></html>
"""

@app.route("/reservations")
def reservations_page():
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT r.id, r.customer_name, r.phone, rt.table_number, r.reservation_date,
                   TIME_FORMAT(r.reservation_time, '%h:%i %p') AS display_time,
                   r.guests, r.status
            FROM reservations r JOIN restaurant_tables rt ON r.table_id=rt.id
            ORDER BY r.reservation_date DESC, r.reservation_time DESC, r.id DESC
        """)
        rows = cur.fetchall()
        cur.close(); conn.close()
        content = render_template_string("""
        <section class="panel"><h2>All Reservations</h2><p class="muted">View every booking and update its status below.</p>
        {% if rows %}<table><thead><tr><th>ID</th><th>Customer</th><th>Phone</th><th>Date</th><th>Time</th><th>Table</th><th>Guests</th><th>Status</th></tr></thead><tbody>
        {% for r in rows %}<tr><td>#{{ r.id }}</td><td>{{ r.customer_name }}</td><td>{{ r.phone }}</td><td>{{ r.reservation_date }}</td><td>{{ r.display_time }}</td><td>T{{ r.table_number }}</td><td>{{ r.guests }}</td><td><form class="status-form" method="POST" action="{{ url_for('update_status', reservation_id=r.id) }}"><input type="hidden" name="return_to" value="reservations"><select name="status">{% for st in statuses %}<option value="{{ st }}" {% if r.status==st %}selected{% endif %}>{{ st }}</option>{% endfor %}</select><button type="submit">Save</button></form></td></tr>{% endfor %}
        </tbody></table>{% else %}<p class="muted">No reservations have been created yet.</p>{% endif %}</section>
        """, rows=rows, statuses=["Pending", "Confirmed", "Seated", "Completed", "Cancelled"])
        return render_template_string(MANAGEMENT_HTML, page_title="Reservations", page_content=content, active_page="reservations")
    except Error as error:
        return f"<h2>Database error</h2><pre>{error}</pre>", 500

@app.route("/tables")
def tables_page():
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, table_number, capacity, status FROM restaurant_tables ORDER BY table_number")
        rows = cur.fetchall()
        cur.close(); conn.close()
        content = render_template_string("""
        <section class="panel"><h2>Manage Restaurant Tables</h2><p class="muted">Change a table's current status. Available, Occupied and Reserved are managed independently from reservation records.</p>
        <div class="table-cards">{% for t in rows %}<article class="table-card"><h3>Table T{{ t.table_number }}</h3><p>Seating capacity: {{ t.capacity }} guests</p><form method="POST" action="{{ url_for('update_table_status', table_id=t.id) }}"><label>Table status<select name="status">{% for st in statuses %}<option value="{{ st }}" {% if t.status==st %}selected{% endif %}>{{ st }}</option>{% endfor %}</select></label><br><br><button type="submit">Update Table</button></form></article>{% endfor %}</div></section>
        """, rows=rows, statuses=["Available", "Occupied", "Reserved"])
        return render_template_string(MANAGEMENT_HTML, page_title="Table Management", page_content=content, active_page="tables")
    except Error as error:
        return f"<h2>Database error</h2><pre>{error}</pre>", 500

@app.route("/schedule")
def schedule_page():
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, table_number, capacity, status FROM restaurant_tables ORDER BY table_number")
        tables = cur.fetchall()
        cur.close(); conn.close()
        content = render_template_string("""
        <section class="panel"><h2>Create New Reservation</h2><p class="muted">Enter the guest details and choose a suitable table and dining time.</p>
        <form class="form-grid" method="POST" action="{{ url_for('reserve') }}">
        <label>Customer name<input name="customer_name" placeholder="e.g. Rohan Sharma" required></label>
        <label>Phone number<input name="phone" type="tel" placeholder="Phone number" required></label>
        <label>Date<input name="reservation_date" type="date" min="{{ today_iso }}" required></label>
        <label>Time<input name="reservation_time" type="time" required></label>
        <label>Guests<input name="guests" type="number" min="1" max="8" value="2" required></label>
        <label>Table<select name="table_id" required><option value="">Choose table</option>{% for t in tables %}<option value="{{ t.id }}">T{{ t.table_number }} — {{ t.capacity }} seats ({{ t.status }})</option>{% endfor %}</select></label>
        <button type="submit">＋ Create Reservation</button></form></section>
        """, tables=tables, today_iso=date.today().isoformat())
        return render_template_string(MANAGEMENT_HTML, page_title="Dining Schedule", page_content=content, active_page="schedule")
    except Error as error:
        return f"<h2>Database error</h2><pre>{error}</pre>", 500

@app.route("/table/<int:table_id>/status", methods=["POST"])
def update_table_status(table_id):
    status = request.form.get("status")
    if status not in {"Available", "Occupied", "Reserved"}:
        flash("Invalid table status.", "error")
        return redirect(url_for("tables_page"))
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE restaurant_tables SET status=%s WHERE id=%s", (status, table_id))
        conn.commit()
        flash("Table status updated successfully.", "success")
    except Error as error:
        conn.rollback()
        flash("Database error: " + str(error), "error")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("tables_page"))

@app.route("/reserve", methods=["POST"])
def reserve():
    name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    table_id = request.form.get("table_id", type=int)
    booking_date = request.form.get("reservation_date")
    booking_time = request.form.get("reservation_time")
    guests = request.form.get("guests", type=int)

    if not all([name, phone, table_id, booking_date, booking_time, guests]) or guests < 1:
        flash("Please fill in every field with valid information.", "error")
        return redirect(url_for("dashboard"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT capacity FROM restaurant_tables WHERE id=%s", (table_id,))
        table = cur.fetchone()
        if not table or guests > table["capacity"]:
            flash("Choose a table with enough seats for your guests.", "error")
            return redirect(url_for("dashboard"))

        # A reservation blocks a table for a two-hour dining window.
        cur.execute("""
            SELECT COUNT(*) AS conflicts FROM reservations
            WHERE table_id=%s AND reservation_date=%s
            AND status IN ('Pending','Confirmed','Seated')
            AND NOT (
                reservation_time < SUBTIME(%s,'02:00:00')
                OR reservation_time > ADDTIME(%s,'02:00:00')
            )
        """, (table_id, booking_date, booking_time, booking_time))

        if cur.fetchone()["conflicts"] > 0:
            flash("This table is already booked near that time. Choose another table or time.", "error")
            return redirect(url_for("dashboard"))

        cur.execute("""
            INSERT INTO reservations
            (customer_name,phone,table_id,reservation_date,reservation_time,guests)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (name, phone, table_id, booking_date, booking_time, guests))
        conn.commit()
        flash("Reservation created successfully!", "success")
    except Error as error:
        conn.rollback()
        flash("Database error: " + str(error), "error")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("dashboard"))

@app.route("/reservation/<int:reservation_id>/status", methods=["POST"])
def update_status(reservation_id):
    status = request.form.get("status")
    allowed = {"Pending", "Confirmed", "Seated", "Completed", "Cancelled"}

    if status not in allowed:
        flash("Invalid reservation status.", "error")
        return redirect(url_for("dashboard"))

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE reservations SET status=%s WHERE id=%s",
            (status, reservation_id)
        )
        conn.commit()
        flash("Reservation status updated.", "success")
    except Error as error:
        conn.rollback()
        flash("Database error: " + str(error), "error")
    finally:
        cur.close()
        conn.close()

    if request.form.get("return_to") == "reservations":
        return redirect(url_for("reservations_page"))
    return redirect(url_for("dashboard"))

# -------------------- OPTIONAL TKINTER DESKTOP MODE --------------------

def run_tkinter():
    import tkinter as tk
    from tkinter import ttk, messagebox

    class RestaurantDesktop:
        def __init__(self, root):
            self.root = root
            root.title("FoodieCorner - Desktop Admin")
            root.geometry("1000x600")
            root.configure(bg="#0b172a")

            tk.Label(
                root, text="FoodieCorner | Reservation Admin",
                font=("Arial", 20, "bold"), bg="#0b172a", fg="white"
            ).pack(pady=15)

            columns = ("id", "customer", "phone", "table", "date", "time", "guests", "status")
            self.tree = ttk.Treeview(root, columns=columns, show="headings", height=18)
            headings = ["ID", "Customer", "Phone", "Table", "Date", "Time", "Guests", "Status"]
            widths = [55, 160, 120, 70, 110, 100, 70, 110]

            for col, heading, width in zip(columns, headings, widths):
                self.tree.heading(col, text=heading)
                self.tree.column(col, width=width, anchor="center")

            self.tree.pack(fill="both", expand=True, padx=18, pady=10)

            controls = tk.Frame(root, bg="#0b172a")
            controls.pack(pady=10)
            ttk.Button(controls, text="Refresh", command=self.load_data).pack(side="left", padx=6)
            ttk.Button(
                controls, text="Confirm selected booking",
                command=self.confirm_selected
            ).pack(side="left", padx=6)

            self.load_data()

        def load_data(self):
            for row in self.tree.get_children():
                self.tree.delete(row)
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    SELECT r.id,r.customer_name,r.phone,rt.table_number,
                    r.reservation_date,TIME_FORMAT(r.reservation_time,'%h:%i %p'),
                    r.guests,r.status
                    FROM reservations r
                    JOIN restaurant_tables rt ON r.table_id=rt.id
                    ORDER BY r.reservation_date DESC,r.reservation_time DESC
                """)
                for row in cur.fetchall():
                    self.tree.insert("", "end", values=row)
                cur.close()
                conn.close()
            except Error as error:
                messagebox.showerror("Database error", str(error))

        def confirm_selected(self):
            selected = self.tree.selection()
            if not selected:
                messagebox.showinfo("Select booking", "Please select a reservation first.")
                return
            reservation_id = self.tree.item(selected[0], "values")[0]
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE reservations SET status='Confirmed' WHERE id=%s",
                    (reservation_id,)
                )
                conn.commit()
                cur.close()
                conn.close()
                self.load_data()
                messagebox.showinfo("Updated", "Reservation marked as Confirmed.")
            except Error as error:
                messagebox.showerror("Database error", str(error))

    root = tk.Tk()
    RestaurantDesktop(root)
    root.mainloop()

# -------------------- START PROGRAM --------------------

if __name__ == "__main__":
    try:
        setup_database()
        print("MySQL database and tables are ready.")
        if "--desktop" in sys.argv:
            run_tkinter()
        else:
            print("Starting Flask dashboard at http://127.0.0.1:5000")
            app.run(debug=True)
    except Error as error:
        print("Could not connect to MySQL.")
        print("Check MYSQL_PASSWORD, MYSQL_USER and make sure MySQL Server is running.")
        print("Details:", error)

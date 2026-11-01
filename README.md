# 🍽️ Restaurant Management System - Python

A Python-based Restaurant Management System that helps manage restaurant table reservations, customer bookings, table availability, and dining schedules using Flask and MySQL.

## 📌 Features

- Interactive restaurant management dashboard
- Create new customer reservations
- Store customer reservation details in MySQL
- Manage restaurant table availability
- Display 12 pre-configured restaurant tables
- Track Available, Occupied, and Reserved table statuses
- View all customer reservations
- Update reservation statuses
- Manage dining schedules
- Check table seating capacity before booking
- Prevent overlapping table reservations within a two-hour booking window
- Display upcoming reservations
- Show daily reservation and guest statistics
- Optional Tkinter desktop administration interface
- Automatically create the MySQL database and required tables

## 💾 Database Storage

The project uses a MySQL database named:

`restaurant_db`

The database contains two main tables:

### 1. restaurant_tables

- Table ID
- Table Number
- Seating Capacity
- Table Status

### 2. reservations

- Reservation ID
- Customer Name
- Phone Number
- Table ID
- Reservation Date
- Reservation Time
- Number of Guests
- Reservation Status
- Booking Creation Date

## 🧠 Concepts Used

- Python Functions
- Flask Web Framework
- MySQL Database Connectivity
- SQL Queries
- Database Creation and Table Creation
- CRUD Operations
- Primary Key and Foreign Key
- Python Exception Handling
- HTML and CSS
- Jinja2 Template Rendering
- Form Handling
- Conditional Statements
- Loops
- Database Relationships
- Tkinter GUI Development
- Input Validation

## 📦 Libraries Used

Install the required libraries using:

```bash
pip install flask mysql-connector-python
```

**Built-in Python Modules:**

- `sys`
- `datetime`
- `tkinter`
- `ttk`
- `messagebox`

## ▶️ How to Run

**1. Install Python and MySQL Server**

Make sure Python and MySQL Server are installed and running on your computer.

**2. Configure MySQL Connection**

Update your MySQL username and password in the Python file.

```python
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_mysql_password"
DATABASE_NAME = "restaurant_db"
```

**3. Install Required Libraries**

```bash
pip install flask mysql-connector-python
```

**4. Run the Python File**

```bash
python restaurant_management.py
```

The application automatically creates the database and required tables.

**5. Open the Application**

Open your browser and visit:

```text
http://127.0.0.1:5000
```

### Optional Desktop Mode

The project also supports a Tkinter-based desktop administration interface.

Run the following command:

```bash
python restaurant_management.py --desktop
```

## 👨‍💻 Developed By

**Tejas Jadhao**

GitHub: [@tejkhemjadhao9606-glitch](https://github.com/tejkhemjadhao9606-glitch)

---

⭐ If you find this project useful, don't forget to give it a star on GitHub!

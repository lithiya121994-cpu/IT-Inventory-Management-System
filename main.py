# Mini_project-IT_Inventory_Management_System

import sqlite3
import re
from datetime import datetime

# Database Connection

con = sqlite3.connect("IT_Invntory.db")
c = con.cursor()

c.execute("PRAGMA foreign_keys = ON")
c.execute("PRAGMA busy_timeout = 30000")

# validation function for email,phone_no,dae,amount

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    return phone.isdigit() and len(phone) == 10

def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False
def validate_positive_amount(amount):
    return amount >= 0


# create employee table

c.execute("""
CREATE TABLE IF NOT EXISTS employees(
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT NOT NULL,
    department TEXT NOT NULL,
    email_id TEXT UNIQUE NOT NULL,
    phone_number TEXT NOT NULL
)
""")

# create login table
c.execute("""
CREATE TABLE IF NOT EXISTS login_users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    employee_id INTEGER,
    FOREIGN KEY(employee_id)
        REFERENCES employees(employee_id)
)
""")

con.commit()

# default admin login

c.execute("""
INSERT OR IGNORE INTO login_users
(user_name, password, role, employee_id)
VALUES (?, ?, ?, ?)
""", (
    "Admin",
    "Password@123",
    "Admin",
    None
))

con.commit()


# Register IT Staff and providing few access to inventory_managment_system

def register_user():
    print("\n========== REGISTER IT STAFF ==========")

    try:

        employee_id = int(input("Enter Employee ID: "))

        # checking employee exists

        c.execute("""
            SELECT employee_id, employee_name, department
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))
        employee = c.fetchone()

        if not employee:
            print("\nInvalid Employee ID!")
            print("Only existing employees can register.")
            return

        employee_name = employee[1]
        department = employee[2]

        print("\nEmployee Name:", employee_name)
        print("Department:", department)

        # oOnly employees from the IT department can register

        if department.strip().lower() != "it":

            print("\nRegistration denied!")
            print("Only employees from the IT department can register.")
            return

        # Checking employee have already account

        c.execute("""
            SELECT user_id, user_name
            FROM login_users
            WHERE employee_id = ?
        """, (employee_id,))

        existing_user = c.fetchone()

        if existing_user:

            print("\nThis employee is already registered!")
            print("Username:", existing_user[1])
            return

        # enter login details

        user_name = input("Enter username: ").strip()
        password = input("Enter password: ")
        confirm_password = input("Confirm password: ")


        # employee field validation

        if not user_name or not password:

            print("\nUsername and password cannot be empty.")
            return
        # password validation

        if password != confirm_password:
            print("\nPasswords do not match!")
            return

        # check user_name already exists

        c.execute("""
            SELECT user_id
            FROM login_users
            WHERE user_name = ?
        """, (user_name,))

        if c.fetchone():
            print("\nUsername already exists!")
            return

        # IT Department staff getting IT Staff role

        role = "IT Staff"
        # insert login account

        c.execute("""
            INSERT INTO login_users
            (user_name, password, role, employee_id)
            VALUES (?, ?, ?, ?)
        """, (
            user_name,
            password,
            role,
            employee_id
        ))

        con.commit()
        print("\nRegistration successful!")
        print("Employee ID:", employee_id)
        print("Employee:", employee_name)
        print("Username:", user_name)
        print("Role:", role)

    except ValueError:

        print("\nPlease enter a valid Employee ID.")

    except sqlite3.IntegrityError:
        con.rollback()
        print("\nUsername already exists!")

    except sqlite3.Error as e:
        con.rollback()
        print("\nDatabase error:", e)

# login

def login():

    print("\n========== LOGIN ==========")

    user_name = input("Enter username: ")
    password = input("Enter password: ")

    c.execute("""
        SELECT user_id, user_name, role, employee_id
        FROM login_users
        WHERE user_name = ?
        AND password = ?
    """, (
        user_name,
        password
    ))

    user = c.fetchone()
    if user:
        print("\nLogin successful!")
        print("Welcome,", user[1])
        print("Role:", user[2])
        return user

    else:
        print("\nInvalid username or password!")
        return None

# employee CRUD

def add_employee():
    print("\n========== ADD EMPLOYEE ==========")
    try:
        employee_name = input("Enter employee name: ")
        department = input("Enter department: ")
        email_id = input("Enter email ID: ")
        phone_number = input("Enter phone number: ")

        if not employee_name or not department or not email_id or not phone_number:
            print("All fields are required!")
            return
        if not validate_email(email_id):
            print("Invalid email address!")
            return
        if not validate_phone(phone_number):
            print("Phone number must contain exactly 10 digits!")
            return

        c.execute("""
            INSERT INTO employees
            (
                employee_name,
                department,
                email_id,
                phone_number
            )
            VALUES (?, ?, ?, ?)
        """, (
            employee_name,
            department,
            email_id,
            phone_number
        ))
        con.commit()
        print("Employee added successfully!")

    except sqlite3.IntegrityError:
        con.rollback()
        print("Email ID already exists!")

    except sqlite3.Error as e:
        con.rollback()
        print("Database error:", e)

# view employee()

def view_employees():

    print("\n========== EMPLOYEE LIST ==========")

    c.execute("""
        SELECT
            employee_id,
            employee_name,
            department,
            email_id,
            phone_number
        FROM employees
        ORDER BY employee_id
    """)

    employees = c.fetchall()

    if not employees:
        print("No employees found!")
        return

    print("-" * 100)
    print(
        f"{'ID':<8}"
        f"{'Name':<25}"
        f"{'Department':<20}"
        f"{'Email':<30}"
        f"{'Phone':<15}"
    )

    print("-" * 100)
    for employee in employees:

        print(
            f"{employee[0]:<8}"
            f"{employee[1]:<25}"
            f"{employee[2]:<20}"
            f"{employee[3]:<30}"
            f"{employee[4]:<15}"
        )
    print("-" * 100)

# update emplyee()

def update_employee():
    print("\n========== UPDATE EMPLOYEE ==========")
    try:
        employee_id = int(input("Enter Employee ID to update: "))


        c.execute("""
            SELECT
                employee_id,
                employee_name,
                department,
                email_id,
                phone_number
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))

        employee = c.fetchone()

        if not employee:
            print("Invalid Employee ID!")
            return

        print("\nCurrent Employee Details:")
        print("Name:", employee[1])
        print("Department:", employee[2])
        print("Email:", employee[3])
        print("Phone:", employee[4])

        employee_name = input("Enter new employee name: ")
        department = input("Enter new department: ")
        email_id = input("Enter new email ID: ")
        phone_number = input("Enter new phone number: ")

        if not employee_name or not department or not email_id or not phone_number:
            print("All fields are required!")
            return
        if not validate_email(email_id):
            print("Invalid email address!")
            return
        if not validate_phone(phone_number):
            print("Phone number must contain exactly 10 digits!")
            return

        c.execute("""
            UPDATE employees
            SET
                employee_name = ?,
                department = ?,
                email_id = ?,
                phone_number = ?
            WHERE employee_id = ?
        """, (
            employee_name,
            department,
            email_id,
            phone_number,
            employee_id
        ))
        con.commit()

        print("\nEmployee updated successfully!")

    except ValueError:
        print("Please enter a valid Employee ID.")
    except sqlite3.IntegrityError as e:

        con.rollback()

        print("Unable to update employee:", e)

    except sqlite3.Error as e:
        con.rollback()

        print("Database error:", e)


# delete employee()


def delete_employee():

    print("\n========== DELETE EMPLOYEE ==========")

    try:
        employee_id = int(input("Enter Employee ID to delete: "))


        c.execute("""
            SELECT employee_id, employee_name
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))

        employee = c.fetchone()


        if not employee:
            print("Invalid Employee ID!")
            return


        # checking active asset assignment status

        c.execute("""
            SELECT assignment_id
            FROM asset_assignments
            WHERE employee_id = ?
            AND returned_date IS NULL
        """, (employee_id,))

        assignment = c.fetchone()

        if assignment:
            print("Cannot delete this employee!")
            print("Employee currently has assigned assets.")
            return
# check login status

        c.execute("""
            SELECT user_id
            FROM login_users
            WHERE employee_id = ?
        """, (employee_id,))

        user_account = c.fetchone()
        if user_account:

            print("Cannot delete this employee!")
            print("This employee has a login account.")
            print("Delete the login account first.")
            return
        confirm = input(f"Are you sure you want to delete "f"{employee[1]}? (y/n): ")

        if confirm.lower() != "y":
            print("Delete cancelled.")
            return

        c.execute("""
            DELETE FROM employees
            WHERE employee_id = ?
        """, (employee_id,))

        con.commit()

        print("\nEmployee deleted successfully!")

    except ValueError:

        print("Please enter a valid Employee ID.")

    except sqlite3.IntegrityError as e:

        con.rollback()

        print("Cannot delete employee:", e)

    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)

# category table

c.execute("""
CREATE TABLE IF NOT EXISTS category(
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
)
""")

con.commit()


# add category()

def add_category():

    print("\n========== ADD CATEGORY ==========")

    try:

        category_name = input("Enter category name: ").strip()

        if category_name == "":
            print("Category name cannot be empty.")
            return

        c.execute("""
            INSERT INTO category
            (category_name)
            VALUES (?)
        """, (category_name,))

        con.commit()

        print("Category added successfully!")

    except sqlite3.IntegrityError:

        con.rollback()

        print("Category already exists!")
    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)
# view category()

def view_categories():

    print("\n========== CATEGORY LIST ==========")

    c.execute("""
        SELECT
            category_id,
            category_name
        FROM category
        ORDER BY category_id
    """)

    categories = c.fetchall()

    if not categories:
        print("No categories found!")
        return
    print("-" * 40)

    print(
        f"{'ID':<10}"
        f"{'Category Name':<25}"
    )

    print("-" * 40)
    for category in categories:
        print(
            f"{category[0]:<10}"
            f"{category[1]:<25}"
        )
    print("-" * 40)

# update category()

def update_category():

    print("\n========== UPDATE CATEGORY ==========")

    try:

        category_id = int(input("Enter Category ID to update: "))
        c.execute("""
            SELECT
                category_id,
                category_name
            FROM category
            WHERE category_id = ?
        """, (category_id,))

        category = c.fetchone()

        if not category:
            print("Invalid Category ID!")
            return

        print("\nCurrent Category:", category[1])
        category_name = input("Enter new category name: ").strip()
        if category_name == "":
            print("Category name cannot be empty.")
            return
        c.execute("""
            UPDATE category
            SET category_name = ?
            WHERE category_id = ?
        """, (
            category_name,
            category_id
        ))
        con.commit()
        print("\nCategory updated successfully!")
    except ValueError:
        print("Please enter a valid Category ID.")

    except sqlite3.IntegrityError as e:

        con.rollback()

        print("Category already exists:", e)

    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)

# delete category()

def delete_category():

    print("\n========== DELETE CATEGORY ==========")

    try:

        category_id = int(input("Enter Category ID to delete: "))

        c.execute("""
            SELECT
                category_id,
                category_name
            FROM category
            WHERE category_id = ?
        """, (category_id,))

        category = c.fetchone()
        if not category:
            print("Invalid Category ID!")
            return


        # Check whether assets use this category

        c.execute("""
            SELECT asset_id
            FROM IT_assets
            WHERE category_id = ?
        """, (category_id,))
        asset = c.fetchone()

        if asset:
            print("Cannot delete this category!")
            print("Assets are currently using this category.")
            return
        confirm = input(
            f"Are you sure you want to delete "
            f"{category[1]}? (y/n): "
        )

        if confirm.lower() != "y":
            print("Delete cancelled.")
            return
        c.execute("""
            DELETE FROM category
            WHERE category_id = ?
        """, (category_id,))
        con.commit()

        print("\nCategory deleted successfully!")
    except ValueError:

        print("Please enter a valid Category ID.")
    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)

# asset table

c.execute("""
CREATE TABLE IF NOT EXISTS IT_assets(
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_tag TEXT NOT NULL UNIQUE,
    asset_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    brand TEXT,
    model TEXT,
    serial_number TEXT UNIQUE,
    purchase_date TEXT,
    purchase_cost REAL,
    status TEXT NOT NULL DEFAULT 'Available',

    FOREIGN KEY(category_id)
    REFERENCES category(category_id)
)
""")

con.commit()

# add asset

def add_asset():

    print("\n========== ADD ASSET ==========")

    try:

        c.execute("""
            SELECT
                category_id,
                category_name
            FROM category
            ORDER BY category_id
        """)

        categories = c.fetchall()
        if not categories:

            print("No categories found!")
            print("Please add a category first.")
            return

        asset_tag = input("Enter asset tag: ").strip()
        asset_name = input("Enter asset name: ").strip()


        if not asset_tag or not asset_name:
            print("Asset tag and asset name are required!")
            return
        print("\nAvailable Categories:")
        for category in categories:
            print(
                f"{category[0]} - {category[1]}"
            )
        category_id = int(input("Enter category ID: "))
        c.execute("""
            SELECT category_id
            FROM category
            WHERE category_id = ?
        """, (category_id,))

        if not c.fetchone():
            print("Invalid Category ID!")
            return
        brand = input("Enter brand: ")
        model = input("Enter model: ")
        serial_number = input("Enter serial number: ")
        purchase_date = input("Enter purchase date (YYYY-MM-DD): ")

        if not validate_date(purchase_date):
            print("Invalid date! Please use YYYY-MM-DD.")
            return
        purchase_cost = float(input("Enter purchase cost: "))
        if not validate_positive_amount(purchase_cost):
            print("Purchase cost cannot be negative!")
            return
        c.execute("""
            INSERT INTO IT_assets
            (
                asset_tag,
                asset_name,
                category_id,
                brand,
                model,
                serial_number,
                purchase_date,
                purchase_cost
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset_tag,
            asset_name,
            category_id,
            brand,
            model,
            serial_number,
            purchase_date,
            purchase_cost
        ))

        con.commit()

        print("\nAsset added successfully!")

    except ValueError:
        print("Please enter valid values.")

    except sqlite3.IntegrityError as e:
        con.rollback()

        print(
            "Unable to add asset. "
            "Asset tag or serial number may already exist."
        )

        print("Database error:", e)
    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)

# view asset

def view_assets():
    print("\n========== ASSET LIST ==========")

    c.execute("""
        SELECT
            ia.asset_id,
            ia.asset_tag,
            ia.asset_name,
            c.category_name,
            ia.brand,
            ia.model,
            ia.serial_number,
            ia.purchase_date,
            ia.purchase_cost,
            ia.status
        FROM IT_assets ia
        JOIN category c
            ON ia.category_id = c.category_id
        ORDER BY ia.asset_id
    """)

    assets = c.fetchall()
    if not assets:
        print("No assets found!")
        return
    print("-" * 130)

    print(
        f"{'ID':<6}"
        f"{'Tag':<15}"
        f"{'Asset Name':<20}"
        f"{'Category':<15}"
        f"{'Brand':<15}"
        f"{'Model':<15}"
        f"{'Serial':<18}"
        f"{'Purchase Date':<15}"
        f"{'Cost':<15}"
        f"{'Status':<15}"
    )

    print("-" * 130)
    for asset in assets:

        cost = asset[8] if asset[8] is not None else 0
        print(
            f"{asset[0]:<6}"
            f"{asset[1]:<15}"
            f"{asset[2]:<20}"
            f"{asset[3]:<15}"
            f"{asset[4] or '-':<15}"
            f"{asset[5] or '-':<15}"
            f"{asset[6] or '-':<18}"
            f"{asset[7] or '-':<15}"
            f"{cost:<15.2f}"
            f"{asset[9]:<15}"
        )

    print("-" * 130)

# update asset


def update_asset():
    print("\n========== UPDATE ASSET ==========")
    try:
        asset_id = int(input("Enter Asset ID to update: "))
        c.execute("""
            SELECT
                asset_id,
                asset_tag,
                asset_name,
                category_id,
                brand,
                model,
                serial_number,
                purchase_date,
                purchase_cost,
                status
            FROM IT_assets
            WHERE asset_id = ?
        """, (asset_id,))


        asset = c.fetchone()
        if not asset:
            print("Invalid Asset ID!")
            return
        print("\nCurrent Asset Details:")
        print("Asset Tag:", asset[1])
        print("Asset Name:", asset[2])
        print("Brand:", asset[4])
        print("Model:", asset[5])
        print("Serial Number:", asset[6])
        print("Purchase Date:", asset[7])
        print("Purchase Cost:", asset[8])
        print("Status:", asset[9])

        asset_tag = input("Enter new asset tag: ")
        asset_name = input("Enter new asset name: ")
        c.execute("""
            SELECT
                category_id,
                category_name
            FROM category
            ORDER BY category_id
        """)
        categories = c.fetchall()
        if not categories:
            print("No categories available!")
            return
        print("\nAvailable Categories:")

        for category in categories:
            print(
                f"{category[0]} - {category[1]}"
            )

        category_id = int(
            input("Enter new Category ID: ")
        )

        c.execute("""
            SELECT category_id
            FROM category
            WHERE category_id = ?
        """, (category_id,))


        if not c.fetchone():
            print("Invalid Category ID!")
            return

        brand = input("Enter new brand: ")
        model = input("Enter new model: ")
        serial_number = input("Enter new serial number: ")
        purchase_date = input("Enter new purchase date (YYYY-MM-DD): ")

        if not validate_date(purchase_date):
            print("Invalid date! Please use YYYY-MM-DD.")
            return
        purchase_cost = float(input("Enter new purchase cost: "))

        if not validate_positive_amount(purchase_cost):
            print("Purchase cost cannot be negative!")
            return

        c.execute("""
            UPDATE IT_assets
            SET
                asset_tag = ?,
                asset_name = ?,
                category_id = ?,
                brand = ?,
                model = ?,
                serial_number = ?,
                purchase_date = ?,
                purchase_cost = ?
            WHERE asset_id = ?
        """, (
            asset_tag,
            asset_name,
            category_id,
            brand,
            model,
            serial_number,
            purchase_date,
            purchase_cost,
            asset_id
        ))

        con.commit()

        print("\nAsset updated successfully!")

    except ValueError:
        print("Please enter valid values.")

    except sqlite3.IntegrityError as e:

        con.rollback()

        print("Unable to update asset:", e)

    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)

# delete asset


def delete_asset():
    print("\n========== DELETE ASSET ==========")

    try:
        asset_id = int(input("Enter Asset ID to delete: "))
        c.execute("""
            SELECT
                asset_id,
                asset_tag,
                asset_name,
                status
            FROM IT_assets
            WHERE asset_id = ?
        """, (asset_id,))

        asset = c.fetchone()

        if not asset:
            print("Invalid Asset ID!")
            return
        if asset[3] == "Assigned":
            print("Cannot delete an assigned asset!")
            print("Please return the asset first.")
            return
        c.execute("""
            SELECT assignment_id
            FROM asset_assignments
            WHERE asset_id = ?
        """, (asset_id,))
        assignment = c.fetchone()
        if assignment:
            print("Cannot delete this asset!")
            print("This asset has assignment history.")
            print("Change the asset status to 'Retired' instead.")
            return
        confirm = input(
            f"Are you sure you want to delete "
            f"{asset[1]} - {asset[2]}? (y/n): "
        )

        if confirm.lower() != "y":
            print("Delete cancelled.")
            return

        c.execute("""
            DELETE FROM IT_assets
            WHERE asset_id = ?
        """, (asset_id,))

        con.commit()

        print("\nAsset deleted successfully!")
    except ValueError:

        print("Please enter a valid Asset ID.")

    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)

# asset assignment table

c.execute("""
CREATE TABLE IF NOT EXISTS asset_assignments(
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    assigned_date TEXT NOT NULL,
    returned_date TEXT,

    FOREIGN KEY(asset_id)
    REFERENCES IT_assets(asset_id),

    FOREIGN KEY(employee_id)
    REFERENCES employees(employee_id)
)
""")

con.commit()
# assign asset

def assign_asset():

    print("\n========== AVAILABLE ASSET ==========")
    c.execute("""
        SELECT
            asset_id,
            asset_tag,
            asset_name
        FROM IT_assets
        WHERE status = 'Available'
    """)


    assets = c.fetchall()

    if not assets:
        print("No available assets found!")
        return

    print("\nAvailable Assets:")
    print("=" * 60)

    for asset in assets:
        print(
            f"ID: {asset[0]} | "
            f"Tag: {asset[1]} | "
            f"Name: {asset[2]}"
        )

    print("=" * 60)

    try:
        asset_id = int(input("Enter Asset ID: "))

        c.execute("""
            SELECT asset_id
            FROM IT_assets
            WHERE asset_id = ?
            AND status = 'Available'
        """, (asset_id,))

        if not c.fetchone():
            print("Invalid Asset ID or asset is already assigned!")
            return

        # show employee

        c.execute("""
            SELECT
                employee_id,
                employee_name,
                department
            FROM employees
        """)


        employees = c.fetchall()

        if not employees:
            print("No employees found!")
            return
        print("\nAvailable Employees:")
        print("=" * 60)

        for employee in employees:
            print(
                f"ID: {employee[0]} | "
                f"Name: {employee[1]} | "
                f"Department: {employee[2]}"
            )
        print("=" * 60)

        employee_id = int(input("Enter Employee ID: "))

        c.execute("""
            SELECT employee_id
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))


        if not c.fetchone():
            print("Invalid Employee ID!")
            return

        assigned_date = input("Enter assignment date (YYYY-MM-DD): ")

        if not validate_date(assigned_date):

            print("Invalid date! Please use YYYY-MM-DD.")
            return
        c.execute("""
            INSERT INTO asset_assignments
            (asset_id,employee_id,assigned_date)VALUES (?, ?, ?)
        """, (asset_id,employee_id,assigned_date))
        c.execute("""
            UPDATE IT_assets
            SET status = 'Assigned'
            WHERE asset_id = ?
        """, (asset_id,))

        con.commit()
        print("\nAsset assigned successfully!")
    except ValueError:

        print("Please enter a valid number.")

    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)

# view assignment

def view_assignments():

    print("\n========== ASSET ASSIGNMENT DETAILS ==========")

    c.execute("""
        SELECT
            aa.assignment_id,
            aa.asset_id,
            ia.asset_tag,
            ia.asset_name,
            aa.employee_id,
            e.employee_name,
            e.department,
            aa.assigned_date,
            aa.returned_date
        FROM asset_assignments aa
        JOIN IT_assets ia
            ON aa.asset_id = ia.asset_id
        JOIN employees e
            ON aa.employee_id = e.employee_id
        ORDER BY aa.assignment_id
    """)

    assignments = c.fetchall()
    if not assignments:
        print("No asset assignments found!")
        return

    print("-" * 140)

    print(
        f"{'Assign ID':<12}"
        f"{'Asset ID':<10}"
        f"{'Asset Tag':<15}"
        f"{'Asset Name':<20}"
        f"{'Emp ID':<10}"
        f"{'Employee':<20}"
        f"{'Department':<15}"
        f"{'Assigned':<15}"
        f"{'Returned':<15}"
    )

    print("-" * 140)

    for assignment in assignments:

        print(
            f"{assignment[0]:<12}"
            f"{assignment[1]:<10}"
            f"{assignment[2]:<15}"
            f"{assignment[3]:<20}"
            f"{assignment[4]:<10}"
            f"{assignment[5]:<20}"
            f"{assignment[6]:<15}"
            f"{assignment[7]:<15}"
            f"{assignment[8] or '-':<15}"
        )

    print("-" * 140)


# return asset

def return_asset():
    try:
        employee_id = int(input("Enter Employee ID: "))

        c.execute("""
            SELECT
                employee_id,
                employee_name
            FROM employees
            WHERE employee_id = ?
        """, (employee_id,))


        employee = c.fetchone()

        if not employee:
            print("Invalid Employee ID!")
            return

        print("\nEmployee:", employee[1])
        c.execute("""
            SELECT
                aa.assignment_id,
                ia.asset_id,
                ia.asset_tag,
                ia.asset_name,
                aa.assigned_date
            FROM asset_assignments aa
            JOIN IT_assets ia
                ON aa.asset_id = ia.asset_id
            WHERE aa.employee_id = ?
            AND aa.returned_date IS NULL
            AND ia.status = 'Assigned'
        """, (employee_id,))

        assets = c.fetchall()
        if not assets:
            print("No assets are currently assigned "
                "to this employee."
            )
            return
        print("\nAssets assigned to this employee:")
        print("=" * 90)

        for asset in assets:
            print(
                f"Assignment ID: {asset[0]} | "
                f"Asset ID: {asset[1]} | "
                f"Asset Tag: {asset[2]} | "
                f"Asset Name: {asset[3]} | "
                f"Assigned Date: {asset[4]}"
            )


        print("=" * 90)
        assignment_id = int(input("Enter Assignment ID to return: "))
        c.execute("""
            SELECT asset_id
            FROM asset_assignments
            WHERE assignment_id = ?
            AND employee_id = ?
            AND returned_date IS NULL
        """, (
            assignment_id,
            employee_id
        ))

        assignment = c.fetchone()
        if not assignment:
            print("Invalid Assignment ID!")
            return
        asset_id = assignment[0]
        returned_date = input("Enter return date (YYYY-MM-DD): ")
        if not validate_date(returned_date):
            print("Invalid date! Please use YYYY-MM-DD.")
            return

        c.execute("""
            UPDATE asset_assignments
            SET returned_date = ?
            WHERE assignment_id = ?
        """, (
            returned_date,
            assignment_id
        ))

        c.execute("""
            UPDATE IT_assets
            SET status = 'Available'
            WHERE asset_id = ?
        """, (asset_id,))

        con.commit()

        print("\nAsset returned successfully!")
        print("Employee:", employee[1])
        print("Assignment ID:", assignment_id)
        print("Asset ID:", asset_id)
        print("Return Date:", returned_date)

    except ValueError:
        print("Please enter a valid number.")
    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)

# update asset status


def update_asset_status():

    print("\n========== UPDATE ASSET STATUS ==========")
    try:

        c.execute("""
            SELECT
                asset_id,
                asset_tag,
                asset_name,
                status
            FROM IT_assets
            ORDER BY asset_id
        """)

        assets = c.fetchall()
        if not assets:

            print("No assets found!")
            return

        print("\nAsset List:")
        print("=" * 80)
        print(
            f"{'Asset ID':<12}"
            f"{'Asset Tag':<15}"
            f"{'Asset Name':<25}"
            f"{'Status':<15}"
        )
        print("-" * 80)

        for asset in assets:
            print(
                f"{asset[0]:<12}"
                f"{asset[1]:<15}"
                f"{asset[2]:<25}"
                f"{asset[3]:<15}"
            )


        print("=" * 80)

        asset_id = int(input("Enter Asset ID to update: "))

        c.execute("""
            SELECT
                asset_id,
                asset_tag,
                asset_name,
                status
            FROM IT_assets
            WHERE asset_id = ?
        """, (asset_id,))


        asset = c.fetchone()

        if not asset:
            print("Invalid Asset ID!")
            return
        current_status = asset[3]
        print("\nCurrent Status:", current_status)
        if current_status == "Assigned":

            print(
                "\nThis asset is currently assigned "
                "to an employee."
            )

            print(
                "Please use 'Return Asset' "
                "to make it Available."
            )

            return
        print("\nAvailable Status:")
        print("1. Available")
        print("2. Maintenance")
        print("3. Retired")

        status_choice = input("Enter new status: " )
        if status_choice == "1":
            new_status = "Available"

        elif status_choice == "2":
            new_status = "Maintenance"

        elif status_choice == "3":
            new_status = "Retired"

        else:
            print("Invalid status choice!")
            return

        c.execute("""
            UPDATE IT_assets
            SET status = ?
            WHERE asset_id = ?
        """, (
            new_status,
            asset_id
        ))
        con.commit()

        print("\nAsset status updated successfully!")
        print("Asset ID:", asset_id)
        print("Asset Tag:", asset[1])
        print("New Status:", new_status)

    except ValueError:

        print("Please enter a valid number.")

    except sqlite3.Error as e:

        con.rollback()

        print("Database error:", e)


#  logged_in_menu

def logged_in_menu(user):

    user_id = user[0]
    user_name = user[1]
    role = user[2]
    employee_id = user[3]

    while True:
        print("\n")
        print("=" * 60)
        print(f"{'IT INVENTORY MANAGEMENT SYSTEM':^60}")
        print("=" * 60)

        print("Logged in user:", user_name)
        print("Role:", role)

        print("-" * 60)

        # admin menu

        if role == "Admin":
            print("1. Employee Management")
            print("2. Category Management")
            print("3. Asset Management")
            print("4. Assign Asset")
            print("5. Return Asset")
            print("6. View Asset Assignments")
            print("7. Update Asset Status")
            print("8. Logout")

        # IT staff menu

        elif role == "IT Staff":
            print("1. View Employees")
            print("2. View Categories")
            print("3. View Assets")
            print("4. Assign Asset")
            print("5. Return Asset")
            print("6. View Asset Assignments")
            print("7. Logout")
        else:
            print("Invalid user role!")
            return

        print("=" * 60)
        choice = input("Enter your choice: ")

        # admin operation

        if role == "Admin":
            if choice == "1":

                while True:
                    print("\n========== EMPLOYEE MANAGEMENT ==========")

                    print("1. Add Employee")
                    print("2. View Employees")
                    print("3. Update Employee")
                    print("4. Delete Employee")
                    print("5. Back")

                    employee_choice = input("Enter your choice: ")
                    if employee_choice == "1":
                        add_employee()

                    elif employee_choice == "2":
                        view_employees()

                    elif employee_choice == "3":
                        update_employee()

                    elif employee_choice == "4":
                        delete_employee()

                    elif employee_choice == "5":
                        break
                    else:
                        print("Invalid choice!")

            elif choice == "2":

                while True:

                    print("\n========== CATEGORY MANAGEMENT ==========")

                    print("1. Add Category")
                    print("2. View Categories")
                    print("3. Update Category")
                    print("4. Delete Category")
                    print("5. Back")


                    category_choice = input("Enter your choice: ")
                    if category_choice == "1":
                        add_category()

                    elif category_choice == "2":
                        view_categories()

                    elif category_choice == "3":
                        update_category()

                    elif category_choice == "4":
                        delete_category()

                    elif category_choice == "5":
                        break

                    else:

                        print("Invalid choice!")

            elif choice == "3":
                while True:

                    print("\n========== ASSET MANAGEMENT ==========")

                    print("1. Add Asset")
                    print("2. View Assets")
                    print("3. Update Asset")
                    print("4. Delete Asset")
                    print("5. Back")


                    asset_choice = input("Enter your choice: ")

                    if asset_choice == "1":
                        add_asset()

                    elif asset_choice == "2":
                        view_assets()

                    elif asset_choice == "3":
                        update_asset()

                    elif asset_choice == "4":
                        delete_asset()

                    elif asset_choice == "5":
                        break

                    else:
                        print("Invalid choice!")

            elif choice == "4":
                assign_asset()

            elif choice == "5":
                return_asset()

            elif choice == "6":
                view_assignments()

            elif choice == "7":
                update_asset_status()

            elif choice == "8":
                print("\nLogged out successfully!")

                break
            else:

                print("\nInvalid choice! Please try again.")

        elif role == "IT Staff":
            if choice == "1":
                view_employees()

            elif choice == "2":
                view_categories()

            elif choice == "3":
                view_assets()

            elif choice == "4":
                assign_asset()

            elif choice == "5":
                return_asset()

            elif choice == "6":
                view_assignments()

            elif choice == "7":

                print("\nLogged out successfully!")

                break
            else:

                print("\nInvalid choice! Please try again.")


# Main menu


def main_menu():

    while True:

        print("\n")
        print("=" * 50)
        print(f"{'IT INVENTORY MANAGEMENT SYSTEM':^50}")
        print("=" * 50)
        print("1. Register User")
        print("2. Login")
        print("3. Exit")
        print("=" * 50)
        choice = input("Enter your choice: ")
        if choice == "1":
            register_user()

        elif choice == "2":
            user = login()


            # Enter logged-in menu ONLY after successful login

            if user:
                logged_in_menu(user)

        elif choice == "3":
            print("\nThank you for using ""IT Inventory Management System!")
            break
        else:

            print("\nInvalid choice! Please try again.")
# program begin

print("Database and tables created successfully!")

try:
    main_menu()
finally:
    con.close()
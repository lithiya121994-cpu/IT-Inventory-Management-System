==============IT INVENTORY MANAGEMENT SYSTEM==============

1.Project Overview
================
The IT Inventory Management System is a simple Python based application used to manage an organization's 
IT employees, assets, asset categories, users, and asset assignments.
The system uses Python and SQLite to store and manage the data. 

It has two types of users: Admin and IT Staff.
The Admin has full access to the system, while IT Staff can mainly view assets and assign assets to employees.

The main purpose of this project is to make IT asset management easier and to keep proper records of assets
and the employees using them.

2.Technology Used
=================
#python
#SQLite3
#Regular Expression
#Datetime
#CLI

3.Main Features
===============

1.User Authentication
-Username
-Password
-User role
    1.1.Admin
        # Add employees
        # View employees
        # Update employees
        # Delete employees
        # Add categories
        # View categories
        # Update categories
        # Delete categories
        # Add assets
        # View assets
        # Update assets
        # Delete assets
        # Assign assets
        # Return assets
        # View asset assignments
        # Update asset status
    1.2.IT Staff
        # View employees
        # View categories
        # View assets
        # Assign assets
        # Return assets 
        # View asset assignments    

2.Employee details include:

-Employee ID
-Employee Name
-Department
-Email ID
-Phone Number

CRUD
====
1.Add Employee
2.View Employees
3.Update Employee
4.Delete Employee

Input validation is implemented for email addresses and phone numbers.

3.Category Management

Categories are used to organize IT assets.
-Laptop
-Desktop
-Monitor
-Printer
-Keyboard
-Mouse

The Admin can:

-Add Category
-View Categories
-Update Category
-Delete Category

A category cannot be deleted if it is currently being used by an IT asset.

4.Asset Management
-Asset ID
-Asset Tag
-Asset Name
-Category
-Brand
-Model
-Serial Number
-Purchase Date
-Purchase Cost
-Status

Available asset statuses are:

-Available
-Assigned
-Maintenance
-Retired

The Admin can:

-Add Asset
-View Assets
-Update Asset
-Delete Asset
-Update Asset Status

5.Asset Assignment

IT assets can be assigned to employees.

During assignment, the system checks:

-asset exists.
-asset is available.
-employee exists.
-assignment date is valid.

After successful assignment, the asset status is changed from:

Available → Assigned

The assignment history is stored in the database.

6.Asset Return

The system allows an asset to be returned using the employee ID.

The process is:

1.Enter Employee ID
        
2.Display currently assigned assets

3.Select Assignment ID
        
4.Enter Return Date
        
5.Return Asset

After returning the asset, its status changes from:

Assigned → Available

The return date is also stored in the assignment history.
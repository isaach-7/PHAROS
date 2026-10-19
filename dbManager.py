# dbManager.py
# Centralised database access module

import sqlite3

def getConnection():
    """
    Returns a connection to pharmacy database.
    Creates the file automatically if it doesn't exist
    """
    connection = sqlite3.connect("pharos.db")

    # Ensure foreign key relationships are enforced
    connection.execute("PRAGMA foreign_keys = ON;")

    return connection

# Central subroutine to call a table for initialization.
def initialiseDatabase():
    """
    Runs all database setup functions.
    Additional tables will be added here in later iterations.
    """
    createUsersTable()
    createProductsTable()
    createPrescriptionsTable()


'''USERS'''
# Creating users table
def createUsersTable():
    """
    Creates the Users table if it does not already exist.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            userID INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    """)

    connection.commit()
    connection.close()
# adding a user into users table
def addUser(username, password):
    """
    Inserts a new user into the Users table.
    Uses parameterised SQL to safely handle user input.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO Users (username, password) VALUES (?, ?);",
        (username, password)
    )

    connection.commit()
    connection.close()

    return True
def getUserByUsername(username):
    """
    Retrieves a user record using their username.
    Returns (userID, username, password) or None.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT userID, username, password FROM Users WHERE username = ?;",
        (username,)
    )

    row = cursor.fetchone()
    connection.close()

    return row

# Creating products table

def createProductsTable():
    """
    Creates the Products table if it does not already exist.
    This table stores product information displayed in the catalogue.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            productID INTEGER PRIMARY KEY AUTOINCREMENT,
            productName TEXT NOT NULL,
            description TEXT NOT NULL,
            dosageProd TEXT NOT NULL,
            price REAL NOT NULL CHECK(price >= 0),
            category TEXT NOT NULL,
            imagePath TEXT NOT NULL
        );
    """)

    connection.commit()
    connection.close()


# adding a product into products table

def addProduct(productName, description, dosageProd, price, category, imagePath):
    """
    Inserts a new product into the Products table.
    Uses parameterised SQL to safely store product data.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO Products (productName, description, dosageProd, price, category, imagePath)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (productName, description, dosageProd, price, category, imagePath)
    )

    connection.commit()
    connection.close()
    return True


# retrieving products from products table

def getAllProducts():
    """
    Retrieves all product records from the database for catalogue display.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT productID, productName, description, dosageProd, price, category, imagePath
        FROM Products;
    """)

    rows = cursor.fetchall()   # corrected: retrieves all rows instead of only one

    connection.close()
    return rows


def searchProducts(searchQuery):
    """
    Searches products by matching the search term against productName and description.
    """
    connection = getConnection()
    cursor = connection.cursor()

    wildcardQuery = "%" + searchQuery + "%"

    cursor.execute("""
        SELECT productID, productName, description, dosageProd, price, category, imagePath
        FROM Products
        WHERE productName LIKE ? OR description LIKE ?;
    """, (wildcardQuery, wildcardQuery))

    rows = cursor.fetchall()
    connection.close()
    return rows


def getProductsByCategory(category):
    """
    Retrieves products that match a selected category.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT productID, productName, description, dosageProd, price, category, imagePath
        FROM Products
        WHERE category = ?;
    """, (category,))

    rows = cursor.fetchall()
    connection.close()
    return rows


def getProductById(productId):
    """
    Retrieves one product using its productID.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT productID, productName, description, dosageProd, price, category, imagePath
        FROM Products
        WHERE productID = ?;
    """, (productId,))

    row = cursor.fetchone()
    connection.close()
    return row


def createPrescriptionsTable():
    """
    Creates the Prescriptions table if it does not already exist.
    This table stores prescription records linked to users and products,
    including patient details and date information for each entry.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Prescriptions (
            prescriptionID INTEGER PRIMARY KEY AUTOINCREMENT,
            userID INTEGER NOT NULL,
            productID INTEGER NOT NULL,
            fullName TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            issueDate TEXT NOT NULL,
            activeUntil TEXT NOT NULL,
            dosagePrs TEXT NOT NULL,
            frequency TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (userID) REFERENCES Users(userID),
            FOREIGN KEY (productID) REFERENCES Products(productID)
        );
    """)

    connection.commit()
    connection.close()


# adding a prescription into prescriptions table

def addPrescription(userId, productId, fullName, address, phone,
                    issueDate, activeUntil, dosagePrs, frequency, notes):
    """
    Inserts a new prescription into the Prescriptions table.
    Uses parameterised SQL to safely store prescription data.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO Prescriptions (userID, productID, fullName, address,
                                   phone, issueDate, activeUntil,
                                   dosagePrs, frequency, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (userId, productId, fullName, address, phone,
         issueDate, activeUntil, dosagePrs, frequency, notes)
    )

    connection.commit()
    connection.close()
    return True

def getPrescriptionsByUserId(userId):
    """
    Retrieves all prescription records belonging to a specific user.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT prescriptionID, userID, productID, fullName, address,
               phone, issueDate, activeUntil, dosagePrs, frequency, notes
        FROM Prescriptions
        WHERE userID = ?;
    """, (userId,))

    rows = cursor.fetchall()
    connection.close()
    return rows


def getPrescriptionById(prescriptionId):
    """
    Retrieves a single prescription using its prescriptionID.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT prescriptionID, userID, productID, fullName, address,
               phone, issueDate, activeUntil, dosagePrs, frequency, notes
        FROM Prescriptions
        WHERE prescriptionID = ?;
    """, (prescriptionId,))

    row = cursor.fetchone()
    connection.close()
    return row


def updatePrescription(prescriptionId, fullName, address, phone,
                       issueDate, activeUntil, dosagePrs, frequency, notes):
    """
    Updates all editable fields of an existing prescription.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE Prescriptions
        SET fullName = ?, address = ?, phone = ?, issueDate = ?,
            activeUntil = ?, dosagePrs = ?, frequency = ?, notes = ?
        WHERE prescriptionID = ?;
    """, (fullName, address, phone, issueDate, activeUntil,
          dosagePrs, frequency, notes, prescriptionId))

    connection.commit()
    connection.close()
    return True


def deletePrescription(prescriptionId):
    """
    Deletes a prescription using its prescriptionID.
    """
    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM Prescriptions
        WHERE prescriptionID = ?;
    """, (prescriptionId,))

    connection.commit()
    connection.close()
    return True
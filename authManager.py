from dbManager import addUser, getUserByUsername

def registerUser(newUsername, newPassword, confirmPassword):

    # Check that required fields are not blank
    if newUsername.strip() == "" or newPassword.strip() == "" or confirmPassword.strip() == "":
        return "Username and password fields cannot be blank"
    
    if newPassword != confirmPassword:
        return "Passwords do not match"
    
    # Check if username already exists
    existingUser = getUserByUsername(newUsername)

    if existingUser is not None:
        return "Username already exists"

    # Insert the user into the database
    addUser(newUsername, newPassword)

    return "Registration successful"

def loginUser(username, password):
    # Check that the fields are not blank
    if username.strip() == "" or password.strip() == "":
        return "Username and password cannot be blank"

    # Retrieve the user record using the entered username
    userRecord = getUserByUsername(username)

    # Check whether the username exists
    if userRecord is None:
        return "Username not found"

    # Retrieve the stored password from the database record
    storedPassword = userRecord[2]

    # Check whether the entered password matches the stored password
    if password == storedPassword:
        return "Login successful"

    return "Incorrect password"
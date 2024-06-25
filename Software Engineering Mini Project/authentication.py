import asyncio
import websockets
import json
import mysql.connector


async def receive_admin_data(websocket, path):
    data = await websocket.recv()
    parsed_data = json.loads(data)
    # Print the contents of the object
    email = parsed_data['email']
    password = parsed_data['password']
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1114',
            database='authentication'
        )
        if connection.is_connected():
            # Perform database operations (e.g., authenticate user)
            cursor = connection.cursor()
            query = "SELECT * FROM ADMIN WHERE email = %s AND password = %s"
            cursor.execute(query, (email, password))
            result = cursor.fetchone()
            if result: 
                await websocket.send("Admin authenticated")
            else:
                await websocket.send("Invalid email or password")
            cursor.close()
            connection.close()
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")


async def receive_user_data(websocket, path):
    data = await websocket.recv()
    parsed_data = json.loads(data)
    # Print the contents of the object
    email = parsed_data['email']
    password = parsed_data['password']
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1114',
            database='authentication'
        )
        if connection.is_connected():
            # Perform database operations (e.g., authenticate user)
            cursor = connection.cursor()
            query = "SELECT email,password FROM user WHERE email = %s AND password = %s"
            cursor.execute(query, (email, password))
            result = cursor.fetchone()
            if result: 
                await websocket.send("User authenticated")
            else:
                await websocket.send("Invalid email or password")
            cursor.close()
            connection.close()
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")


async def receive_register_data(websocket, path):
    data = await websocket.recv()
    parsed_data = json.loads(data)
    # Print the contents of the object
    name = parsed_data['name']
    email = parsed_data['email']
    password = parsed_data['password']
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1114',
            database='authentication'
        )
        if connection.is_connected():
            # Perform database operations (e.g., authenticate user)
            cursor = connection.cursor()
            query = "SELECT * FROM user WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            if result:
                await websocket.send("User already exists")
            else:
                # Insert the new user if the user does not already exist
                query = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
                cursor.execute(query, (name, email, password))
                connection.commit()  # Commit the transaction
                await websocket.send("User registered successfully")
            cursor.close()
            connection.close()
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")

async def receive_update_data(websocket, path):
    data = await websocket.recv()
    parsed_data = json.loads(data)
    # Print the contents of the object
    email = parsed_data['email']
    password = parsed_data['password']
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1114',
            database='authentication'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            # Check if the user with the provided email already exists
            query = "SELECT * FROM user WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            if result:
                # If the user exists, update the password
                update_query = "UPDATE user SET password = %s WHERE email = %s"
                cursor.execute(update_query, (password, email))
                connection.commit()  # Commit the transaction
                await websocket.send("Password updated successfully")
            else:
                # If the user does not exist, send a message indicating that the user does not exist
                await websocket.send("User does not exist")
            cursor.close()
            connection.close()
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
    


start_server_admin = websockets.serve(receive_admin_data, "localhost", 8765)
start_server_user = websockets.serve(receive_user_data,"localhost",8766)
start_server_register = websockets.serve(receive_register_data,"localhost",8767)
start_server_update = websockets.serve(receive_update_data,"localhost",8768)

asyncio.get_event_loop().run_until_complete(start_server_admin)
asyncio.get_event_loop().run_until_complete(start_server_user)
asyncio.get_event_loop().run_until_complete(start_server_register)
asyncio.get_event_loop().run_until_complete(start_server_update)
asyncio.get_event_loop().run_forever()




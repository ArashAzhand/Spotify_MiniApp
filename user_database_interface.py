from tkinter import messagebox
import pyodbc
def connect_to_db():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=LAPTOP-KE2OAO1H;'
        'DATABASE=temp_spotify;'
        'Trusted_Connection=yes;',
        autocommit=True
    )
    return conn



def insert_user(user_name, password, birth_year, email, location, isartist):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            EXEC InsertUser ?, ?, ?, ?, ?, ?
        """, (user_name, password, birth_year, email, location, isartist))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_user(user_id, user_name, password, birth_year, email, country_id):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            EXEC UpdateUser ?, ?, ?, ?, ?, ?
        """, (user_id, user_name, password, birth_year, email, country_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_user(user_id):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            EXEC DeleteUser ?
        """, (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))
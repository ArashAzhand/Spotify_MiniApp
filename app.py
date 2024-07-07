import tkinter as tk
from tkinter import messagebox
from user_database_interface import *
from user_page import *
import pyodbc


def connect_to_db():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=LAPTOP-KE2OAO1H;' #select @@SERVERNAME
        'DATABASE=temp_spotify;'
        'Trusted_Connection=yes;',
        autocommit=True
    )
    return conn


def open_user_window(username):
    root = tk.Tk()
    root.title("User Page")
    root.geometry("800x600")

    def return_to_login():
        root.destroy()
        main_login_window()

    create_user_page(root, username, return_to_login)

    root.mainloop()





def open_singer_window():
    singer_window = tk.Tk()
    singer_window.title("Singer Window")
    singer_window.geometry("300x200")

    singer_label = tk.Label(singer_window, text="Welcome, Singer!")
    singer_label.pack(pady=20)

    singer_window.mainloop()




def create_user_account_window():
    def create_account():
        new_username = new_username_entry.get()
        new_password = new_password_entry.get()
        b_y = new_BirthYear_entry.get()
        email = new_Email_entry.get()
        loc = new_Location_entry.get()

        insert_user(new_username, new_password, b_y, email, loc)
        account_window.destroy()


    account_window = tk.Tk()
    account_window.title("Create New Account")
    account_window.geometry("300x250")

    new_username_label = tk.Label(account_window, text="New Username")
    new_username_label.grid(row=1, column=0, pady=5)
    new_username_entry = tk.Entry(account_window)
    new_username_entry.grid(row=1, column=1, pady=5)

    new_password_label = tk.Label(account_window, text="New Password")
    new_password_label.grid(row=2, column=0, pady=5)
    new_password_entry = tk.Entry(account_window, show="*")
    new_password_entry.grid(row=2, column=1, pady=5)

    new_BirthYear_label = tk.Label(account_window, text="BirthYear")
    new_BirthYear_label.grid(row=3, column=0, pady=5)
    new_BirthYear_entry = tk.Entry(account_window)
    new_BirthYear_entry.grid(row=3, column=1, pady=5)

    new_Email_label = tk.Label(account_window, text="Email")
    new_Email_label.grid(row=4, column=0, pady=5)
    new_Email_entry = tk.Entry(account_window)
    new_Email_entry.grid(row=4, column=1, pady=5)

    new_Location_label = tk.Label(account_window, text="Location")
    new_Location_label.grid(row=5, column=0, pady=5)
    new_Location_entry = tk.Entry(account_window)
    new_Location_entry.grid(row=5, column=1, pady=5)

    create_account_button = tk.Button(account_window, text="Create Account", command=create_account)
    create_account_button.grid(row=6,column=1,pady=20)

    account_window.mainloop()

def main_login_window():
    def check_login():
        username = username_entry.get()
        password = password_entry.get()
        role = role_var.get()

        if role == "User":
            try:
                conn = connect_to_db()
                cursor = conn.cursor()

                query = """
                SELECT * FROM Users 
                WHERE username = ? AND password = ?
                """
                cursor.execute(query, (username, password))

                user = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if user:
                    messagebox.showinfo("Login succesfull", f"wellcome {username}")
                    login_window.destroy()
                    open_user_window(username)
                else:
                    messagebox.showerror("Login failed", "Invalid username or password!")
            
            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
                return False

        else:
            try:
                conn = connect_to_db()
                cursor = conn.cursor()
                

                query = """
                SELECT * FROM Artists 
                WHERE ArtistName = ? AND Password = ?
                """
                cursor.execute(query, (username, password))

                user = cursor.fetchone()
                cursor.close()
                conn.close()

                if user:
                    messagebox.showinfo("login succesful", f"wellcome {username}")                     
                    login_window.destroy()    
                    open_singer_window(username)
                else:
                    messagebox.showerror("Login failed", "Invalid artistname or password!")

            except Exception as e:
                messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
                return False



    login_window = tk.Tk()
    login_window.title("Login Window")
    login_window.geometry("300x300")

    username_label = tk.Label(login_window, text="Username")
    username_label.pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    password_label = tk.Label(login_window, text="Password")
    password_label.pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    role_var = tk.StringVar(value="User")
    user_check = tk.Radiobutton(login_window, text="User", variable=role_var, value="User")
    user_check.pack(pady=5)
    singer_check = tk.Radiobutton(login_window, text="Singer", variable=role_var, value="Singer")
    singer_check.pack(pady=5)

    login_button = tk.Button(login_window, text="Login", command=check_login)
    login_button.pack(pady=20)




    create_account_button = tk.Button(login_window, text="Create New User Account", command=create_user_account_window)
    create_account_button.pack(pady=10)

    login_window.mainloop()


# main_login_window()
open_user_window("arash")
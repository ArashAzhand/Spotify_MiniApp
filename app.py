import customtkinter as ctk
from tkinter import messagebox
from user_database_interface import *
from user_page import *
import pyodbc

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("dark-blue")  

SPOTIFY_GREEN = "#1DB954"
SPOTIFY_BLACK = "#121212"
SPOTIFY_GRAY = "#212121"
SPOTIFY_WHITE = "#FFFFFF"

def connect_to_db():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=LAPTOP-KE2OAO1H;'
        'DATABASE=temp_spotify;'
        'Trusted_Connection=yes;',
        autocommit=True
    )
    return conn



def open_user_window(username):
    root = ctk.CTk()
    root.title("Spotify - User Page")
    root.geometry("800x600")
    root.configure(fg_color=SPOTIFY_BLACK)

    def return_to_login():
        root.destroy()
        main_login_window()

    def reset_user_page():
        root.destroy()
        open_user_window(username)

    create_user_page(root, username, return_to_login, reset_user_page, 0)

    root.mainloop()
    
def open_artist_window(username):
    root = ctk.CTk()
    root.title("Spotify - Artist Page")
    root.geometry("800x600")
    root.configure(fg_color=SPOTIFY_BLACK)

    def return_to_login():
        root.destroy()
        main_login_window()

    def reset_user_page():
        root.destroy()
        open_artist_window(username)

    create_user_page(root, username, return_to_login, reset_user_page, 1)

    root.mainloop()

def create_user_account_window():
    def create_account():
        new_username = entries["username"].get()
        new_password = entries["password"].get()
        b_y = entries["birth_year"].get()
        email = entries["email"].get()
        country_name = country_var.get()
        role = role_var.get()
        
        country_id = country_dict.get(country_name)
        
        if role == "User":
            role = 0
        else:
            role = 1

        insert_user(new_username, new_password, b_y, email, country_id, role)
        messagebox.showinfo("Account Created", "Your account has been successfully created!")
        account_window.destroy()

    account_window = ctk.CTk()
    account_window.title("Spotify - Create New Account")
    account_window.geometry("400x700")
    account_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(account_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_label = ctk.CTkLabel(frame, text="Create Your Spotify Account", font=("Helvetica", 20, "bold"), text_color=SPOTIFY_WHITE)
    title_label.pack(pady=20)

    fields = [("Username", "username"), ("Password", "password"), ("Birth Year", "birth_year"),
              ("Email", "email")]

    entries = {}
    for text, name in fields:
        label = ctk.CTkLabel(frame, text=text, text_color=SPOTIFY_WHITE)
        label.pack(pady=5)
        entry = ctk.CTkEntry(frame, width=300, placeholder_text=f"Enter your {text.lower()}")
        entry.pack(pady=5)
        entries[name] = entry

    country_dict = {
        "Australia": 4,
        "Brazil": 8,
        "France": 6,
        "Germany": 5,
        "Iran": 3,
        "Japan": 7,
        "United Kingdom": 2,
        "United States": 1
    }

    country_var = ctk.StringVar(value="United States")
    country_label = ctk.CTkLabel(frame, text="Country", text_color=SPOTIFY_WHITE)
    country_label.pack(pady=5)
    country_menu = ctk.CTkOptionMenu(frame, variable=country_var, values=list(country_dict.keys()))
    country_menu.pack(pady=5)

    role_var = ctk.StringVar(value="User")
    role_label = ctk.CTkLabel(frame, text="Role", text_color=SPOTIFY_WHITE)
    role_label.pack(pady=5)
    role_menu = ctk.CTkOptionMenu(frame, variable=role_var, values=["User", "Artist"])
    role_menu.pack(pady=5)

    create_account_button = ctk.CTkButton(frame, text="CREATE ACCOUNT", command=create_account, fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
    create_account_button.pack(pady=20)

    account_window.mainloop()

def main_login_window():
    def check_login():
        username = username_entry.get()
        password = password_entry.get()
        
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            query = """
            SELECT * FROM Users 
            WHERE username = ? AND password = ?
            """
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            cursor.execute("""
                            select IsArtist
                            from Users
                            where username = ?
                            """, username)
            role = cursor.fetchone()

            cursor.close()
            conn.close()
            if user:
                if role[0]: # Aartist
                    messagebox.showinfo("Login successful", f"Welcome {username}")
                    login_window.destroy()
                    open_artist_window(username)
                else: # User
                    messagebox.showinfo("Login successful", f"Welcome {username}")
                    login_window.destroy()
                    open_user_window(username)
            else:
                messagebox.showerror("Login failed", "Invalid username or password!")
        
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
            return False

    login_window = ctk.CTk()
    login_window.title("Spotify Login")
    login_window.geometry("400x500")
    login_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(login_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_label = ctk.CTkLabel(frame, text="Log in to Spotify", font=("Helvetica", 24, "bold"), text_color=SPOTIFY_WHITE)
    title_label.pack(pady=20)

    username_entry = ctk.CTkEntry(frame, width=300, placeholder_text="Username")
    username_entry.pack(pady=10)

    password_entry = ctk.CTkEntry(frame, width=300, show="*", placeholder_text="Password")
    password_entry.pack(pady=10)

    login_button = ctk.CTkButton(frame, text="LOG IN", command=check_login, fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
    login_button.pack(pady=20)

    create_account_button = ctk.CTkButton(frame, text="Don't have an account? Sign up", 
                                          command=create_user_account_window, fg_color="transparent", 
                                          text_color=SPOTIFY_GREEN, hover_color=SPOTIFY_GRAY)
    create_account_button.pack(pady=10)

    login_window.mainloop()

if __name__ == "__main__":
   main_login_window()


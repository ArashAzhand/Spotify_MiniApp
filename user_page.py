import tkinter as tk
from tkinter import ttk, messagebox
from user_database_interface import *

def edit_account(username):
    def update_account():
        new_username = new_username_entry.get()
        new_password = new_password_entry.get()
        b_y = new_BirthYear_entry.get()
        email = new_Email_entry.get()
        loc = new_Location_entry.get()

        update_user(new_username, new_password, b_y, email, loc)
        account_window.destroy()

    account_window = tk.Tk()
    account_window.title(f"{username} account")
    account_window.geometry("300x250")

    new_username_label = tk.Label(account_window, text="New Username")
    new_username_label.grid(row=1, column=0, pady=5)
    new_username_entry = tk.Entry(account_window)
    new_username_entry.grid(row=1, column=1, pady=5)
    new_username_entry.insert(0, username)

    new_password_label = tk.Label(account_window, text="New Password")
    new_password_label.grid(row=2, column=0, pady=5)
    new_password_entry = tk.Entry(account_window, show="*")
    new_password_entry.grid(row=2, column=1, pady=5)

    new_BirthYear_label = tk.Label(account_window, text="New BirthYear")
    new_BirthYear_label.grid(row=3, column=0, pady=5)
    new_BirthYear_entry = tk.Entry(account_window)
    new_BirthYear_entry.grid(row=3, column=1, pady=5)

    new_Email_label = tk.Label(account_window, text="New Email")
    new_Email_label.grid(row=4, column=0, pady=5)
    new_Email_entry = tk.Entry(account_window)
    new_Email_entry.grid(row=4, column=1, pady=5)

    new_Location_label = tk.Label(account_window, text="New Location")
    new_Location_label.grid(row=5, column=0, pady=5)
    new_Location_entry = tk.Entry(account_window)
    new_Location_entry.grid(row=5, column=1, pady=5)

    update_account_button = tk.Button(account_window, text="Update", command=update_account)
    update_account_button.grid(row=6,column=1,pady=20)

    account_window.mainloop()

def create_header(parent, username, return_to_login):
    header_frame = tk.Frame(parent, bg='black')
    header_frame.pack(fill=tk.X)

    user_info = tk.Label(header_frame, text=username, bg='black', fg='white', font=10)
    user_info.pack(side=tk.LEFT, padx=10)

    exit_btn = tk.Button(header_frame, text="EXIT", bg='green', command=return_to_login)
    exit_btn.pack(side=tk.RIGHT)

    edit_profile_btn = tk.Button(header_frame, text="Edit Profile", bg='green', command=lambda: edit_account(username))
    edit_profile_btn.pack(side=tk.RIGHT, padx=10)

    subscription_btn = tk.Button(header_frame, text="Subscribe", bg='green')
    subscription_btn.pack(side=tk.RIGHT)


def create_menu_bar(parent):
    menu_bar = tk.Menu(parent)

    home_menu = tk.Menu(menu_bar, tearoff=0)
    browse_menu = tk.Menu(menu_bar, tearoff=0)
    library_menu = tk.Menu(menu_bar, tearoff=0)
    friends_menu = tk.Menu(menu_bar, tearoff=0)
    wallet_menu = tk.Menu(menu_bar, tearoff=0)

    home_menu.add_command(label="Home")
    browse_menu.add_command(label="Browse")
    library_menu.add_command(label="Your Library")
    friends_menu.add_command(label="Friends")
    wallet_menu.add_command(label="Wallet")

    menu_bar.add_cascade(label="Home", menu=home_menu)
    menu_bar.add_cascade(label="Browse", menu=browse_menu)
    menu_bar.add_cascade(label="Your Library", menu=library_menu)
    menu_bar.add_cascade(label="Friends", menu=friends_menu)
    menu_bar.add_cascade(label="Wallet", menu=wallet_menu)

    parent.config(menu=menu_bar)

def create_playlists_tab(parent):
    tk.Label(parent, text="Playlists Content").pack()

def create_liked_songs_tab(parent):
    tk.Label(parent, text="Liked Songs Content").pack()

def create_recommended_tab(parent):
    tk.Label(parent, text="Recommended Content").pack()

def create_comments_tab(parent):
    tk.Label(parent, text="Comments Content").pack()

def create_tickets_tab(parent):
    tk.Label(parent, text="Concert Tickets Content").pack()

def create_main_content(parent):
    content_frame = tk.Frame(parent)
    content_frame.pack(fill=tk.BOTH, expand=True)

    tab_control = ttk.Notebook(content_frame)
    
    playlists_tab = ttk.Frame(tab_control)
    liked_songs_tab = ttk.Frame(tab_control)
    recommended_tab = ttk.Frame(tab_control)
    comments_tab = ttk.Frame(tab_control)
    tickets_tab = ttk.Frame(tab_control)

    tab_control.add(playlists_tab, text="Playlists")
    tab_control.add(liked_songs_tab, text="Liked Songs")
    tab_control.add(recommended_tab, text="Recommended")
    tab_control.add(comments_tab, text="Comments")
    tab_control.add(tickets_tab, text="Concert Tickets")
    tab_control.pack(fill=tk.BOTH, expand=True)

    create_playlists_tab(playlists_tab)
    create_liked_songs_tab(liked_songs_tab)
    create_recommended_tab(recommended_tab)
    create_comments_tab(comments_tab)
    create_tickets_tab(tickets_tab)

def create_user_page(root, username, return_to_login):
    create_header(root, username, return_to_login)
    create_menu_bar(root)
    create_main_content(root)

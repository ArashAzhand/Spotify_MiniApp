import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from user_database_interface import *
from artist_page import *


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

SPOTIFY_GREEN = "#1DB954"
SPOTIFY_BLACK = "#121212"
SPOTIFY_GRAY = "#212121"
SPOTIFY_WHITE = "#FFFFFF"
SPOTIFY_RED = "#FF0000"

def edit_account(username):
    def update_account():
        new_username = entries["username"].get()
        new_password = entries["password"].get()
        b_y = entries["birth_year"].get()
        email = entries["email"].get()
        country_name = country_var.get()
        country_id = country_dict.get(country_name)

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            select UserID from Users where UserName = ?
        """, (username))
        user_id = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        update_user(user_id, new_username, new_password, b_y, email, country_id)
        messagebox.showinfo("Account Updated", "Your account has been Updated succesfuly!")
        account_window.destroy()

    account_window = ctk.CTk()
    account_window.title(f"{username} account")
    account_window.geometry("400x700")
    account_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(account_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_label = ctk.CTkLabel(frame, text="Edit Your Account", font=("Helvetica", 20, "bold"), text_color=SPOTIFY_WHITE)
    title_label.pack(pady=20)

    fields = [("New Username", "username"), ("New Password", "password"), ("New Birth Year", "birth_year"),
              ("New Email", "email")]

    entries = {}
    for text, name in fields:
        label = ctk.CTkLabel(frame, text=text, text_color=SPOTIFY_WHITE)
        label.pack(pady=5)
        entry = ctk.CTkEntry(frame, width=300)
        entry.pack(pady=5)
        entries[name] = entry
        if name == "username":
            entry.insert(0, username)

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
    country_label = ctk.CTkLabel(frame, text="New Country", text_color=SPOTIFY_WHITE)
    country_label.pack(pady=5)
    country_menu = ctk.CTkOptionMenu(frame, variable=country_var, values=list(country_dict.keys()))
    country_menu.pack(pady=5)

    update_account_button = ctk.CTkButton(frame, text="Update Account", command=update_account, fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
    update_account_button.pack(pady=20)

    account_window.mainloop()

def delete_account(username, return_to_login):
    response = messagebox.askyesno("confirm delete", "Are you sure?")
    if response:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            select UserID from Users where UserName = ?
        """, (username))
        user_id = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        delete_user(user_id)
        messagebox.showinfo("Account deleted", "Your account has been deleted succesfuly!")
        return_to_login()

def charge_wallet(user_id, refresh_callback):
    def add_funds():
        try:
            amount = float(entry_amount.get())
            if amount <= 0:
                messagebox.showerror("Invalid Amount", "Please enter a valid amount greater than 0.")
                return
            
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("EXEC Deposit @UserID = ?, @Amount = ?", (user_id, amount))
            conn.commit()
            cursor.close()
            conn.close()
            
            messagebox.showinfo("Success", f"${amount} has been added to your wallet.")
            charge_window.destroy()
            refresh_callback()  
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a numeric value.")
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    charge_window = ctk.CTk()
    charge_window.title("Add Funds to Wallet")
    charge_window.geometry("400x200")
    charge_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(charge_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_label = ctk.CTkLabel(frame, text="Add Funds to Your Wallet", font=("Helvetica", 16, "bold"), text_color=SPOTIFY_WHITE)
    title_label.pack(pady=10)

    entry_amount = ctk.CTkEntry(frame, width=300, placeholder_text="Enter amount to add")
    entry_amount.pack(pady=5)

    add_button = ctk.CTkButton(frame, text="Add Funds", command=add_funds, fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
    add_button.pack(pady=10)

    charge_window.mainloop()


def check_subscribe(username, sub_status, refresh_header):
    def open_sub_window():
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM users WHERE UserName = ?", (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("SELECT Balance FROM Wallet WHERE UserID = ?", (user_id,))
        wallet_balance = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        if sub_status == "Premium":
            messagebox.showinfo("Subscription status", "You are already subscribed!")
        else:
            sub_window = ctk.CTk()
            sub_window.title("Subscribe to Premium")
            sub_window.geometry("400x300")
            sub_window.configure(fg_color=SPOTIFY_BLACK)

            frame = ctk.CTkFrame(sub_window, fg_color=SPOTIFY_GRAY)
            frame.pack(pady=20, padx=20, fill="both", expand=True)

            title_label = ctk.CTkLabel(frame, text="Subscribe to Premium", font=("Helvetica", 16, "bold"), text_color=SPOTIFY_WHITE)
            title_label.pack(pady=10)

            price_label = ctk.CTkLabel(frame, text="Subscription Price: $20", text_color=SPOTIFY_WHITE)
            price_label.pack(pady=5)

            balance_label = ctk.CTkLabel(frame, text=f"Your Wallet Balance: ${wallet_balance}", text_color=SPOTIFY_WHITE)
            balance_label.pack(pady=5)

            def confirm_subscription():
                nonlocal wallet_balance
                if wallet_balance < 20:
                    messagebox.showinfo("Insufficient Funds", "You do not have enough funds. Please add funds to your wallet.")
                    sub_window.destroy()
                    charge_wallet(user_id, open_sub_window)
                else:
                    conn = connect_to_db()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Users SET SubscriptionStatus = 'Premium' WHERE UserID = ?", (user_id,))
                    cursor.execute("EXEC Withdrawal @UserID = ?, @Amount = ?", (user_id, 20))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    messagebox.showinfo("Subscription Success", "You have been successfully subscribed to Premium.")
                    sub_window.destroy()
                    refresh_header()

            subscribe_button = ctk.CTkButton(frame, text="Subscribe", command=confirm_subscription, fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
            subscribe_button.pack(pady=10)

            sub_window.mainloop()

    open_sub_window()

        
def create_header(parent, username, return_to_login):
    def refresh_header():
        for widget in header_frame.winfo_children():
            widget.destroy()
        
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT SubscriptionStatus FROM users WHERE UserName = ?", (username,))
        sub_status = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        user_info = ctk.CTkLabel(header_frame, text=f"{username}\n({sub_status} Subscription)", text_color=SPOTIFY_WHITE, font=("Helvetica", 16, "bold"))
        user_info.pack(side="left", padx=10)

        exit_btn = ctk.CTkButton(header_frame, text="Exit Account", command=return_to_login, fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
        exit_btn.pack(side="right")

        edit_profile_btn = ctk.CTkButton(header_frame, text="Edit Profile", command=lambda: edit_account(username), fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
        edit_profile_btn.pack(side="right", padx=10)

        subscription_btn = ctk.CTkButton(header_frame, text="Subscribe", command=lambda: check_subscribe(username, sub_status, refresh_header), fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
        subscription_btn.pack(side="right")

        delete_account_btn = ctk.CTkButton(header_frame, text="Delete Account", command=lambda: delete_account(username, return_to_login), fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
        delete_account_btn.pack(side="right", padx=10)

    header_frame = ctk.CTkFrame(parent, fg_color=SPOTIFY_BLACK)
    header_frame.pack(fill="x", pady=10, padx=10)

    refresh_header()


#---------------------------------------------------------------

def search_in_terminal():
    s_type = int(input("search type (1- Song  2- Album): "))
    conn = connect_to_db()
    cursor = conn.cursor()
    if s_type == 1:
        print("please fill the parts you need to look for:")
        genre = input("genre: ")
        artist_name = input("artist name: ")
        song_name = input("song name: ")
        artist_country = input("artist country: ")
        ReleaseYear = input("release year: ")

        genre = genre if genre else 'None'
        artist_name = artist_name if artist_name else 'None'
        song_name = song_name if song_name else 'None'
        artist_country = artist_country if artist_country else 'None'
        ReleaseYear = int(ReleaseYear) if ReleaseYear else 'None'

        cursor.execute("EXEC SearchSongs ?, ?, ?, ?, ?", (genre, artist_name, song_name, artist_country, ReleaseYear))
        songs = cursor.fetchall()

        for song in songs:
            print(f"name: {song[1]} - genre: {song[2]} - artist name: {song[3]} - country: {song[4]} - release date: {song[5]}")
        print("\nsearch finished\n")
        search_in_terminal()

    elif s_type == 2:
        print("please fill the parts you need to look for:")
        genre = input("genre: ")
        artist_name = input("artist name: ")
        album_name = input("album name: ")
        country = input("country: ")
        ReleaseYear = input("release year: ")

        genre = genre if genre else 'None'
        artist_name = artist_name if artist_name else 'None'
        album_name = album_name if album_name else 'None'
        country = country if country else 'None'
        ReleaseYear = int(ReleaseYear) if ReleaseYear else 'None'

        cursor.execute("EXEC SearchAlbums ?, ?, ?, ?, ?", (genre, artist_name, album_name, country, ReleaseYear))
        albums = cursor.fetchall()

        for album in albums:
            print(f"Album name: {album[1]} - Artist name: {album[2]} - country: {album[3]} - release date: {album[4]}")
        print("\nsearch finished\n")
        search_in_terminal()
    else:
        print("wrong input try again!")
        search_in_terminal()

    cursor.close()
    conn.close()

    
    

def browse(username):
    search_window = ctk.CTk()
    search_window.title("Browse")
    search_window.geometry("500x600")

    search_frame = ctk.CTkFrame(search_window)
    search_frame.pack(pady=20, padx=20, fill="x")

    search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search...")
    search_entry.pack(side="left", expand=True, fill="x")

    search_type_var = ctk.StringVar(value="User")
    search_type_menu = ctk.CTkOptionMenu(search_frame, values=["User", "Artist", "Playlist"], variable=search_type_var)
    search_type_menu.pack(side="left", padx=(10, 0))

    search_button = ctk.CTkButton(search_frame, text="Search", command=lambda: search())
    search_button.pack(pady=(10, 0))

    terminal_input_button = ctk.CTkButton(search_frame, text="search in terminal", command=search_in_terminal)
    terminal_input_button.pack(side="left", pady=(10, 0), padx=(10, 0))

    results_frame = ctk.CTkFrame(search_window)
    results_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def search():
        query = search_entry.get()
        search_type = search_type_var.get()
        
        for widget in results_frame.winfo_children():
            widget.destroy()

        if search_type in ["User", "Artist"]:
            result = search_user_or_artist(query, search_type)
            if result:
                show_user_or_artist(result, username)
            else:
                show_error(f"No {search_type} found.")
        elif search_type == "Playlist":
            result = search_playlist(query)
            if result:
                if result['is_private'] == 0:
                    show_playlist(result)
                else:
                    if is_friend(username, result['creator_id']):
                        show_playlist(result)
                    else:
                        show_error("You must be friends with the playlist creator to view this playlist.")
            else:
                show_error("No playlist found.")

    def search_user_or_artist(query, search_type):
        conn = connect_to_db()
        cursor = conn.cursor()
        
        if search_type == "User":
            cursor.execute("""
                SELECT UserID, UserName, Email, IsArtist 
                FROM Users 
                WHERE UserName = ?
            """, (query,))
        else:  # Artist
            cursor.execute("""
                SELECT Users.UserID, Users.UserName, Users.Email, Artists.ArtistName
                FROM Users
                JOIN Artists ON Users.UserID = Artists.ArtistID
                WHERE Artists.ArtistName = ?
            """, (query,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def search_playlist(query):
        conn = connect_to_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.PlaylistID, p.PlaylistName, p.UserID, p.IsPrivate, u.UserName
            FROM Playlists p
            JOIN Users u ON p.UserID = u.UserID
            WHERE p.PlaylistName LIKE ?
        """, (query,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'creator_id': result[2],
                'is_private': bool(result[3]),
                'creator_name': result[4]
            }
        return None

    def is_friend(username, user2):
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("select UserID from Users where UserName = ?", username)
        user1 = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) 
            FROM Friends 
            WHERE ((UserID = ? AND FriendID = ?) OR (UserID = ? AND FriendID = ?))
            AND Status = 'Accepted'
        """, (user1, user2, user2, user1))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result[0] > 0

    def show_user_or_artist(result, current_user):
        user_frame = ctk.CTkFrame(results_frame)
        user_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(user_frame, text=f"Name: {result[1]}").pack(anchor="w")
        ctk.CTkLabel(user_frame, text=f"Email: {result[2]}").pack(anchor="w")
        
        if result[3]:  # IsArtist
            ctk.CTkLabel(user_frame, text="Artist").pack(anchor="w")

        follow_button = ctk.CTkButton(user_frame, text="Follow", command=lambda: follow_user(current_user, result[0]))
        follow_button.pack(pady=(10, 0))

        user_frame.bind("<Button-1>", lambda e: show_user_details(result[0]))

    def show_playlist(result):
        playlist_frame = ctk.CTkFrame(results_frame)
        playlist_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(playlist_frame, text=f"Playlist: {result['name']}").pack(anchor="w")
        ctk.CTkLabel(playlist_frame, text=f"Created by: {result['creator_name']}").pack(anchor="w")
        
        playlist_frame.bind("<Button-1>", lambda e: show_playlist_details(result['id']))

    def show_error(message):
        error_label = ctk.CTkLabel(results_frame, text=message, text_color="red")
        error_label.pack(pady=20)

    def follow_user(curr_username, followed_id):
        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("select UserID from Users where username = ?", (curr_username))
        follower_id = cursor.fetchone()[0]
        
        cursor.execute("EXEC Follow ?, ?", (follower_id, followed_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        messagebox.showinfo("Follow", f"You are now following user {followed_id}")

    def show_user_details(user_id):
        details_window = ctk.CTk()
        details_window.title(f"User Details - {user_id}")
        details_window.geometry("400x300")

        conn = connect_to_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT Users.UserID, Users.UserName, Users.Email, Users.BirthYear, 
                Users.SubscriptionStatus, Users.IsArtist, Country.CountryName,
                CASE WHEN Artists.ArtistID IS NOT NULL THEN Artists.ArtistName ELSE NULL END AS ArtistName
            FROM Users
            LEFT JOIN Country ON Users.CountryID = Country.CountryID
            LEFT JOIN Artists ON Users.UserID = Artists.ArtistID
            WHERE Users.UserID = ?
        """, (user_id,))
        
        user_info = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_info:
            info_frame = ctk.CTkFrame(details_window)
            info_frame.pack(pady=20, padx=20, fill="both", expand=True)

            labels = [
                f"User ID: {user_info[0]}",
                f"Username: {user_info[1]}",
                f"Email: {user_info[2]}",
                f"Birth Year: {user_info[3] or 'Not provided'}",
                f"Subscription: {user_info[4]}",
                f"Country: {user_info[6] or 'Not provided'}",
                f"Is Artist: {'Yes' if user_info[5] else 'No'}",
                f"Artist Name: {user_info[7] or 'N/A'}" if user_info[5] else None
            ]

            for label in labels:
                if label:
                    ctk.CTkLabel(info_frame, text=label).pack(anchor="w", pady=5)

        else:
            ctk.CTkLabel(details_window, text="User not found.").pack(pady=20)

        details_window.mainloop()

    def show_playlist_details(playlist_id):
        details_window = ctk.CTkToplevel()
        details_window.title(f"Playlist Details - {playlist_id}")
        details_window.geometry("400x600")

        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.Title, u.UserName
            FROM PlaylistSongs ps
            JOIN Songs s ON ps.SongID = s.SongID
            JOIN Users u ON s.ArtistID = u.UserID
            WHERE ps.PlaylistID = ?
        """, (playlist_id,))
        songs = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) 
            FROM PlaylistLikes 
            WHERE PlaylistID = ?
        """, (playlist_id,))
        likes_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        ctk.CTkLabel(details_window, text=f"Likes: {likes_count}").pack(pady=(10, 20))

        songs_frame = ctk.CTkFrame(details_window)
        songs_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(songs_frame, text="Songs:").pack(anchor="w")
        
        for song in songs:
            song_frame = ctk.CTkFrame(songs_frame)
            song_frame.pack(pady=5, padx=10, fill="x")
            ctk.CTkLabel(song_frame, text=f"Title: {song[0]}").pack(anchor="w")
            ctk.CTkLabel(song_frame, text=f"Artist: {song[1]}").pack(anchor="w")

    search_window.mainloop()

#--------------------------------------------------------------------------

def open_message_window(user_id, friend_id, friend_username, friend_window_destroy):
    def send_message():
        message_content = message_entry.get("1.0", "end-1c")
        if not message_content:
            messagebox.showerror("Error", "Please enter a message.")
            return

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Messages (SenderID, ReceiverID, MessageContent) VALUES (?, ?, ?)",
                       (user_id, friend_id, message_content))
        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Success", f"Message sent to {friend_username}")
        message_entry.delete("1.0", "end")
        refresh_messages()

    def refresh_messages():
        messages_text.configure(state="normal")
        messages_text.delete("1.0", "end")
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SenderID, MessageContent, SendTime 
            FROM Messages 
            WHERE (SenderID = ? AND ReceiverID = ?) OR (SenderID = ? AND ReceiverID = ?)
            ORDER BY SendTime DESC
        """, (user_id, friend_id, friend_id, user_id))
        messages = cursor.fetchall()
        cursor.close()
        conn.close()

        for msg in messages:
            sender = "You" if msg[0] == user_id else friend_username
            messages_text.insert("1.0", f"{sender} ({msg[2]}): {msg[1]}\n\n")
        messages_text.configure(state="disabled")

    friend_window_destroy()
    message_window = ctk.CTk()
    message_window.title(f"Chat with {friend_username}")
    message_window.geometry("400x700")
    message_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(message_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_label = ctk.CTkLabel(frame, text=f"Chat with {friend_username}", font=("Helvetica", 16, "bold"), text_color=SPOTIFY_WHITE)
    title_label.pack(pady=10)

    messages_text = ctk.CTkTextbox(frame, width=350, height=300, state="disabled")
    messages_text.pack(pady=10, padx=10, fill="both", expand=True)

    message_entry = ctk.CTkTextbox(frame, width=350, height=100)
    message_entry.pack(pady=10)

    send_button = ctk.CTkButton(frame, text="Send", command=send_message, fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
    send_button.pack(pady=10)

    refresh_messages()

    message_window.mainloop()

def friends(username):
    def add_friend():
        def submit_friend_request():
            friend_username = entry_username.get()
            if not friend_username:
                messagebox.showerror("Error", "Please enter a username.")
                return

            conn = connect_to_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT UserID FROM users WHERE UserName = ?", (friend_username,))
            friend_row = cursor.fetchone()
            if not friend_row:
                messagebox.showerror("Error", "Username does not exist.")
                cursor.close()
                conn.close()
                return

            friend_id = friend_row[0]

            cursor.execute("SELECT * FROM Friends WHERE (UserID = ? AND FriendID = ? AND Status != 'Rejected')", (user_id, friend_id))
            if cursor.fetchone():
                messagebox.showerror("Error", "Friend request already sent or you are already friends.")
                cursor.close()
                conn.close()
                return

            cursor.execute("EXEC AddFriendRequest ?, ?", (user_id, friend_id))

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", f"Friend request sent to {friend_username}")
            add_friend_window.destroy()
            refresh_friends_list()

        add_friend_window = ctk.CTk()
        add_friend_window.title("Add Friend")
        add_friend_window.geometry("300x200")
        add_friend_window.configure(fg_color=SPOTIFY_BLACK)

        frame = ctk.CTkFrame(add_friend_window, fg_color=SPOTIFY_GRAY)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        title_label = ctk.CTkLabel(frame, text="Add Friend", font=("Helvetica", 16, "bold"), text_color=SPOTIFY_WHITE)
        title_label.pack(pady=10)

        entry_username = ctk.CTkEntry(frame, width=250, placeholder_text="Enter friend's username")
        entry_username.pack(pady=5)

        submit_button = ctk.CTkButton(frame, text="Send Request", command=submit_friend_request, fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
        submit_button.pack(pady=10)

        add_friend_window.mainloop()

    def refresh_friends_list():
        for widget in friends_requests_frame.winfo_children():
            widget.destroy()
        for widget in confirmed_friends_frame.winfo_children():
            widget.destroy()
        for widget in rejected_friends_frame.winfo_children():
            widget.destroy()

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Status FROM Friends WHERE FriendID = ?", (user_id,))
        friends = cursor.fetchall()
        
        friend_requests = [f for f in friends if f[1] == 'Pending']

        cursor.execute("""SELECT UserID, Status FROM Friends WHERE FriendID = ? 
                       UNION 
                       SELECT FriendID, Status FROM Friends WHERE UserID = ? 
                       """, (user_id, user_id))
        both_friends = cursor.fetchall()
        confirmed_friends = [f for f in both_friends if f[1] == 'Accepted']
        rejected_friends = [f for f in both_friends if f[1] == 'Rejected']

        if friend_requests:
            friend_requests_label = ctk.CTkLabel(friends_requests_frame, text="Friend Requests:", text_color=SPOTIFY_WHITE, font=("Helvetica", 14, "bold"))
            friend_requests_label.pack(pady=5)
            for request in friend_requests:
                cursor.execute("SELECT UserName FROM users WHERE UserID = ?", (request[0],))
                request_username = cursor.fetchone()[0]
                request_frame = ctk.CTkFrame(friends_requests_frame, fg_color=SPOTIFY_GRAY)
                request_frame.pack(pady=5, padx=10, fill="x")

                request_label = ctk.CTkLabel(request_frame, text=request_username, text_color=SPOTIFY_WHITE)
                request_label.pack(side="left", padx=10)

                accept_button = ctk.CTkButton(request_frame, text="Accept", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                              command=lambda friend_id=request[0]: respond_to_friend_request(user_id, friend_id, 'Accepted'))
                accept_button.pack(side="right", padx=5)

                reject_button = ctk.CTkButton(request_frame, text="Reject", fg_color="#ff5555", hover_color="#ff7b7b",
                                              command=lambda friend_id=request[0]: respond_to_friend_request(user_id, friend_id, 'Rejected'))
                reject_button.pack(side="right", padx=5)

        if confirmed_friends:
            confirmed_friends_label = ctk.CTkLabel(confirmed_friends_frame, text="Friends:", text_color=SPOTIFY_WHITE, font=("Helvetica", 14, "bold"))
            confirmed_friends_label.pack(pady=5)
            for friend in confirmed_friends:
                cursor.execute("SELECT UserName FROM users WHERE UserID = ?", (friend[0],))
                friend_username = cursor.fetchone()[0]
                friend_frame = ctk.CTkFrame(confirmed_friends_frame, fg_color=SPOTIFY_GRAY)
                friend_frame.pack(pady=5, padx=10, fill="x")

                friend_label = ctk.CTkLabel(friend_frame, text=friend_username, text_color=SPOTIFY_WHITE)
                friend_label.pack(side="left", padx=10)

                message_button = ctk.CTkButton(friend_frame, text="Message", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                               command=lambda uid=user_id, fid=friend[0], fname=friend_username: open_message_window(uid, fid, fname, friend_window_destroy))
                message_button.pack(side="right", padx=5)

        if rejected_friends:
            rejected_friends_label = ctk.CTkLabel(rejected_friends_frame, text="Rejected Requests:", text_color=SPOTIFY_WHITE, font=("Helvetica", 14, "bold"))
            rejected_friends_label.pack(pady=5)
            for friend in rejected_friends:
                cursor.execute("SELECT UserName FROM users WHERE UserID = ?", (friend[0],))
                friend_username = cursor.fetchone()[0]
                friend_label = ctk.CTkLabel(rejected_friends_frame, text=friend_username, text_color=SPOTIFY_WHITE)
                friend_label.pack(pady=5, padx=10)

        cursor.close()
        conn.close()

    def respond_to_friend_request(user_id, friend_id, response):
        conn = connect_to_db()
        cursor = conn.cursor()
        if response == 'Accepted':
            cursor.execute("EXEC AcceptFriendRequest ?, ?", (friend_id, user_id))
        else:
            cursor.execute("UPDATE Friends SET Status = 'Rejected' WHERE UserID = ? AND FriendID = ?", (user_id, friend_id))
            cursor.execute("UPDATE Friends SET Status = 'Rejected' WHERE UserID = ? AND FriendID = ?", (friend_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        refresh_friends_list()

    def friend_window_destroy():
        friends_window.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID FROM users WHERE UserName = ?", (username,))
    user_id = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    friends_window = ctk.CTk()
    friends_window.title("Friends")
    friends_window.geometry("400x600")
    friends_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(friends_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_label = ctk.CTkLabel(frame, text="Your Friends", font=("Helvetica", 16, "bold"), text_color=SPOTIFY_WHITE)
    title_label.pack(pady=10)

    add_friend_button = ctk.CTkButton(frame, text="Add Friend", command=add_friend, fg_color=SPOTIFY_GREEN, hover_color="#1ED760")
    add_friend_button.pack(pady=10)

    friends_requests_frame = ctk.CTkFrame(frame, fg_color=SPOTIFY_BLACK)
    friends_requests_frame.pack(pady=10, padx=10, fill="both", expand=True)

    confirmed_friends_frame = ctk.CTkFrame(frame, fg_color=SPOTIFY_BLACK)
    confirmed_friends_frame.pack(pady=10, padx=10, fill="both", expand=True)

    rejected_friends_frame = ctk.CTkFrame(frame, fg_color=SPOTIFY_BLACK)
    rejected_friends_frame.pack(pady=10, padx=10, fill="both", expand=True)

    refresh_friends_list()

    friends_window.mainloop()


def wallet(username):
    def refresh_wallet():
        wallet_window.destroy()
        wallet(username)

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID FROM users WHERE UserName = ?", (username,))
    user_id = cursor.fetchone()[0]

    cursor.execute("SELECT Balance FROM Wallet WHERE UserID = ?", (user_id,))
    wallet_balance = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    wallet_window = ctk.CTk()
    wallet_window.title("Wallet")
    wallet_window.geometry("300x200")
    wallet_window.configure(fg_color="#191414")

    frame = ctk.CTkFrame(wallet_window, fg_color="#191414")
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    balance_label = ctk.CTkLabel(
        frame, 
        text=f"Current Balance: ${wallet_balance:.2f}", 
        font=("Helvetica", 16),
        text_color="white"
    )
    balance_label.pack(pady=10)

    add_funds_button = ctk.CTkButton(
        frame, 
        text="Deposit", 
        command=lambda: charge_wallet(user_id, refresh_wallet),
        fg_color="#1DB954",
        hover_color="#1ED760",
        text_color="white"
    )
    add_funds_button.pack(pady=10)

    wallet_window.mainloop()

#---------------------------------------------------------------
def artist_option(username): 
    artist_window = ctk.CTkToplevel()
    artist_window.title("Artist Options")
    artist_window.geometry("400x300")
    artist_window.configure(fg_color=SPOTIFY_BLACK)

    artist_frame = ctk.CTkFrame(artist_window, fg_color=SPOTIFY_GRAY)
    artist_frame.pack(pady=20, padx=20, fill="both", expand=True)

    ctk.CTkLabel(artist_frame, text="Artist Options", font=("Helvetica", 16, "bold"), text_color=SPOTIFY_WHITE).pack(pady=10)

    artist_buttons = {
        "song_handling": song_handling,
        "album_handling": album_handling,
        "concert_handling": concert_handling
    }

    for button_text, button_command in artist_buttons.items():
        ctk.CTkButton(
            artist_frame,
            text=button_text,
            fg_color=SPOTIFY_GREEN,
            text_color=SPOTIFY_WHITE,
            hover_color="#1ED760",
            command=lambda cmd=button_command: cmd(username)
        ).pack(pady=5)

def create_menu_bar(parent, username, reset_user_page, is_artist):
    def home(dd):
        reset_user_page()

    def command_wrapper(func):
        return lambda: func(username)

    menu_frame = ctk.CTkFrame(parent, fg_color=SPOTIFY_GRAY)
    menu_frame.pack(fill="x", pady=10, padx=10)

    buttons = {
        "Home": home,
        "Browse": browse,      
        "Friends": friends,
        "Wallet": wallet
    }

    if is_artist:
        buttons["Artist Options"] = artist_option

    for button_text, button_command in buttons.items():
        ctk.CTkButton(
            menu_frame,
            text=button_text,
            fg_color="transparent",
            text_color=SPOTIFY_WHITE,
            hover_color=SPOTIFY_GREEN,
            command=command_wrapper(button_command)
        ).pack(side="left", padx=5)




#-----------------------------------------------------------



def show_song_list(sub_status, frame, user_id):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Songs.SongID, Songs.Title, Genre.GenreName, Users.UserName
        FROM Songs
        LEFT JOIN Genre ON Songs.GenreID = Genre.GenreID
        LEFT JOIN Users ON Songs.ArtistID = Users.UserID
    """)
    songs = cursor.fetchall()
    cursor.close()
    conn.close()

    canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_BLACK)
    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color=SPOTIFY_BLACK)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    i = 0
    for song in songs:
        i += 1
        song_frame = ctk.CTkFrame(scrollable_frame, fg_color=SPOTIFY_GRAY)
        song_frame.pack(fill="x", pady=5)

        song_label = ctk.CTkLabel(song_frame, text=f"{i}: {song[1]} - {song[2]} - {song[3]}", text_color=SPOTIFY_WHITE)
        song_label.pack(side="left", padx=10)
        
        song_label.bind("<Button-1>", lambda event, song_id=song[0]: show_song_lyrics(song_id, frame))

        if sub_status == "Premium":
            like_button = ctk.CTkButton(song_frame, text="Like", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                        command=lambda song_id=song[0]: like_song(song_id, user_id))
            like_button.pack(side="right", padx=5)

            comment_button = ctk.CTkButton(song_frame, text="Comment", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                           command=lambda song_id=song[0]: comment_song(song_id, user_id))
            comment_button.pack(side="right", padx=5)

def show_song_lyrics(song_id, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT Title, Lyrics FROM Songs WHERE SongID = ?", (song_id,))
    song = cursor.fetchone()

    title_label = ctk.CTkLabel(frame, text=song[0], text_color=SPOTIFY_WHITE, font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)

    lyrics_label = ctk.CTkLabel(frame, text=song[1], text_color=SPOTIFY_WHITE, wraplength=380, justify="left")
    lyrics_label.pack(pady=10)

    cursor.execute("""
        SELECT Users.UserName
        FROM SongLikes
        JOIN Users ON SongLikes.UserID = Users.UserID
        WHERE SongLikes.SongID = ?
    """, (song_id,))
    liked_users = cursor.fetchall()

    if liked_users:
        liked_users_label = ctk.CTkLabel(frame, text="Liked by: " + ", ".join(user[0] for user in liked_users),
                                         text_color=SPOTIFY_WHITE)
        liked_users_label.pack(pady=5)

    cursor.execute("""
        SELECT Users.UserName, SongComments.CommentText
        FROM SongComments
        JOIN Users ON SongComments.UserID = Users.UserID
        WHERE SongComments.SongID = ?
    """, (song_id,))
    comments = cursor.fetchall()

    if comments:
        comments_label = ctk.CTkLabel(frame, text="Comments:", text_color=SPOTIFY_WHITE, font=("Helvetica", 12, "bold"))
        comments_label.pack(pady=5)

        for comment in comments:
            comment_text = f"{comment[0]}: {comment[1]}"
            comment_label = ctk.CTkLabel(frame, text=comment_text, text_color=SPOTIFY_WHITE, wraplength=380, justify="left")
            comment_label.pack(pady=5)

    cursor.close()
    conn.close()


def like_song(song_id, user_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM SongLikes WHERE UserID = ? AND SongID = ?", (user_id, song_id))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "You have already liked this song.")
            cursor.close()
            conn.close()
            return
        
        cursor.execute("EXEC LikeSong @UserID = ?, @SongID = ?", (user_id, song_id))
        conn.commit()
        messagebox.showinfo("Success", "Song liked successfully!")

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")

    finally:
        cursor.close()
        conn.close()

def comment_song(song_id, user_id):
    comment_window = ctk.CTkToplevel()
    comment_window.title("Add Comment")
    comment_window.geometry("300x200")
    comment_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(comment_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    comment_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter your comment")
    comment_entry.pack(pady=10)

    submit_button = ctk.CTkButton(frame, text="Submit", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                  command=lambda: submit_comment(song_id, comment_entry.get(), user_id, comment_window))
    submit_button.pack(pady=10)

def submit_comment(song_id, comment_text, user_id, comment_window):
    if not comment_text:
        messagebox.showerror("Error", "Please enter a comment.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC CommentOnSong @UserID = ?, @SongID = ?, @CommentText = ?", (user_id, song_id, comment_text))
        conn.commit()
        messagebox.showinfo("Success", "Comment added successfully!")
        comment_window.destroy()  
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

#----------------------------------------------------------------
def show_albums(sub_status, frame, user_id):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AlbumID, Title, ReleaseDate, ArtistID
        FROM Albums
    """)
    albums = cursor.fetchall()

    cursor.close()
    conn.close()

    for album in albums:
        album_id = album[0]
        title = album[1]
        release_date = album[2]

        album_frame = ctk.CTkFrame(frame, fg_color="gray")
        album_frame.pack(fill="x", pady=5)

        album_label = ctk.CTkLabel(album_frame, text=f"{title} (Released: {release_date})", text_color="white")
        album_label.pack(side="left", padx=10)

        like_button = ctk.CTkButton(album_frame, text="Like", command=lambda a_id=album_id: like_album(user_id, a_id))
        like_button.pack(side="right", padx=5)

        comment_button = ctk.CTkButton(album_frame, text="Comment", command=lambda a_id=album_id: comment_album(user_id, a_id))
        comment_button.pack(side="right", padx=5)

        album_label.bind("<Button-1>", lambda event, a_id=album_id: show_album_details(a_id, frame, user_id))

def like_album(user_id, album_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO AlbumLikes (UserID, AlbumID) VALUES (?, ?)", (user_id, album_id))
        conn.commit()
        messagebox.showinfo("Success", "Album liked successfully!")
    except pyodbc.IntegrityError:
        messagebox.showinfo("Info", "You have already liked this album.")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def comment_album(user_id, album_id):
    def submit_comment():
        comment_text = comment_entry.get("1.0", "end-1c").strip()
        if not comment_text:
            messagebox.showerror("Error", "Comment cannot be empty.")
            return
        
        conn = connect_to_db()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO AlbumComments (UserID, AlbumID, CommentText) VALUES (?, ?, ?)", (user_id, album_id, comment_text))
            conn.commit()
            messagebox.showinfo("Success", "Comment added successfully!")
            comment_window.destroy()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            cursor.close()
            conn.close()

    comment_window = ctk.CTkToplevel()
    comment_window.title("Add Comment")
    comment_window.geometry("400x300")

    comment_label = ctk.CTkLabel(comment_window, text="Enter your comment:")
    comment_label.pack(pady=10)

    comment_entry = ctk.CTkTextbox(comment_window, width=350, height=150)
    comment_entry.pack(pady=10)

    submit_button = ctk.CTkButton(comment_window, text="Submit", command=submit_comment)
    submit_button.pack(pady=10)

def show_album_details(album_id, frame, user_id):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.SongID, s.Title
        FROM Songs s
        JOIN AlbumSongs a ON s.SongID = a.SongID
        WHERE a.AlbumID = ?
    """, (album_id,))
    songs = cursor.fetchall()

    cursor.execute("""
        SELECT u.UserName, c.CommentText, c.CommentDate
        FROM AlbumComments c
        JOIN Users u ON c.UserID = u.UserID
        WHERE c.AlbumID = ?
    """, (album_id,))
    comments = cursor.fetchall()

    cursor.execute("""
        SELECT u.UserName
        FROM AlbumLikes l
        JOIN Users u ON l.UserID = u.UserID
        WHERE l.AlbumID = ?
    """, (album_id,))
    likes = cursor.fetchall()

    cursor.close()
    conn.close()

    songs_label = ctk.CTkLabel(frame, text="Songs in this album:", text_color="white")
    songs_label.pack(pady=10)

    for song in songs:
        song_label = ctk.CTkLabel(frame, text=song[1], text_color="white")
        song_label.pack(pady=2)

    comments_label = ctk.CTkLabel(frame, text="Comments:", text_color="white")
    comments_label.pack(pady=10)

    for comment in comments:
        comment_text = f"{comment[0]} ({comment[2]}): {comment[1]}"
        comment_label = ctk.CTkLabel(frame, text=comment_text, text_color="white")
        comment_label.pack(pady=2)

    likes_label = ctk.CTkLabel(frame, text="Liked by:", text_color="white")
    likes_label.pack(pady=10)

    for like in likes:
        like_label = ctk.CTkLabel(frame, text=like[0], text_color="white")
        like_label.pack(pady=2)
#----------------------------------------------------------------

def create_playlist(user_id, playlist_name, is_private):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Playlists (UserID, PlaylistName, IsPrivate) VALUES (?, ?, ?)",
                       (user_id, playlist_name, is_private))
        conn.commit()
        messagebox.showinfo("Success", "Playlist created successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def delete_playlist(playlist_id, user_id, container):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC DeletePlaylist ?", (playlist_id,))

        conn.commit()
        messagebox.showinfo("Success", "Playlist deleted successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    refresh_playlists(user_id, container)

def like_playlist(user_id, playlist_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO PlaylistLikes (UserID, PlaylistID) VALUES (?, ?)", (user_id, playlist_id))
        conn.commit()
        messagebox.showinfo("Success", "Playlist liked successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def comment_playlist(user_id, playlist_id, comment_text):
    if not comment_text:
        messagebox.showerror("Error", "Please enter a comment.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO PlaylistComments (UserID, PlaylistID, CommentText) VALUES (?, ?, ?)",
                       (user_id, playlist_id, comment_text))
        conn.commit()
        messagebox.showinfo("Success", "Comment added successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def create_playlist_window(user_id, container):
    def submit_playlist():
        playlist_name = name_entry.get()
        is_private = private_var.get()
        if not playlist_name:
            messagebox.showerror("Error", "Please enter a playlist name.")
            return
        create_playlist(user_id, playlist_name, is_private)
        playlist_window.destroy()
        refresh_playlists(user_id, container)

    playlist_window = ctk.CTkToplevel()
    playlist_window.title("Create Playlist")
    playlist_window.geometry("300x200")
    playlist_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(playlist_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    name_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter playlist name")
    name_entry.pack(pady=10)

    private_var = ctk.IntVar()
    private_checkbox = ctk.CTkCheckBox(frame, text="Private", variable=private_var)
    private_checkbox.pack(pady=10)

    submit_button = ctk.CTkButton(frame, text="Create", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                  command=submit_playlist)
    submit_button.pack(pady=10)

def show_playlist_songs_window(playlist_id, user_id):
    playlist_songs_window = ctk.CTkToplevel()
    playlist_songs_window.title("Manage Playlist Songs")
    playlist_songs_window.geometry("450x700")
    playlist_songs_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(playlist_songs_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    existing_songs_label = ctk.CTkLabel(frame, text="Songs in Playlist", text_color=SPOTIFY_WHITE)
    existing_songs_label.pack(pady=10)

    existing_songs_frame = ctk.CTkFrame(frame, fg_color=SPOTIFY_BLACK)
    existing_songs_frame.pack(fill="both", expand=True)

    canvas_existing = ctk.CTkCanvas(existing_songs_frame, bg=SPOTIFY_BLACK)
    scrollbar_existing = ctk.CTkScrollbar(existing_songs_frame, orientation="vertical", command=canvas_existing.yview)
    scrollable_frame_existing = ctk.CTkFrame(canvas_existing, fg_color=SPOTIFY_GRAY)

    scrollable_frame_existing.bind(
        "<Configure>",
        lambda e: canvas_existing.configure(
            scrollregion=canvas_existing.bbox("all")
        )
    )

    canvas_existing.create_window((0, 0), window=scrollable_frame_existing, anchor="nw")
    canvas_existing.configure(yscrollcommand=scrollbar_existing.set)

    canvas_existing.pack(side="left", fill="both", expand=True)
    scrollbar_existing.pack(side="right", fill="y")

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.SongID, s.Title 
        FROM Songs s 
        JOIN PlaylistSongs ps ON s.SongID = ps.SongID 
        WHERE ps.PlaylistID = ?
    """, (playlist_id,))
    existing_songs = cursor.fetchall()

    for song in existing_songs:
        song_label = ctk.CTkLabel(scrollable_frame_existing, text=song[1], text_color=SPOTIFY_WHITE)
        song_label.pack(anchor="w", pady=5)

    add_songs_label = ctk.CTkLabel(frame, text="Add Songs to Playlist", text_color=SPOTIFY_WHITE)
    add_songs_label.pack(pady=10)

    add_songs_frame = ctk.CTkFrame(frame, fg_color=SPOTIFY_BLACK)
    add_songs_frame.pack(fill="both", expand=True)

    canvas_add = ctk.CTkCanvas(add_songs_frame, bg=SPOTIFY_BLACK)
    scrollbar_add = ctk.CTkScrollbar(add_songs_frame, orientation="vertical", command=canvas_add.yview)
    scrollable_frame_add = ctk.CTkFrame(canvas_add, fg_color=SPOTIFY_GRAY)

    scrollable_frame_add.bind(
        "<Configure>",
        lambda e: canvas_add.configure(
            scrollregion=canvas_add.bbox("all")
        )
    )

    canvas_add.create_window((0, 0), window=scrollable_frame_add, anchor="nw")
    canvas_add.configure(yscrollcommand=scrollbar_add.set)

    canvas_add.pack(side="left", fill="both", expand=True)
    scrollbar_add.pack(side="right", fill="y")

    cursor.execute("SELECT SongID, Title FROM Songs WHERE CanAddToPlaylist = 1")
    all_songs = cursor.fetchall()
    cursor.close()
    conn.close()

    song_vars = {}
    for song in all_songs:
        song_id, song_title = song
        if song_id not in [s[0] for s in existing_songs]:  
            var = ctk.IntVar()
            song_vars[song_id] = var
            ctk.CTkCheckBox(scrollable_frame_add, text=song_title, variable=var, fg_color=SPOTIFY_GREEN).pack(anchor="w", pady=5)

    def add_songs_to_playlist():
        selected_song_ids = [song_id for song_id, var in song_vars.items() if var.get() == 1]
        if selected_song_ids:
            conn = connect_to_db()
            cursor = conn.cursor()
            try:
                for song_id in selected_song_ids:
                    cursor.execute("INSERT INTO PlaylistSongs (PlaylistID, SongID) VALUES (?, ?)", (playlist_id, song_id))
                conn.commit()
                messagebox.showinfo("Success", "Songs added to playlist successfully!")
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                cursor.close()
                conn.close()
            playlist_songs_window.destroy()
        else:
            messagebox.showerror("Error", "Please select at least one song.")

    add_button = ctk.CTkButton(frame, text="Add to Playlist", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                               command=add_songs_to_playlist)
    add_button.pack(pady=10)

def refresh_playlists(user_id, container):
    for widget in container.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT PlaylistID, PlaylistName FROM Playlists WHERE UserID = ?", (user_id,))
    playlists = cursor.fetchall()
    cursor.close()
    conn.close()

    for playlist in playlists:
        playlist_id, playlist_name = playlist

        playlist_item = ctk.CTkFrame(container, fg_color=SPOTIFY_BLACK)
        playlist_item.pack(fill="x", pady=5, padx=10)

        playlist_label = ctk.CTkLabel(playlist_item, text=playlist_name, text_color=SPOTIFY_WHITE)
        playlist_label.pack(side="left", padx=10)
        
        playlist_label.bind("<Button-1>", lambda event, pid=playlist_id: show_playlist_songs_window(pid, user_id))

        like_button = ctk.CTkButton(playlist_item, text="Like", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                    command=lambda pid=playlist_id: like_playlist(user_id, pid))
        like_button.pack(side="left", padx=5)

        comment_button = ctk.CTkButton(playlist_item, text="Comment", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                       command=lambda pid=playlist_id: comment_playlist_window(user_id, pid))
        comment_button.pack(side="left", padx=5)

        delete_button = ctk.CTkButton(playlist_item, text="Delete", fg_color=SPOTIFY_RED, hover_color="#FF0000",
                                      command=lambda pid=playlist_id: delete_playlist(pid, user_id, container))
        delete_button.pack(side="left", padx=5)

def comment_playlist_window(user_id, playlist_id):
    def submit_comment():
        comment_text = comment_entry.get()
        comment_playlist(user_id, playlist_id, comment_text)
        comment_window.destroy()

    comment_window = ctk.CTkToplevel()
    comment_window.title("Add Comment")
    comment_window.geometry("300x200")
    comment_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(comment_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    comment_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter your comment")
    comment_entry.pack(pady=10)

    submit_button = ctk.CTkButton(frame, text="Submit", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                  command=submit_comment)
    submit_button.pack(pady=10)

def show_playlists(sub_status, frame, user_id):
    global playlist_frame
    playlist_frame = ctk.CTkFrame(frame, fg_color=SPOTIFY_BLACK)
    playlist_frame.pack(fill="both", expand=True, padx=10, pady=10)

    create_button = ctk.CTkButton(playlist_frame, text="Create Playlist", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                  command=lambda: create_playlist_window(user_id, playlists_container))
    create_button.pack(pady=10, padx=10, anchor="n")

    playlists_container = ctk.CTkFrame(playlist_frame, fg_color=SPOTIFY_GRAY)
    playlists_container.pack(fill="both", expand=True, padx=10, pady=10)

    refresh_playlists(user_id, playlists_container)
#----------------------------------------------------------------

def show_liked_songs(sub_status, frame, user_id):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.SongID, s.Title, g.GenreName, u.UserName
        FROM SongLikes ls
        JOIN Songs s ON ls.SongID = s.SongID
        LEFT JOIN Genre g ON s.GenreID = g.GenreID
        LEFT JOIN Users u ON s.ArtistID = u.UserID
        WHERE ls.UserID = ?
    """, (user_id,))
    liked_songs = cursor.fetchall()
    cursor.close()
    conn.close()

    canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_BLACK)
    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color=SPOTIFY_BLACK)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for song in liked_songs:
        song_frame = ctk.CTkFrame(scrollable_frame, fg_color=SPOTIFY_GRAY)
        song_frame.pack(fill="x", pady=5)

        song_label = ctk.CTkLabel(song_frame, text=f"{song[1]} - {song[2]} by {song[3]}", text_color=SPOTIFY_WHITE)
        song_label.pack(side="left", padx=10)
        
        song_label.bind("<Button-1>", lambda event, song_id=song[0]: show_song_lyrics(song_id, frame))

        unlike_button = ctk.CTkButton(song_frame, text="Unlike", fg_color=SPOTIFY_RED, hover_color="#FF0000",
                                      command=lambda song_id=song[0]: unlike_song(song_id, user_id, frame))
        unlike_button.pack(side="right", padx=5)

        comment_button = ctk.CTkButton(song_frame, text="Comment", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                       command=lambda song_id=song[0]: comment_song(song_id, user_id))
        comment_button.pack(side="right", padx=5)

def unlike_song(song_id, user_id, frame):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC UnlikeSong  ?, ?", (user_id, song_id))
        conn.commit()
        messagebox.showinfo("Success", "Song unliked successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    show_liked_songs("Premium", frame, user_id)  # Refresh the liked songs list
#----------------------------------------------------------------

def show_recommended(sub_status, frame, user_id):
    for widget in frame.winfo_children():
        widget.destroy()

    recommended_songs_frame = ctk.CTkFrame(frame, fg_color=SPOTIFY_GRAY)
    recommended_albums_frame = ctk.CTkFrame(frame, fg_color=SPOTIFY_GRAY)

    ctk.CTkLabel(recommended_songs_frame, text="Song Suggestions", font=("Helvetica", 16, "bold"), text_color=SPOTIFY_WHITE).pack(pady=10)
    ctk.CTkLabel(recommended_albums_frame, text="Album Suggestions", font=("Helvetica", 16, "bold"), text_color=SPOTIFY_WHITE).pack(pady=10)

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT Title FROM SuggestSongs(?)", (user_id,))
    songs = cursor.fetchall()

    cursor.execute("SELECT AlbumTitle FROM SuggestAlbums(?)", (user_id,))
    albums = cursor.fetchall()

    cursor.close()
    conn.close()

    for song in songs:
        ctk.CTkLabel(recommended_songs_frame, text=song[0], fg_color=SPOTIFY_GREEN, text_color=SPOTIFY_WHITE).pack(pady=5)

    for album in albums:
        ctk.CTkLabel(recommended_albums_frame, text=album[0], fg_color=SPOTIFY_GREEN, text_color=SPOTIFY_WHITE).pack(pady=5)

    recommended_songs_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    recommended_albums_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)


#----------------------------------------------------------------

def show_followers(sub_status, frame, user_id):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM GetFollowers(?)", (user_id,))
    followers = cursor.fetchall()
    cursor.close()
    conn.close()

    canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_BLACK)
    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color=SPOTIFY_BLACK)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for follower in followers:
        follower_frame = ctk.CTkFrame(scrollable_frame, fg_color=SPOTIFY_GRAY)
        follower_frame.pack(fill="x", pady=5)

        follower_label = ctk.CTkLabel(follower_frame, text=f"{follower[1]}", text_color=SPOTIFY_WHITE)
        follower_label.pack(side="left", padx=10)
        
        follower_label.bind("<Button-1>", lambda event, follower_id=follower[0]: show_user_info(follower_id, frame))

def show_user_info(user_id, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.UserName, u.Email, u.BirthYear, u.SubscriptionStatus, c.CountryName
        FROM Users u
        LEFT JOIN Country c ON u.CountryID = c.CountryID
        WHERE u.UserID = ?
    """, (user_id,))
    user_info = cursor.fetchone()
    cursor.close()
    conn.close()

    if user_info:
        user_name_label = ctk.CTkLabel(frame, text=f"User Name: {user_info[0]}", text_color=SPOTIFY_WHITE)
        user_name_label.pack(pady=10)
        
        email_label = ctk.CTkLabel(frame, text=f"Email: {user_info[1]}", text_color=SPOTIFY_WHITE)
        email_label.pack(pady=10)
        
        dob_label = ctk.CTkLabel(frame, text=f"BirthYear: {user_info[2]}", text_color=SPOTIFY_WHITE)
        dob_label.pack(pady=10)
        
        sub_status_label = ctk.CTkLabel(frame, text=f"Subscription Status: {user_info[3]}", text_color=SPOTIFY_WHITE)
        sub_status_label.pack(pady=10)

        country_label = ctk.CTkLabel(frame, text=f"Country: {user_info[4]}", text_color=SPOTIFY_WHITE)
        country_label.pack(pady=10)

#----------------------------------------------------------------

def show_followings(sub_status, frame, user_id):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM GetFollowings(?)", (user_id,))
    followings = cursor.fetchall()
    cursor.close()
    conn.close()

    canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_BLACK)
    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color=SPOTIFY_BLACK)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for following in followings:
        following_frame = ctk.CTkFrame(scrollable_frame, fg_color=SPOTIFY_GRAY)
        following_frame.pack(fill="x", pady=5)

        following_label = ctk.CTkLabel(following_frame, text=f"{following[1]}", text_color=SPOTIFY_WHITE)
        following_label.pack(side="left", padx=10)
        
        following_label.bind("<Button-1>", lambda event, following_id=following[0]: show_user_info(following_id, frame))

        unfollow_button = ctk.CTkButton(following_frame, text="Unfollow", fg_color=SPOTIFY_RED, hover_color="#FF0000",
                                        command=lambda following_id=following[0]: unfollow_user(user_id, following_id, frame))
        unfollow_button.pack(side="right", padx=5)

def unfollow_user(user_id, following_id, frame):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC UnfollowUser ?, ?", (user_id, following_id))
        conn.commit()
        messagebox.showinfo("Success", "User unfollowed successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    show_followings("Premium", frame, user_id)

#----------------------------------------------------------------


def show_concert_tickets(sub_status, frame, user_id):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.TicketID, c.ConcertName, c.ConcertDate, c.TicketPrice, c.IsCancelled, t.IsCancelled
        FROM Tickets t
        JOIN Concerts c ON t.ConcertID = c.ConcertID
        WHERE t.UserID = ? AND t.IsExpired = 0 AND t.IsCancelled = 0
    """, (user_id,))
    valid_tickets = cursor.fetchall()

    cursor.execute("""
        SELECT t.TicketID, c.ConcertName, c.ConcertDate, c.TicketPrice, c.IsCancelled, t.IsCancelled
        FROM Tickets t
        JOIN Concerts c ON t.ConcertID = c.ConcertID
        WHERE t.UserID = ? AND (t.IsExpired = 1 OR t.IsCancelled = 1 OR c.IsCancelled = 1)
    """, (user_id,))
    expired_or_cancelled_tickets = cursor.fetchall()

    cursor.close()
    conn.close()

    valid_label = ctk.CTkLabel(frame, text="Valid Tickets", text_color=SPOTIFY_WHITE)
    valid_label.pack(pady=10)

    valid_canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_BLACK)
    valid_scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=valid_canvas.yview)
    valid_scrollable_frame = ctk.CTkFrame(valid_canvas, fg_color=SPOTIFY_BLACK)

    valid_scrollable_frame.bind(
        "<Configure>",
        lambda e: valid_canvas.configure(
            scrollregion=valid_canvas.bbox("all")
        )
    )

    valid_canvas.create_window((0, 0), window=valid_scrollable_frame, anchor="nw")
    valid_canvas.configure(yscrollcommand=valid_scrollbar.set)

    valid_canvas.pack(side="left", fill="both", expand=True)
    valid_scrollbar.pack(side="right", fill="y")

    for ticket in valid_tickets:
        ticket_frame = ctk.CTkFrame(valid_scrollable_frame, fg_color=SPOTIFY_GRAY)
        ticket_frame.pack(fill="x", pady=5)

        status = "Cancelled by Artist" if ticket[4] else "Valid"
        ticket_label = ctk.CTkLabel(ticket_frame, text=f"{ticket[1]} on {ticket[2]} - ${ticket[3]} - {status}", text_color=SPOTIFY_WHITE)
        ticket_label.pack(side="left", padx=10)

        if not ticket[4]:
            cancel_button = ctk.CTkButton(ticket_frame, text="Cancel Ticket", fg_color=SPOTIFY_RED, hover_color="#FF0000",
                                          command=lambda ticket_id=ticket[0], price=ticket[3]: cancel_ticket(ticket_id, user_id, price, frame))
            cancel_button.pack(side="right", padx=5)

    expired_label = ctk.CTkLabel(frame, text="Expired or Cancelled Tickets", text_color=SPOTIFY_WHITE)
    expired_label.pack(pady=10)

    expired_canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_BLACK)
    expired_scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=expired_canvas.yview)
    expired_scrollable_frame = ctk.CTkFrame(expired_canvas, fg_color=SPOTIFY_BLACK)

    expired_scrollable_frame.bind(
        "<Configure>",
        lambda e: expired_canvas.configure(
            scrollregion=expired_canvas.bbox("all")
        )
    )

    expired_canvas.create_window((0, 0), window=expired_scrollable_frame, anchor="nw")
    expired_canvas.configure(yscrollcommand=expired_scrollbar.set)

    expired_canvas.pack(side="left", fill="both", expand=True)
    expired_scrollbar.pack(side="right", fill="y")

    for ticket in expired_or_cancelled_tickets:
        ticket_frame = ctk.CTkFrame(expired_scrollable_frame, fg_color=SPOTIFY_GRAY)
        ticket_frame.pack(fill="x", pady=5)

        if ticket[4]:
            status = "Cancelled by Artist"
        elif ticket[5]:
            status = "Cancelled by you"
        else:
            status = "Expired"

        ticket_label = ctk.CTkLabel(ticket_frame, text=f"{ticket[1]} on {ticket[2]} - ${ticket[3]} - {status}", text_color=SPOTIFY_WHITE)
        ticket_label.pack(side="left", padx=10)

def cancel_ticket(ticket_id, user_id, price, frame):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.IsCancelled 
            FROM Tickets t
            JOIN Concerts c ON t.ConcertID = c.ConcertID
            WHERE t.TicketID = ?
        """, (ticket_id,))
        concert_cancelled = cursor.fetchone()[0]

        if concert_cancelled:
            messagebox.showinfo("Info", "This concert has already been cancelled by the Artist and the fee has been refunded to your wallet!")
        else:
            cursor.execute("UPDATE Tickets SET IsCancelled = 1 WHERE TicketID = ?", (ticket_id,))
            cursor.execute("EXEC CancelTicket ?, ?", (user_id, ticket_id))
            conn.commit()
            messagebox.showinfo("Success", "The ticket has been successfully cancelled and the fee has been refunded to your wallet!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    show_concert_tickets("Premium", frame, user_id)

#----------------------------------------------------------------


def show_concerts(sub_status, frame, user_id):
    for widget in frame.winfo_children():
        widget.destroy()

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.ConcertID, c.ConcertName, c.ConcertDate, c.TicketPrice, u.UserName as ArtistName
        FROM Concerts c
        JOIN Users u ON c.ArtistID = u.UserID
        WHERE c.IsCancelled = 0 
        ORDER BY c.ConcertDate
    """)
    concerts = cursor.fetchall()

    cursor.close()
    conn.close()

    concerts_label = ctk.CTkLabel(frame, text="Available Concerts", text_color=SPOTIFY_WHITE, font=("Helvetica", 16, "bold"))
    concerts_label.pack(pady=10)

    canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_BLACK)
    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color=SPOTIFY_BLACK)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for concert in concerts:
        concert_frame = ctk.CTkFrame(scrollable_frame, fg_color=SPOTIFY_GRAY)
        concert_frame.pack(fill="x", pady=5, padx=10)

        concert_info = f"{concert[1]} by {concert[4]} on {concert[2]} - ${concert[3]}"
        concert_label = ctk.CTkLabel(concert_frame, text=concert_info, text_color=SPOTIFY_WHITE)
        concert_label.pack(side="left", padx=10)

        buy_button = ctk.CTkButton(concert_frame, text="Buy Ticket", fg_color=SPOTIFY_GREEN, hover_color="#1ED760",
                                   command=lambda cid=concert[0], price=concert[3]: buy_ticket(cid, user_id, price, frame))
        buy_button.pack(side="right", padx=5)

def buy_ticket(concert_id, user_id, price, frame):
    def refresh_callback():
        buy_ticket(concert_id, user_id, price, frame)
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT w.Balance FROM Users u JOIN Wallet w ON u.UserID = w.UserID WHERE u.UserID = ?", (user_id,))
        balance = cursor.fetchone()[0]

        if balance < price:
            messagebox.showinfo("Insufficient Funds", "Your wallet balance is insufficient. Please charge your wallet.")
            charge_wallet(user_id, refresh_callback)
            return

        purchase_date = datetime.now()

        cursor.execute("EXEC BuyTicket ?, ?", (user_id, concert_id))

        conn.commit()
        messagebox.showinfo("Success", "Ticket purchased successfully!")

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")

    finally:
        cursor.close()
        conn.close()

    show_concerts("Premium", frame, user_id)

#----------------------------------------------------------------

def create_tab(parent, name, command, sub_status, user_id):
    frame = ctk.CTkFrame(parent, fg_color=SPOTIFY_GRAY)
    label = ctk.CTkLabel(frame, text=f"{name} Content", text_color=SPOTIFY_WHITE)
    label.pack(pady=20)
    command(sub_status, frame, user_id)
    return frame

#---------------------------------------------------------------

def create_tab_view(parent, username):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT UserID, SubscriptionStatus FROM Users WHERE username = ?
    """, (username,))
    user_row = cursor.fetchone()
    user_id = user_row[0]
    sub_status = user_row[1]
    cursor.close()
    conn.close()

    tab_view = ctk.CTkTabview(parent, fg_color=SPOTIFY_GRAY)
    tab_view.pack(fill="both", expand=True, padx=10, pady=10)

    tabs = {
        "Song List": show_song_list
    }

    if sub_status == "Premium":
        tabs.update({
            "Albums": show_albums,
            "Playlists": show_playlists,
            "Liked Songs": show_liked_songs,
            "Recommended": show_recommended,
            "Followers": show_followers,
            "Followings": show_followings,
            "Concert Tickets": show_concert_tickets,
            "Concerts": show_concerts
        })

    for tab, command in tabs.items():
        tab_frame = tab_view.add(tab)
        frame = create_tab(tab_frame, tab, command, sub_status, user_id)
        frame.pack(fill="both", expand=True, padx=10, pady=10)




def create_user_page(root, username, return_to_login, reset_user_page, isArtist):        
    root.configure(fg_color=SPOTIFY_BLACK)
    
    create_header(root, username, return_to_login)
    create_menu_bar(root, username, reset_user_page, isArtist)
    create_tab_view(root, username)
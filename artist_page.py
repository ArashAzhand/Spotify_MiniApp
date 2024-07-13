import customtkinter as ctk
import pyodbc
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from user_page import *

SPOTIFY_GRAY = "#282828"
SPOTIFY_WHITE = "#FFFFFF"
SPOTIFY_GREEN = "#1DB954"
SPOTIFY_BLACK = "#191414"
SPOTIFY_RED = "#FF0000"

def connect_to_db():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=LAPTOP-KE2OAO1H;'
        'DATABASE=temp_spotify;'
        'Trusted_Connection=yes;',
        autocommit=True
    )
    return conn

def get_artist_id(username):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT UserID FROM Users WHERE UserName = ?", (username,))
    artist_id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return artist_id

def add_song_to_db(title, genre_id, release_date, lyrics, artist_id, can_add_to_playlist):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Songs (Title, GenreID, ReleaseDate, Lyrics, ArtistID, CanAddToPlaylist) VALUES (?, ?, ?, ?, ?, ?)",
                       (title, genre_id, release_date, lyrics, artist_id, can_add_to_playlist))
        conn.commit()
        messagebox.showinfo("Success", "Song added successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def fetch_songs():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT SongID, Title, CanAddToPlaylist FROM Songs")
    songs = cursor.fetchall()
    cursor.close()
    conn.close()
    return songs

def delete_song(song_id, username):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("select UserID from Users where Username = ?", username)
        user_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT 1 FROM Songs WHERE SongID = ? AND ArtistID = ?", (song_id, user_id))
        out = cursor.fetchall()
        if not out:
            messagebox.showerror("delete error", "You are not allowed to delete this song")
        else:
            cursor.execute("EXEC DeleteSong ?, ?", (user_id, song_id))
            conn.commit()
            messagebox.showinfo("Success", "Song deleted successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    song_handling(username)

def toggle_playlist_option(song_id, current_value, username):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        new_value = not current_value
        cursor.execute("UPDATE Songs SET CanAddToPlaylist = ? WHERE SongID = ?", (new_value, song_id))
        conn.commit()
        messagebox.showinfo("Success", "Song playlist option updated successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    song_handling(username)

def add_song_window(username):
    add_song_window = ctk.CTkToplevel()
    add_song_window.title("Add Song")
    add_song_window.geometry("400x400")
    add_song_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(add_song_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter song title")
    title_entry.pack(pady=10)

    genre_id_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter genre ID")
    genre_id_entry.pack(pady=10)

    release_date_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter release date (YYYY-MM-DD)")
    release_date_entry.pack(pady=10)

    lyrics_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter lyrics")
    lyrics_entry.pack(pady=10)

    can_add_to_playlist_var = tk.BooleanVar(value=True)
    can_add_to_playlist_checkbox = ctk.CTkCheckBox(frame, text="Can add to playlist", variable=can_add_to_playlist_var)
    can_add_to_playlist_checkbox.pack(pady=10)

    def submit_new_song():
        title = title_entry.get()
        genre_id = genre_id_entry.get()
        release_date = release_date_entry.get()
        lyrics = lyrics_entry.get()
        can_add_to_playlist = can_add_to_playlist_var.get()
        artist_id = get_artist_id(username)

        try:
            datetime.strptime(release_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        add_song_to_db(title, genre_id, release_date, lyrics, artist_id, can_add_to_playlist)
        add_song_window.destroy()
        song_handling(username)

    submit_button = ctk.CTkButton(frame, text="Add Song", fg_color=SPOTIFY_GREEN, hover_color="#1ED760", command=submit_new_song)
    submit_button.pack(pady=10)

def song_handling(username):
    song_window = ctk.CTkToplevel()
    song_window.title("Song Handling")
    song_window.geometry("600x400")
    song_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(song_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    add_song_button = ctk.CTkButton(frame, text="Add Song", fg_color=SPOTIFY_GREEN, hover_color="#1ED760", command=lambda: add_song_window(username))
    add_song_button.pack(pady=10)

    canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_GRAY, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame = ctk.CTkFrame(canvas, fg_color=SPOTIFY_GRAY)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    songs = fetch_songs()

    for song in songs:
        song_id, title, can_add_to_playlist = song
        song_frame = ctk.CTkFrame(scrollable_frame, fg_color=SPOTIFY_GRAY)
        song_frame.pack(fill="x", pady=5)

        song_label = ctk.CTkLabel(song_frame, text=title, text_color=SPOTIFY_WHITE)
        song_label.pack(side="left", padx=10)

        delete_button = ctk.CTkButton(song_frame, text="Delete", fg_color=SPOTIFY_RED, hover_color="#FF0000", command=lambda song_id=song_id: delete_song(song_id, username))
        delete_button.pack(side="right", padx=5)

        toggle_button_text = "Disable Playlist" if can_add_to_playlist else "Enable Playlist"
        toggle_button = ctk.CTkButton(song_frame, text=toggle_button_text, fg_color=SPOTIFY_GREEN, hover_color="#1ED760", command=lambda song_id=song_id, value=can_add_to_playlist: toggle_playlist_option(song_id, value, username))
        toggle_button.pack(side="right", padx=5)




def album_handling(username):
    artist_id = get_artist_id(username)
    
    album_window = ctk.CTkToplevel()
    album_window.title("Album Handling")
    album_window.geometry("600x400")
    album_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(album_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    add_album_button = ctk.CTkButton(frame, text="Add Album", fg_color=SPOTIFY_GREEN, hover_color="#1ED760", command=lambda: add_album_window(username))
    add_album_button.pack(pady=10)

    canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_GRAY, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame = ctk.CTkFrame(canvas, fg_color=SPOTIFY_GRAY)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    albums = fetch_albums()

    for album in albums:
        album_id, title = album
        album_frame = ctk.CTkFrame(scrollable_frame, fg_color=SPOTIFY_GRAY)
        album_frame.pack(fill="x", pady=5)

        album_label = ctk.CTkLabel(album_frame, text=title, text_color=SPOTIFY_WHITE)
        album_label.pack(side="left", padx=10)

        delete_button = ctk.CTkButton(album_frame, text="Delete", fg_color=SPOTIFY_RED, hover_color="#FF0000", command=lambda album_id=album_id: delete_album(album_id, username))
        delete_button.pack(side="right", padx=5)

        manage_songs_button = ctk.CTkButton(album_frame, text="Manage Songs", fg_color=SPOTIFY_GREEN, hover_color="#1ED760", command=lambda album_id=album_id: manage_album_songs(album_id))
        manage_songs_button.pack(side="right", padx=5)

def fetch_albums():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT AlbumID, Title FROM Albums")
    albums = cursor.fetchall()
    cursor.close()
    conn.close()
    return albums

def delete_album(album_id, username):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC DeleteAlbum ?", (album_id,))
        conn.commit()
        messagebox.showinfo("Success", "Album deleted successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    album_handling(username)

def add_album_to_db(title, artist_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Albums (Title, ArtistID) VALUES (?, ?)", (title, artist_id))
        conn.commit()
        messagebox.showinfo("Success", "Album added successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def add_album_window(username):
    add_album_window = ctk.CTkToplevel()
    add_album_window.title("Add Album")
    add_album_window.geometry("400x300")
    add_album_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(add_album_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter album title")
    title_entry.pack(pady=10)

    def submit_new_album():
        title = title_entry.get()
        artist_id = get_artist_id(username)

        add_album_to_db(title, artist_id)
        add_album_window.destroy()
        album_handling(username)

    submit_button = ctk.CTkButton(frame, text="Add Album", fg_color=SPOTIFY_GREEN, hover_color="#1ED760", command=submit_new_album)
    submit_button.pack(pady=10)

def manage_album_songs(album_id):
    manage_album_songs_window = ctk.CTkToplevel()
    manage_album_songs_window.title("Manage Album Songs")
    manage_album_songs_window.geometry("450x700")
    manage_album_songs_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(manage_album_songs_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    existing_songs_label = ctk.CTkLabel(frame, text="Songs in Album", text_color=SPOTIFY_WHITE)
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
        JOIN AlbumSongs a ON s.SongID = a.SongID 
        WHERE a.AlbumID = ?
    """, (album_id,))
    existing_songs = cursor.fetchall()

    for song in existing_songs:
        song_label = ctk.CTkLabel(scrollable_frame_existing, text=song[1], text_color=SPOTIFY_WHITE)
        song_label.pack(anchor="w", pady=5)

    add_songs_label = ctk.CTkLabel(frame, text="Add Songs to Album", text_color=SPOTIFY_WHITE)
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

    cursor.execute("SELECT SongID, Title FROM Songs")
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

    def add_songs_to_album():
        selected_song_ids = [song_id for song_id, var in song_vars.items() if var.get() == 1]
        if selected_song_ids:
            conn = connect_to_db()
            cursor = conn.cursor()
            try:
                for song_id in selected_song_ids:
                    cursor.execute("INSERT INTO AlbumSongs (AlbumID, SongID) VALUES (?, ?)", (album_id, song_id))
                conn.commit()
                messagebox.showinfo("Success", "Songs added to album successfully!")
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                cursor.close()
                conn.close()
            manage_album_songs_window.destroy()
        else:
            messagebox.showerror("Error", "Please select at least one song.")

    add_button = ctk.CTkButton(frame, text="Add to Album", fg_color=SPOTIFY_GREEN, hover_color="#1ED760", command=add_songs_to_album)
    add_button.pack(pady=10)





def concert_handling(username):
    artist_id = get_artist_id(username)
    
    concert_window = ctk.CTkToplevel()
    concert_window.title("Concert Handling")
    concert_window.geometry("600x400")
    concert_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(concert_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    add_concert_button = ctk.CTkButton(frame, text="Add Concert", fg_color=SPOTIFY_GREEN, hover_color="#1ED760", command=lambda: add_concert_window(username))
    add_concert_button.pack(pady=10)

    canvas = ctk.CTkCanvas(frame, bg=SPOTIFY_GRAY, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ctk.CTkScrollbar(frame, orientation="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame = ctk.CTkFrame(canvas, fg_color=SPOTIFY_GRAY)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    concerts = fetch_concerts(artist_id)

    for concert in concerts:
        concert_id, title, date, price = concert
        concert_frame = ctk.CTkFrame(scrollable_frame, fg_color=SPOTIFY_GRAY)
        concert_frame.pack(fill="x", pady=5)

        concert_label = ctk.CTkLabel(concert_frame, text=f"{title} - {date} - ${price}", text_color=SPOTIFY_WHITE)
        concert_label.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(concert_frame, text="Cancel", fg_color=SPOTIFY_RED, hover_color="#FF0000", command=lambda concert_id=concert_id: cancel_concert(concert_id, username))
        cancel_button.pack(side="right", padx=5)

def fetch_concerts(artist_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ConcertID, ConcertName, ConcertDate, TicketPrice FROM Concerts WHERE isCancelled = 0 AND ArtistID = ?", (artist_id,))
    concerts = cursor.fetchall()
    cursor.close()
    conn.close()
    return concerts

def cancel_concert(concert_id, username):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC ArtistCancelConcert ?", (concert_id,))
        conn.commit()
        messagebox.showinfo("Success", "Concert canceled and refund issued!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    concert_handling(username)

def add_concert_to_db(title, date, price, artist_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Concerts (ConcertName, ConcertDate, TicketPrice, ArtistID) VALUES (?, ?, ?, ?)", (title, date, price, artist_id))
        conn.commit()
        messagebox.showinfo("Success", "Concert added successfully!")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def add_concert_window(username):
    add_concert_window = ctk.CTkToplevel()
    add_concert_window.title("Add Concert")
    add_concert_window.geometry("400x300")
    add_concert_window.configure(fg_color=SPOTIFY_BLACK)

    frame = ctk.CTkFrame(add_concert_window, fg_color=SPOTIFY_GRAY)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter concert title")
    title_entry.pack(pady=10)

    date_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter date (YYYY-MM-DD)")
    date_entry.pack(pady=10)

    price_entry = ctk.CTkEntry(frame, width=250, placeholder_text="Enter price")
    price_entry.pack(pady=10)

    def submit_new_concert():
        title = title_entry.get()
        date = date_entry.get()
        price = price_entry.get()
        artist_id = get_artist_id(username)

        try:
            datetime.strptime(date, '%Y-%m-%d')
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Invalid date or price format.")
            return

        add_concert_to_db(title, date, price, artist_id)
        add_concert_window.destroy()
        concert_handling(username)

    submit_button = ctk.CTkButton(frame, text="Add Concert", fg_color=SPOTIFY_GREEN, hover_color="#1ED760", command=submit_new_concert)
    submit_button.pack(pady=10)

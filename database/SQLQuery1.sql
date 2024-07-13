CREATE TABLE Genre (
    GenreID INT PRIMARY KEY IDENTITY(1,1),
    GenreName VARCHAR(50) NOT NULL UNIQUE
);
--select * from Artists
--select * from Users

CREATE TABLE Country (
    CountryID INT PRIMARY KEY IDENTITY(1,1),
    CountryName VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    UserName VARCHAR(50) NOT NULL UNIQUE,
    [Password] VARCHAR(255) NOT NULL,
    BirthYear INT,
    Email VARCHAR(100) NOT NULL UNIQUE,
    CountryID INT,
    SubscriptionStatus VARCHAR(10) NOT NULL DEFAULT 'Basic' CHECK (SubscriptionStatus IN ('Premium', 'Basic')),
    IsArtist BIT DEFAULT 0,
    FOREIGN KEY (CountryID) REFERENCES Country(CountryID)
);


CREATE TABLE Artists (
    ArtistID INT PRIMARY KEY,
    ArtistName VARCHAR(50) NOT NULL UNIQUE,
    FOREIGN KEY (ArtistID) REFERENCES Users(UserID)
);

CREATE TABLE Songs (
    SongID INT PRIMARY KEY IDENTITY(1,1),
    Title VARCHAR(100) NOT NULL,
    GenreID INT,
    ReleaseDate DATE,
    Lyrics TEXT,
    ArtistID INT,
    CanAddToPlaylist BIT DEFAULT 1,
    FOREIGN KEY (GenreID) REFERENCES Genre(GenreID),
    FOREIGN KEY (ArtistID) REFERENCES Users(UserID)
);

CREATE TABLE Albums (
    AlbumID INT PRIMARY KEY IDENTITY(1,1),
    Title VARCHAR(100) NOT NULL,
    ReleaseDate DATE,
    ArtistID INT,
    FOREIGN KEY (ArtistID) REFERENCES Users(UserID)
);

CREATE TABLE AlbumSongs (
    AlbumID INT,
    SongID INT,
    PRIMARY KEY (AlbumID, SongID),
    FOREIGN KEY (AlbumID) REFERENCES Albums(AlbumID),
    FOREIGN KEY (SongID) REFERENCES Songs(SongID)
);

CREATE TABLE Playlists (
    PlaylistID INT PRIMARY KEY IDENTITY(1,1),
    PlaylistName VARCHAR(100) NOT NULL,
    UserID INT,
    IsPrivate BIT DEFAULT 0,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE PlaylistSongs (
    PlaylistID INT,
    SongID INT,
    PRIMARY KEY (PlaylistID, SongID),
    FOREIGN KEY (PlaylistID) REFERENCES Playlists(PlaylistID),
    FOREIGN KEY (SongID) REFERENCES Songs(SongID)
);

CREATE TABLE SongLikes (
    UserID INT,
    SongID INT,
    PRIMARY KEY (UserID, SongID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (SongID) REFERENCES Songs(SongID)
);

CREATE TABLE PlaylistLikes (
    UserID INT,
    PlaylistID INT,
    PRIMARY KEY (UserID, PlaylistID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (PlaylistID) REFERENCES Playlists(PlaylistID)
);

CREATE TABLE AlbumLikes (
    UserID INT,
    AlbumID INT,
    PRIMARY KEY (UserID, AlbumID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (AlbumID) REFERENCES Albums(AlbumID)
);

CREATE TABLE SongComments (
    CommentID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    SongID INT,
    CommentText TEXT,
    CommentDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (SongID) REFERENCES Songs(SongID)
);

CREATE TABLE PlaylistComments (
    CommentID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    PlaylistID INT,
    CommentText TEXT,
    CommentDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (PlaylistID) REFERENCES Playlists(PlaylistID)
);

CREATE TABLE AlbumComments (
    CommentID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    AlbumID INT,
    CommentText TEXT,
    CommentDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (AlbumID) REFERENCES Albums(AlbumID)
);


CREATE TABLE Friends (
    UserID INT,
    FriendID INT,
    Status VARCHAR(10) DEFAULT 'Pending' CHECK (Status IN ('Rejected', 'Pending', 'Accepted')),
    PRIMARY KEY (UserID, FriendID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (FriendID) REFERENCES Users(UserID)
);

	

CREATE TABLE Followers (
    UserID INT,
    FollowerID INT,
    PRIMARY KEY (UserID, FollowerID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (FollowerID) REFERENCES Users(UserID)
);



CREATE TABLE Concerts (
    ConcertID INT PRIMARY KEY IDENTITY(1,1),
    ConcertName VARCHAR(100) NOT NULL,
    ConcertDate DATE,
    TicketPrice DECIMAL(10, 2),
    ArtistID INT,
    IsCancelled BIT DEFAULT 0,
    FOREIGN KEY (ArtistID) REFERENCES Users(UserID)
);

CREATE TABLE Tickets (
    TicketID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    ConcertID INT,
    PurchaseDate DATE,
    IsExpired BIT DEFAULT 0,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (ConcertID) REFERENCES Concerts(ConcertID)
);

ALTER TABLE Tickets ADD IsCancelled BIT DEFAULT 0;

CREATE TABLE Wallet (
    WalletID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    Balance DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE WalletTransactions (
    TransactionID INT PRIMARY KEY IDENTITY(1,1),
    WalletID INT,
    Amount DECIMAL(10, 2),
    TransactionDate DATETIME DEFAULT GETDATE(),
    TransactionType VARCHAR(10) NOT NULL CHECK(TransactionType IN ('Deposit' ,'Withdrawal')),
    FOREIGN KEY (WalletID) REFERENCES Wallet(WalletID)
);


CREATE TABLE ListeningHistory (
    HistoryID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    SongID INT,
    ListenDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (SongID) REFERENCES Songs(SongID)
);

CREATE TABLE [Messages] (
    MessageID INT PRIMARY KEY IDENTITY(1,1),
    SenderID INT,
    ReceiverID INT,
    MessageContent NVARCHAR(MAX),
    SendTime DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (SenderID) REFERENCES Users(UserID),
    FOREIGN KEY (ReceiverID) REFERENCES Users(UserID)
);



-----------------------------------------------------
/*DROP TABLE IF EXISTS ListeningHistory;
DROP TABLE IF EXISTS [Messages];
DROP TABLE IF EXISTS WalletTransactions;
DROP TABLE IF EXISTS Tickets;
DROP TABLE IF EXISTS Concerts;
DROP TABLE IF EXISTS Followers;
DROP TABLE IF EXISTS Friends;
DROP TABLE IF EXISTS AlbumComments;
DROP TABLE IF EXISTS PlaylistComments;
DROP TABLE IF EXISTS SongComments;
DROP TABLE IF EXISTS AlbumLikes;
DROP TABLE IF EXISTS PlaylistLikes;
DROP TABLE IF EXISTS SongLikes;
DROP TABLE IF EXISTS PlaylistSongs;
DROP TABLE IF EXISTS Playlists;
DROP TABLE IF EXISTS AlbumSongs;
DROP TABLE IF EXISTS Albums;
DROP TABLE IF EXISTS Songs;
DROP TABLE IF EXISTS Wallet;
DROP TABLE IF EXISTS Artists;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Country;
DROP TABLE IF EXISTS Genre;*/




-----------------------------------------------------------
INSERT INTO Country (CountryName) VALUES ('United States');
INSERT INTO Country (CountryName) VALUES ('United Kingdom');
INSERT INTO Country (CountryName) VALUES ('Iran');
INSERT INTO Country (CountryName) VALUES ('Australia');
INSERT INTO Country (CountryName) VALUES ('Germany');
INSERT INTO Country (CountryName) VALUES ('France');
INSERT INTO Country (CountryName) VALUES ('Japan');
INSERT INTO Country (CountryName) VALUES ('Brazil');

INSERT INTO Genre (GenreName) VALUES ('Rock');
INSERT INTO Genre (GenreName) VALUES ('Pop');
INSERT INTO Genre (GenreName) VALUES ('Jazz');
INSERT INTO Genre (GenreName) VALUES ('Classical');
INSERT INTO Genre (GenreName) VALUES ('Hip Hop');
INSERT INTO Genre (GenreName) VALUES ('Country');
INSERT INTO Genre (GenreName) VALUES ('Electronic');
INSERT INTO Genre (GenreName) VALUES ('Reggae');
INSERT INTO Genre (GenreName) VALUES ('Blues');
INSERT INTO Genre (GenreName) VALUES ('Metal');
------------------------------------------------------------



select * from Users

select * from Friends

delete Friends

select * from Playlists
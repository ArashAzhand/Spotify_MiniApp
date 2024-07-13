CREATE PROCEDURE InsertUser
    @UserName VARCHAR(50),
    @Password VARCHAR(255),
    @BirthYear INT,
    @Email VARCHAR(100),
    @CountryID INT,
	@IsArtist bit
AS
BEGIN
    INSERT INTO Users (UserName, [Password], BirthYear, Email, CountryID, IsArtist)
    VALUES (@UserName, @Password, @BirthYear, @Email, @CountryID, @IsArtist);

	DECLARE @NewUserID INT;
    SET @NewUserID = SCOPE_IDENTITY();

	INSERT INTO Wallet (UserID)
    VALUES (@NewUserID);

    IF @IsArtist = 1
    BEGIN
        INSERT INTO Artists (ArtistID, ArtistName)
        VALUES (@NewUserID, @UserName);

		UPDATE Users
		SET SubscriptionStatus = 'Premium'
		WHERE UserName = @UserName;
    END
END;

drop procedure InsertUser
exec insertUser qq, ww, 11, ee, 4, 0
----------------------------------------------------------


CREATE PROCEDURE UpdateUser
	@UserID int,
    @UserName VARCHAR(50),
    @Password VARCHAR(50),
    @BirthYear INT,
    @Email VARCHAR(100),
    @CountryID int
AS
BEGIN
    UPDATE Users
    SET UserName = @UserName,
        [Password] = @Password,
        BirthYear = @BirthYear,
        Email = @Email,
        CountryID = @CountryID
    WHERE UserID = @UserID;
END;



CREATE PROCEDURE DeleteUser
    @UserID INT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY

        DELETE FROM ListeningHistory WHERE UserID = @UserID;

        DELETE FROM WalletTransactions WHERE WalletID IN (SELECT WalletID FROM Wallet WHERE UserID = @UserID);

        DELETE FROM Wallet WHERE UserID = @UserID;

        DELETE FROM Tickets WHERE UserID = @UserID;

        DELETE FROM Concerts WHERE ArtistID = @UserID;

        DELETE FROM Followers WHERE UserID = @UserID OR FollowerID = @UserID;

        DELETE FROM Friends WHERE UserID = @UserID OR FriendID = @UserID;

        DELETE FROM AlbumComments WHERE UserID = @UserID;

        DELETE FROM PlaylistComments WHERE UserID = @UserID;

        DELETE FROM SongComments WHERE UserID = @UserID;

        DELETE FROM AlbumLikes WHERE UserID = @UserID;

        DELETE FROM PlaylistLikes WHERE UserID = @UserID;

        DELETE FROM SongLikes WHERE UserID = @UserID;

        DELETE FROM PlaylistSongs WHERE PlaylistID IN (SELECT PlaylistID FROM Playlists WHERE UserID = @UserID);

        DELETE FROM Playlists WHERE UserID = @UserID;

        DELETE FROM AlbumSongs WHERE AlbumID IN (SELECT AlbumID FROM Albums WHERE ArtistID = @UserID);

        DELETE FROM Albums WHERE ArtistID = @UserID;

        DELETE FROM Songs WHERE ArtistID = @UserID;

        DELETE FROM Artists WHERE ArtistID = @UserID;

        DELETE FROM [Messages] WHERE SenderID = @UserID OR ReceiverID = @UserID;

        DELETE FROM Users WHERE UserID = @UserID;

        -- Commit transaction
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        -- Rollback transaction in case of error
        ROLLBACK TRANSACTION;

        -- Raise the error
        THROW;
    END CATCH
END;

select * from Users

EXEC DeleteUser @UserID = 8;

--drop procedure DeleteUser
-------------------------------------------------checked


CREATE PROCEDURE Deposit
    @UserID INT,
    @Amount DECIMAL(10, 2)
AS
BEGIN
    UPDATE Wallet
    SET Balance = Balance + @Amount
    WHERE UserID = @UserID;

    INSERT INTO WalletTransactions (WalletID, Amount, TransactionType)
    VALUES ((SELECT WalletID FROM Wallet WHERE UserID = @UserID), @Amount, 'Deposit');
END;


CREATE PROCEDURE Withdrawal
    @UserID INT,
    @Amount DECIMAL(10, 2)
AS
BEGIN
    UPDATE Wallet
    SET Balance = Balance - @Amount
    WHERE UserID = @UserID;

    INSERT INTO WalletTransactions (WalletID, Amount, TransactionType)
    VALUES ((SELECT WalletID FROM Wallet WHERE UserID = @UserID), @Amount, 'Withdrawal');
END;

-----------------------------------------------------------


CREATE OR ALTER PROCEDURE AddFriendRequest
    @UserID INT,
    @FriendID INT
AS
BEGIN
  IF ((SELECT SubscriptionStatus FROM Users WHERE [UserID] = @UserID) = 'Basic' )
  BEGIN
    PRINT 'Please subscribe to Premium';
  END
  ELSE IF ((SELECT SubscriptionStatus FROM Users WHERE [UserID] = @FriendID) = 'Basic' )
  BEGIN
    PRINT 'This User Is not subscribed to Premium';
  END
  ELSE
    BEGIN
    -- Check if there is a pending or accepted friend request from UserID to FriendID
    IF EXISTS (
      SELECT 1 
      FROM Friends 
      WHERE UserID = @UserID 
        AND FriendID = @FriendID 
        AND Status IN ('Pending')
    )
    BEGIN
      PRINT 'A friend request already exists with status Pending or Accepted.';
    END
    ELSE IF EXISTS (
      SELECT 1 
      FROM Friends 
      WHERE UserID = @UserID 
        AND FriendID = @FriendID 
        AND Status = ('Accepted')
      UNION
      SELECT 1 
      FROM Friends 
      WHERE UserID = @FriendID
        AND FriendID = @UserID 
        AND Status = ('Accepted')
    )
    BEGIN 
      PRINT 'This User already exist in you friends list';
    END
    ELSE
    BEGIN
      -- Check if there is a rejected friend request from UserID to FriendID
      IF EXISTS (
        SELECT 1 
        FROM Friends 
        WHERE UserID = @UserID 
          AND FriendID = @FriendID 
          AND Status = 'Rejected'
      )
      BEGIN
        -- Update the status to Pending if previously rejected
        UPDATE Friends
        SET Status = 'Pending'
        WHERE UserID = @UserID 
          AND FriendID = @FriendID 
          AND Status = 'Rejected';

        PRINT 'Friend request status updated to Pending.';
      END
      ELSE
      BEGIN
        INSERT INTO Friends (UserID, FriendID, Status)
        VALUES (@UserID, @FriendID, 'Pending');

        PRINT 'Friend request sent successfully.';
      END
    END
  END
END;




-----------------------------------------------------


CREATE OR ALTER PROCEDURE LikeSong
    @UserID INT,
    @SongID INT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Check if the user has already liked the song
        IF NOT EXISTS (SELECT 1 FROM SongLikes WHERE UserID = @UserID AND SongID = @SongID)
        BEGIN
            -- Insert the like into the SongLikes table
            INSERT INTO SongLikes (UserID, SongID)
            VALUES (@UserID, @SongID);
            
            -- Notify all friends
            DECLARE @SongTitle NVARCHAR(100);
            DECLARE @UserName NVARCHAR(50);
            
            -- Get the song title
            SELECT @SongTitle = Title FROM Songs WHERE SongID = @SongID;
            
            -- Get the user name
            SELECT @UserName = UserName FROM Users WHERE UserID = @UserID;
            
            -- Insert a message into the Messages table for each friend
            INSERT INTO Messages (SenderID, ReceiverID, MessageContent, SendTime)
            SELECT @UserID, FriendID, 
                   @UserName + ' liked the song "' + @SongTitle + '".', 
                   GETDATE()
            FROM Friends
            WHERE UserID = @UserID AND Status = 'Accepted';

            PRINT 'Song liked successfully and friends notified.';
        END
        ELSE
        BEGIN
            PRINT 'User has already liked this song.';
        END

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;

        THROW;
    END CATCH
END;

CREATE OR ALTER PROCEDURE CommentOnSong
    @UserID INT,
    @SongID INT,
    @CommentText TEXT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Insert the comment into the SongComments table
        INSERT INTO SongComments (UserID, SongID, CommentText, CommentDate)
        VALUES (@UserID, @SongID, @CommentText, GETDATE());
        
        -- Notify all friends
        DECLARE @SongTitle VARCHAR(100);
        DECLARE @UserName VARCHAR(50);
        
        -- Get the song title
        SELECT @SongTitle = Title FROM Songs WHERE SongID = @SongID;
        
        -- Get the user name
        SELECT @UserName = UserName FROM Users WHERE UserID = @UserID;
        
        -- Insert a message into the Messages table for each friend
        INSERT INTO Messages (SenderID, ReceiverID, MessageContent, SendTime)
        SELECT @UserID, FriendID, 
               @UserName + ' commented on the song "' + @SongTitle + '".', 
               GETDATE()
        FROM Friends
        WHERE UserID = @UserID AND Status = 'Accepted';

        PRINT 'Comment added successfully and friends notified.';
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;

CREATE OR ALTER PROCEDURE UnlikeSong
    @UserID INT,
    @SongID INT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Check if the user has liked the song
        IF EXISTS (SELECT 1 FROM SongLikes WHERE UserID = @UserID AND SongID = @SongID)
        BEGIN
            
            DELETE FROM SongLikes WHERE UserID = @UserID AND SongID = @SongID;
            
            -- Notify all friends
            DECLARE @SongTitle VARCHAR(100);
            DECLARE @UserName VARCHAR(50);
            
            -- Get the song title
            SELECT @SongTitle = Title FROM Songs WHERE SongID = @SongID;
            
            -- Get the user name
            SELECT @UserName = UserName FROM Users WHERE UserID = @UserID;
            
            -- Insert a message into the Messages table for each friend
            INSERT INTO [Messages] (SenderID, ReceiverID, MessageContent, SendTime)
            SELECT @UserID, FriendID, 
                   @UserName + ' unliked the song "' + @SongTitle + '".', 
                   GETDATE()
            FROM Friends
            WHERE UserID = @UserID AND Status = 'Accepted';

            PRINT 'Song unliked successfully and friends notified.';
        END
        ELSE
        BEGIN
            PRINT 'User has not liked this song.';
        END

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;

CREATE PROCEDURE Follow
    @UserID INT,
    @FollowedUserID INT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Check if the follow relationship already exists
        IF NOT EXISTS (SELECT 1 FROM Followers WHERE UserID = @FollowedUserID AND FollowerID = @UserID)
        BEGIN
            -- Insert the follow relationship into the Followers table
            INSERT INTO Followers (UserID, FollowerID)
            VALUES (@FollowedUserID, @UserID);

            PRINT 'Follow relationship added successfully.';
        END
        ELSE
        BEGIN
            PRINT 'The user is already following the specified user.';
        END

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;

CREATE FUNCTION GetFollowers (@UserID INT)
RETURNS TABLE
AS
RETURN
(
    SELECT 
        U.UserID AS FollowerID,
        U.UserName AS FollowerUserName
    FROM 
        Followers F
    JOIN 
        Users U ON F.FollowerID = U.UserID
    WHERE 
        F.UserID = @UserID
);

CREATE OR ALTER FUNCTION GetFollowings (@UserID INT)
RETURNS @Following TABLE
(
    FollowingID INT,
    FollowingUserName VARCHAR(50)
)
AS
BEGIN
    INSERT INTO @Following
    SELECT 
        U.UserID AS FollowingID,
        U.UserName AS FollowingUserName
    FROM 
        Followers F
    JOIN 
        Users U ON F.UserID = U.UserID
    WHERE 
        F.FollowerID = @UserID;

    RETURN;
END;

CREATE OR ALTER PROCEDURE BuyTicket
    @UserID INT,
    @ConcertID INT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        DECLARE @TicketPrice DECIMAL(10, 2);
        DECLARE @ArtistID INT;
        DECLARE @UserWalletID INT;
        DECLARE @ArtistWalletID INT;
        DECLARE @UserBalance DECIMAL(10, 2);

        -- Check if the concert is not canceled
        IF EXISTS (SELECT 1 FROM Concerts WHERE ConcertID = @ConcertID AND IsCancelled = 0)
        BEGIN
            -- Get ticket price and artist ID
            SELECT @TicketPrice = TicketPrice, @ArtistID = ArtistID 
            FROM Concerts 
            WHERE ConcertID = @ConcertID;
            
            -- Get user's wallet ID and balance
            SELECT @UserWalletID = WalletID, @UserBalance = Balance 
            FROM Wallet 
            WHERE UserID = @UserID;
            
            -- Check if the user has sufficient balance
            IF @UserBalance >= @TicketPrice
            BEGIN
                -- Get artist's wallet ID
                SELECT @ArtistWalletID = WalletID 
                FROM Wallet 
                WHERE UserID = @ArtistID;

                -- Insert the ticket into the Tickets table
                INSERT INTO Tickets (UserID, ConcertID, PurchaseDate, IsExpired)
                VALUES (@UserID, @ConcertID, GETDATE(), 0);

                -- Perform the wallet transactions
                -- Withdraw from user's wallet
                UPDATE Wallet
                SET Balance = Balance - @TicketPrice
                WHERE WalletID = @UserWalletID;

                INSERT INTO WalletTransactions (WalletID, Amount, TransactionDate, TransactionType)
                VALUES (@UserWalletID, @TicketPrice, GETDATE(), 'Withdrawal');

                -- Deposit to artist's wallet
                UPDATE Wallet
                SET Balance = Balance + @TicketPrice
                WHERE WalletID = @ArtistWalletID;

                INSERT INTO WalletTransactions (WalletID, Amount, TransactionDate, TransactionType)
                VALUES (@ArtistWalletID, @TicketPrice, GETDATE(), 'Deposit');

                PRINT 'Ticket purchased successfully and wallet transactions completed.';
            END
            ELSE
            BEGIN
                PRINT 'Insufficient balance in user''s wallet.';
            END
        END
        ELSE
        BEGIN
            PRINT 'The concert is canceled.';
        END

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;

CREATE OR ALTER PROCEDURE DeletePlaylist
    @PlaylistID INT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Delete related entries from PlaylistComments table
        DELETE FROM PlaylistComments WHERE PlaylistID = @PlaylistID;

        -- Delete related entries from PlaylistLikes table
        DELETE FROM PlaylistLikes WHERE PlaylistID = @PlaylistID;

        -- Delete related entries from PlaylistSongs table
        DELETE FROM PlaylistSongs WHERE PlaylistID = @PlaylistID;

        -- Delete the entry from Playlists table
        DELETE FROM Playlists WHERE PlaylistID = @PlaylistID;

        COMMIT TRANSACTION;
        PRINT 'Playlist and related entries deleted successfully.';
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
    END CATCH
END;

CREATE PROCEDURE DeleteSong
    @SongID INT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Delete related entries from AlbumSongs table
        DELETE FROM AlbumSongs WHERE SongID = @SongID;

        -- Delete related entries from PlaylistSongs table
        DELETE FROM PlaylistSongs WHERE SongID = @SongID;

        -- Delete related entries from SongComments table
        DELETE FROM SongComments WHERE SongID = @SongID;

        -- Delete related entries from SongLikes table
        DELETE FROM SongLikes WHERE SongID = @SongID;

        -- Delete related entries from ListeningHistory table
        DELETE FROM ListeningHistory WHERE SongID = @SongID;

        -- Delete the entry from Songs table
        DELETE FROM Songs WHERE SongID = @SongID;

        COMMIT TRANSACTION;
        PRINT 'Song and related entries deleted successfully.';
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
    END CATCH
END;

CREATE OR ALTER PROCEDURE DeleteAlbum
    @AlbumID INT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Delete related entries from AlbumSongs table
        DELETE FROM AlbumSongs WHERE AlbumID = @AlbumID;

        -- Delete related entries from AlbumComments table
        DELETE FROM AlbumComments WHERE AlbumID = @AlbumID;

        -- Delete related entries from AlbumLikes table
        DELETE FROM AlbumLikes WHERE AlbumID = @AlbumID;

        -- Delete the entry from Albums table
        DELETE FROM Albums WHERE AlbumID = @AlbumID;

        COMMIT TRANSACTION;
        PRINT 'Album and related entries deleted successfully.';
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
    END CATCH
END;


CREATE OR ALTER FUNCTION SuggestSongs (@UserID INT)
RETURNS @SuggestedSongs TABLE
(
    SongID INT,
    Title VARCHAR(100),
    ArtistID INT,
    ArtistName VARCHAR(50)
)
AS
BEGIN
    -- Insert suggested songs based on similar artists
    INSERT INTO @SuggestedSongs
    SELECT 
        S.SongID,
        S.Title,
        S.ArtistID,
        A.ArtistName
    FROM 
        Songs S
    JOIN 
        Artists A ON S.ArtistID = A.ArtistID
    WHERE 
        S.ArtistID IN 
        (
            SELECT DISTINCT S.ArtistID
            FROM Songs S
            JOIN SongLikes SL ON S.SongID = SL.SongID
            WHERE SL.UserID = @UserID
        )
        AND S.SongID NOT IN 
        (
            SELECT SL.SongID
            FROM SongLikes SL
            WHERE SL.UserID = @UserID
        );

    RETURN;
END;


CREATE  OR ALTER FUNCTION SuggestAlbums (@UserID INT)
RETURNS @SuggestedAlbums TABLE
(
    AlbumID INT,
    AlbumTitle VARCHAR(100),
    ArtistID INT,
    ArtistName VARCHAR(50),
    ReleaseDate DATE
)
AS
BEGIN
    -- Insert suggested albums based on similar artists
    INSERT INTO @SuggestedAlbums
    SELECT 
        A.AlbumID,
        A.Title AS AlbumTitle,
        A.ArtistID,
        AR.ArtistName,
        A.ReleaseDate
    FROM 
        Albums A
    JOIN 
        Artists AR ON A.ArtistID = AR.ArtistID
    WHERE 
        A.ArtistID IN 
        (
            SELECT DISTINCT S.ArtistID
            FROM Songs S
            JOIN SongLikes SL ON S.SongID = SL.SongID
            WHERE SL.UserID = @UserID
        )
        AND A.AlbumID NOT IN 
        (
            SELECT AL.AlbumID
            FROM AlbumLikes AL
            WHERE AL.UserID = @UserID
        );

    RETURN;
END;


CREATE PROCEDURE LikePlaylist
    @UserID INT,
    @PlaylistID INT
AS
BEGIN
    -- Check if the user has already liked the song
    IF NOT EXISTS (SELECT 1 FROM PlaylistLikes WHERE UserID = @UserID AND PlaylistID = @PlaylistID)
    BEGIN
        INSERT INTO PlaylistLikes(UserID, PlaylistID)
        VALUES (@UserID, @PlaylistID);
        
        PRINT 'Playlist liked successfully.';
    END
    ELSE
    BEGIN
        PRINT 'User has already liked this Playlist.';
    END
END;


CREATE PROCEDURE LikeAlbum
    @UserID INT,
    @AlbumID INT
AS
BEGIN
    -- Check if the user has already liked the song
    IF NOT EXISTS (SELECT 1 FROM AlbumLikes WHERE UserID = @UserID AND AlbumID = @AlbumID)
    BEGIN
        INSERT INTO AlbumLikes(UserID, AlbumID)
        VALUES (@UserID, @AlbumID);
        
        PRINT 'Album liked successfully.';
    END
    ELSE
    BEGIN
        PRINT 'User has already liked this Album.';
    END
END;

CREATE OR ALTER PROCEDURE CancelConcert
    @ConcertID INT
AS
BEGIN
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Check if the concert exists and is not already cancelled
        IF EXISTS (SELECT 1 FROM Concerts WHERE ConcertID = @ConcertID AND IsCancelled = 0)
        BEGIN
            -- Get the ticket price for the concert
            DECLARE @TicketPrice DECIMAL(10, 2);
            SELECT @TicketPrice = TicketPrice FROM Concerts WHERE ConcertID = @ConcertID;

            -- Set the concert as cancelled
            UPDATE Concerts
            SET IsCancelled = 1
            WHERE ConcertID = @ConcertID;

            -- Update the status of all tickets for the concert to expired
            UPDATE Tickets
            SET IsExpired = 1
            WHERE ConcertID = @ConcertID;

            -- Refund the ticket price to users' wallets
            UPDATE Wallet
            SET Balance = Balance + @TicketPrice
            WHERE UserID IN (SELECT UserID FROM Tickets WHERE ConcertID = @ConcertID);

            -- Insert deposit transaction records for all affected users
            INSERT INTO WalletTransactions (WalletID, Amount, TransactionDate, TransactionType)
            SELECT WalletID, @TicketPrice, GETDATE(), 'Deposit'
            FROM Wallet
            WHERE UserID IN (SELECT UserID FROM Tickets WHERE ConcertID = @ConcertID);

            COMMIT TRANSACTION;
            PRINT 'Concert cancelled and ticket refunds processed successfully.';
        END
        ELSE
        BEGIN
            PRINT 'Concert not found or already cancelled.';
            ROLLBACK TRANSACTION;
        END
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
    END CATCH
END;
CREATE TABLE Users (
    UserName VARCHAR(50) primary key,
    Password VARCHAR(50) NOT NULL,
    BirthYear INT,
    Email VARCHAR(100) NOT NULL,
    Location VARCHAR(100),
	profit int default 20,
    SubscriptionStatus BIT NOT NULL DEFAULT 0
);
CREATE TABLE Artists (
    ArtistID INT PRIMARY KEY IDENTITY(1,1),
    ArtistName VARCHAR(50) NOT NULL,
	Password VARCHAR(50) NOT NULL,
);

drop table users


INSERT INTO Users (UserName, Password, BirthYear, Email, Location)
VALUES 
('john_doe', 'password123', 1990, 'john@example.com', 'New York, USA'),
('jane_smith', 'password456', 1985, 'jane@example.com', 'Los Angeles, USA'),
('mike_jones', 'password789', 1995, 'mike@example.com', 'Chicago, USA');
INSERT INTO Artists (ArtistName, Password)
VALUES 
('The_Beatles', 'a123'),
('Taylor_Swift', 'a456'),
('Ed_Sheeran', 'a789');


CREATE PROCEDURE InsertUser
    @UserName VARCHAR(50),
    @Password VARCHAR(50),
    @BirthYear INT,
    @Email VARCHAR(100),
    @Location VARCHAR(100),
    @SubscriptionStatus BIT
AS
BEGIN
    INSERT INTO Users (UserName, Password, BirthYear, Email, Location)
    VALUES (@UserName, @Password, @BirthYear, @Email, @Location);
END;


CREATE PROCEDURE UpdateUser
    @UserID INT,
    @UserName VARCHAR(50),
    @Password VARCHAR(50),
    @BirthYear INT,
    @Email VARCHAR(100),
    @Location VARCHAR(100),
    @SubscriptionStatus BIT
AS
BEGIN
    UPDATE Users
    SET UserName = @UserName,
        Password = @Password,
        BirthYear = @BirthYear,
        Email = @Email,
        Location = @Location,
        SubscriptionStatus = @SubscriptionStatus
    WHERE UserID = @UserID;
END;


CREATE PROCEDURE DeleteUser
    @UserID INT
AS
BEGIN
    DELETE FROM Users
    WHERE UserID = @UserID;
END;



select * from Users
select * from Artists


-- STOP ALL INSTANCES OF THE SERVERSIDE BACKEND 
-- BEFORE APPLYING THIS SQL TO THE DATABASE.

DROP TABLE IF EXISTS userpictures;
DROP TABLE IF EXISTS userfriends;
DROP TABLE IF EXISTS userfriendrequests;
DROP TABLE IF EXISTS usertags;
DROP TABLE IF EXISTS reportedusers;
DROP TABLE IF EXISTS eventsusers;
DROP TABLE IF EXISTS reportedevents;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;

CREATE TABLE `users` (
  `User_ID` int NOT NULL AUTO_INCREMENT,
  `Email` varchar(255) NOT NULL,
  `First_Name` char(60) NOT NULL,
  `Last_Name` char(60) NOT NULL,
  `DateOfBirth` date NOT NULL,
  `Password` varchar(64) NOT NULL,
  `Twitter_Link` varchar(255) DEFAULT NULL,
  `Instagram_Link` varchar(255) DEFAULT NULL,
  `Spotify_Link` varchar(255) DEFAULT NULL,
  `LinkedIn_Link` varchar(255) DEFAULT NULL,
  `Description` mediumtext DEFAULT NULL,
  `Verification_Code` varchar(6) DEFAULT NULL,
  `User_Verified` boolean NOT NULL DEFAULT FALSE,
  `Password_Code` varchar(6) DEFAULT NULL,
  `Password_Changed` boolean NOT NULL DEFAULT FALSE,
  `User_Created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Last_Login` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`User_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `userpictures` (
  `Picture_ID` int NOT NULL AUTO_INCREMENT,
  `User_ID` int NOT NULL,
  `Picture_Path` varchar(255) NOT NULL,
  PRIMARY KEY (`Picture_ID`),
  FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `userfriends` (
  `User_ID` int NOT NULL,
  `Friend_ID` int NOT NULL,
  PRIMARY KEY (`User_ID`, `Friend_ID`),
  CONSTRAINT fk_user_id FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE,
  CONSTRAINT fk_friend_id FOREIGN KEY (`Friend_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE
  -- UNIQUE `Unique_Friendships` (`User_ID`, `Friend_ID`),
  -- INDEX `User_ID` (`User_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `userfriendrequests` (
  `Reciever_ID` int NOT NULL,
  `Sender_ID` int NOT NULL,
  PRIMARY KEY (`Reciever_ID`, `Sender_ID`),
  CONSTRAINT fk_reciever_id FOREIGN KEY (`Reciever_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE,
  CONSTRAINT fk_sender_id FOREIGN KEY (`Sender_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE
  -- UNIQUE `Unique_Friendships` (`User_ID`, `Friend_ID`),
  -- INDEX `User_ID` (`User_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `usertags` (
  `User_ID` int NOT NULL,
  `User_Tag` varchar(255) NOT NULL,
  PRIMARY KEY (`User_ID`, `User_Tag`),
  FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `events` (
  `Event_ID` int NOT NULL AUTO_INCREMENT,
  `User_ID` int NOT NULL,
  `Name` varchar(30) NOT NULL,
  `Description` text DEFAULT NULL,
  `Picture_Path` varchar(255) DEFAULT NULL,
  `DateTime` datetime NOT NULL,
  `Location` varchar(255) NOT NULL,
  `Event_Created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Event_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `eventsusers` (
  `Event_ID` int NOT NULL,
  `User_ID` int NOT NULL,
  PRIMARY KEY (`Event_ID`, `User_ID`),
  FOREIGN KEY (`Event_ID`) REFERENCES `events` (`Event_ID`) ON DELETE CASCADE,
  FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `reportedusers` (
  `Report_ID` int NOT NULL AUTO_INCREMENT,
  `Reporting_User_ID` int NOT NULL,
  `Reported_User_ID` int NOT NULL,
  `Report_Reason` varchar(255) NOT NULL,
  PRIMARY KEY (`Report_ID`),
  FOREIGN KEY (`Reporting_User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE,
  FOREIGN KEY (`Reported_User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `reportedevents` (
  `Report_ID` int NOT NULL AUTO_INCREMENT,
  `Reporting_User_ID` int NOT NULL,
  `Reported_Event_ID` int NOT NULL,
  `Report_Reason` varchar(255) NOT NULL,
  PRIMARY KEY (`Report_ID`),
  FOREIGN KEY (`Reporting_User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE,
  FOREIGN KEY (`Reported_Event_ID`) REFERENCES `events` (`Event_ID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


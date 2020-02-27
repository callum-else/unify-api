CREATE TABLE `users` (
  `User_ID` varchar(255) NOT NULL,
  `Email` varchar(255) NOT NULL,
  `First_Name` char(60) NOT NULL,
  `Last_Name` char(60) NOT NULL,
  `DateOfBirth` date NOT NULL,
  `Password` varchar(64) NOT NULL,
  `Profile_Picture` varchar(60) DEFAULT NULL,
  `Twitter_Link` varchar(255) DEFAULT NULL,
  `Instagram_Link` varchar(255) DEFAULT NULL,
  `Description` mediumtext DEFAULT NULL,
  `User_Created` datetime NOT NULL,
  `Last_Login` datetime NOT NULL,
  PRIMARY KEY (`User_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `userfriends` (
  `User_ID` varchar(255) NOT NULL,
  `Friend_ID` varchar(255) NOT NULL,
  PRIMARY KEY (`User_ID`, `Friend_ID`),
  FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`),
  FOREIGN KEY (`Friend_ID`) REFERENCES `users` (`User_ID`),
  UNIQUE `Unique_Friendships` (`User_ID`, `Friend_ID`),
  INDEX `User_ID` (`User_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `usermessages` (
  `User_ID` varchar(255) NOT NULL,
  `Recipient_ID` varchar(255) NOT NULL,
  `Message_ID` varchar(255) NOT NULL,
  `Message` text NOT NULL,
  `Sent_DateTime` datetime NOT NULL,
  PRIMARY KEY (`Message_ID`),
  FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`),
  FOREIGN KEY (`Recipient_ID`) REFERENCES `users` (`User_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `usertags` (
  `User_ID` varchar(255) NOT NULL,
  `User_Tag` varchar(255) NOT NULL,
  PRIMARY KEY (`User_ID`, `User_Tag`),
  FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `events` (
  `Event_ID` varchar(255) NOT NULL,
  `User_ID` varchar(255) NOT NULL,
  `Name` varchar(30) NOT NULL,
  `Description` text NOT NULL,
  `DateTime` datetime NOT NULL,
  `Location_Longitude` decimal(9,0) NOT NULL,
  `Location_Latitude` decimal(10,0) NOT NULL,
  PRIMARY KEY (`Event_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `eventsusers` (
  `Event_ID` varchar(255) NOT NULL,
  `User_ID` varchar(255) NOT NULL,
  PRIMARY KEY (`Event_ID`, `User_ID`),
  FOREIGN KEY (`Event_ID`) REFERENCES `events` (`Event_ID`),
  FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `users` (
  `User_ID` int NOT NULL AUTO_INCREMENT,
  `Email` varchar(255) NOT NULL,
  `First_Name` char(60) NOT NULL,
  `Last_Name` char(60) NOT NULL,
  `DateOfBirth` date NOT NULL,
  `Password` varchar(64) NOT NULL,
  `Twitter_Link` varchar(255) DEFAULT NULL,
  `Instagram_Link` varchar(255) DEFAULT NULL,
  `Description` mediumtext DEFAULT NULL,
  `Verification_Code` varchar(6) DEFAULT NULL,
  `User_Verified` boolean NOT NULL DEFAULT FALSE,
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
  FOREIGN KEY (`User_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE,
  FOREIGN KEY (`Friend_ID`) REFERENCES `users` (`User_ID`) ON DELETE CASCADE,
  UNIQUE `Unique_Friendships` (`User_ID`, `Friend_ID`),
  INDEX `User_ID` (`User_ID`)
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
  `Description` text NOT NULL,
  `Event_Picture` varchar(255) DEFAULT NULL,
  `DateTime` datetime NOT NULL,
  `Event_Location` varchar(255) NOT NULL,
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


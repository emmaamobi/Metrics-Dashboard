# This file creates the tables necessary for data collection as well as all of the columns needed to do so
# This file starts all of the data collection files and insertes the data into the database where it needs to go

# 3: Start collecting data

from datetime import datetime, timedelta
from sqlite3 import Connection, Cursor

from libs import *


class DataCollection:
    def __init__(
        self,
        oauthToken: str,
        outfile: str,
        repository: str,
        username: str,
    ) -> None:
        self.file = outfile
        self.repository = repository
        self.token = oauthToken
        self.username = username

        self.dbConnector = DatabaseConnector(databaseFileName=outfile)

    def checkForFile(self) -> Connection:
        self.dbConnector.createDatabase()
        return self.dbConnector.openDatabaseConnection()

    def createFileTablesColumns(self, dbConnection: Connection) -> bool:
        commitsSQL = "CREATE TABLE Commits (SHA TEXT, Date TEXT, Author TEXT, Message TEXT, Comment Count INTEGER, Tree_URL TEXT, PRIMARY KEY(SHA));"

        issuesSQL = "CREATE TABLE Issues (ID TEXT, Count TEXT, Title TEXT, Author TEXT, Assignees TEXT, Labels TEXT, Description TEXT, Created At TEXT, Updated At TEXT, Closed At TEXT, PRIMARY KEY(ID));"

        self.dbConnector.executeSQL(
            sql=commitsSQL, databaseConnection=dbConnection, commit=True
        )
        self.dbConnector.executeSQL(
            sql=issuesSQL, databaseConnection=dbConnection, commit=True
        )

    def startDataCollection(self) -> None:
        pass


dc = DataCollection(
    oauthToken=10,
    outfile="dicks.db",
    repository="temp",
    repositoryURL="temp",
    username="temp",
)

t = dc.checkForFile()

dc.createFileTablesColumns(t)
import MySQLdb
import ScrumblesObjects
import re

class DataBaseLoginInfo:
    #todo def __init__(self,file) Load login info from an encrypted file
    pass

class Query:
    getAllUsers = 'SELECT * FROM UserTable'
    getAllSprints = 'SELECT * FROM SprintTable'
    getAllCards = 'SELECT * FROM CardTable'
    getAllComments = 'SELECT * FROM CommentTable'
    @staticmethod
    def getUserIdByUsernameAndPassword(username, password):
        query = 'SELECT * from UserTable WHERE (BINARY UserName=\'%s\') AND (BINARY UserPassword=\'%s\')' % (
        username, password)
        return query

    @staticmethod
    def assignCardToSprint(item,sprint):
        assert item.itemID is not None
        assert sprint.sprintID is not None
        query = 'UPDATE CardTable SET CardDueDate = ( ' \
                'SELECT DueDate FROM SprintTable WHERE SprintID=%i), ' \
                'SprintID = %i, Status=1 WHERE CardID = %i' % (sprint.sprintID,
                                                     sprint.sprintID,
                                                     item.itemID)
        return query

    @staticmethod
    def createObject(obj):
        query = ''
        if type(obj) == ScrumblesObjects.User:
            query = UserQuery.createUser(obj)
        elif type(obj) == ScrumblesObjects.Sprint:
            query = SprintQuery.createSprint(obj)
        elif type(obj) == ScrumblesObjects.Item:
            query = CardQuery.createCard(obj)
        elif type(obj) == ScrumblesObjects.Comment:
            query = CommentQuery.createComment(obj)
        else:
            raise Exception('Invalid Object Type')
        return query

    @staticmethod
    def deleteObject(obj):
        query = ''
        if type(obj) == ScrumblesObjects.User:
            query = UserQuery.deleteUser(obj)
        elif type(obj) == ScrumblesObjects.Comment:
            query = CommentQuery.deleteComment(obj)
        elif type(obj) == ScrumblesObjects.Sprint:
            query = SprintQuery.deleteSprint(obj)
        elif type(obj) == ScrumblesObjects.Item:
            query = CardQuery.deleteCard(obj)
        else:
            raise Exception('Invalid Object Type')
        return query

    @staticmethod
    def updateObject(obj):
        query = ''
        if type(obj) == ScrumblesObjects.User:
            query = UserQuery.updateUser(obj)
        elif type(obj) == ScrumblesObjects.Comment:
            query = CommentQuery.updateComment(obj)
        elif type(obj) == ScrumblesObjects.Sprint:
            query = SprintQuery.updateSprint(obj)
        elif type(obj) == ScrumblesObjects.Item:
            query = CardQuery.updateCard(obj)
        else:
            raise Exception('Invalid Object Type')
        return query

class SprintQuery(Query):
    @staticmethod
    def createSprint(sprint):
        assert sprint.sprintName is not None
        query = 'INSERT INTO SprintTable (StartDate,DueDate,SprintName) VALUES (\'%s\',\'%s\',\'%s\')' % (
            str(sprint.sprintStartDate), str(sprint.sprintDueDate), sprint.sprintName)
        return query

    @staticmethod
    def updateSprint(sprint):
        assert sprint is not None
        assert sprint.sprintID is not None

        query = 'UPDATE SprintTable SET StartDate=%s,' \
                'DueDate=\'%s\', SprintName=\'%s\' WHERE SprintID=%i'%(
            sprint.sprintStartDate,
            sprint.sprintDueDate,
            sprint.sprintName,
            sprint.sprintID
        )
        return query

    @staticmethod
    def getSprintBySprintID(sprintID):
        assert sprintID is not None
        query = 'SELECT * FROM SprintTable WHERE SprintID=%i' % (sprintID)
        return query

    @staticmethod
    def deleteSprint(sprint):
        assert sprint is not None
        query = 'DELETE FROM SprintTable WHERE SprintID=%i' % (sprint.sprintID)
        return query

class CardQuery(Query):
    @staticmethod
    def createCard(item):
        assert item is not None
        assert item.itemType is not None
        assert item.itemTitle is not None
        assert item.itemDescription is not None
        query = 'INSERT INTO CardTable (' \
                'CardType,' \
                'CardPriority,' \
                'CardTitle,' \
                'CardDescription,' \
                'CardCreatedDate,' \
                'Status) VALUES (' \
                '\'%s\',0,\'%s\',\'%s\',' \
                'NOW(),0)' % (
            item.itemType,
            item.itemTitle,
            item.itemDescription
        )
        return query

    @staticmethod
    def updateCard(item):
        assert item is not None
        assert item.itemID is not None
        query = 'UPDATE CardTable SET ' \
                'CardType=\'%s\',' \
                'CardPriority=%i,' \
                'CardTitle=\'%s\',' \
                'CardDescription=\'%s\',' \
                'CardDueDate=\'%s\',' \
                'CardCodeLink=\'%s\',' \
                'SprintID=%i,' \
                'UserID=%i,' \
                'Status=%i WHERE CardID=%i'% (
            item.itemType,
            item.itemPriority,
            item.itemTitle,
            item.itemDescription,
            item.itemDueDate,
            item.itemCodeLink,
            item.itemSprintID,
            item.itemUserID,
            item.itemStatus,
            item.itemID
        )
        return query

    @staticmethod
    def getCardByCardID(cardID):
        query = 'SELECT * from CardTable WHERE CardID=%i' % (cardID)
        return query

    @staticmethod
    def getCardByCardTitle(cardTitle):
        query = 'SELECT * FROM CardTable WHERE CardTitle=\'%s\'' % (cardTitle)
        return query

    @staticmethod
    def getCardsBySprint(sprint):
        assert sprint is not None
        assert sprint.sprintID is not None
        query = 'SELECT * FROM CardTable WHERE SprintID=%i' % (sprint.sprintID)
        return query

    @staticmethod
    def deleteCard(item):
        assert item is not None
        query = 'DELETE FROM CardTable WHERE CardID=%i' % (item.itemID)
        return query

class UserQuery(Query):
    @staticmethod
    def getUserByUsername(username):
        query = 'SELECT * from UserTable WHERE UserName=\'%s\'' % (username)
        return query

    @staticmethod
    def createUser(user):
        ObjectValidator.validate(user)
        password = Password(user.userPassword)

        query = 'INSERT INTO UserTable (userName,UserEmailAddress,UserPassword,UserRole) VALUES (\'%s\',\'%s\',\'%s\',\'%s\')' % (
            user.userName, user.userEmailAddress, str(password), user.userRole)
        return query

    @staticmethod
    def updateUser(user):
        assert user is not None
        assert user.userID is not None
        query = 'UPDATE UserTable SET ' \
                'UserName=\'%s\',' \
                'UserEmailAddress=\'%s\',' \
                'UserPassword=\'%s\',' \
                'UserRole=\'%s\' WHERE ' \
                'UserID=%i' % (
            user.userName,
            user.userEmailAddress,
            user.userPassword,
            user.userRole,
            user.userID
        )
        return query

    @staticmethod
    def deleteUser(user):
        assert user is not None
        query = 'DELETE FROM UserTable WHERE UserID=%i' % (user.userID)
        return query

class CommentQuery(Query):
    def createComment(comment):
        assert comment is not None
        assert comment.commentContent is not None
        assert comment.commentItemID is not None
        assert comment.commentUserID is not None
        query = 'INSERT INTO CommentTable (CommentTimeStamp,' \
                'CommentContent,' \
                'CardID,' \
                'UserID) VALUES ( NOW(), \'%s\',%i,%i)' % (
                    comment.commentContent,
                    comment.commentItemID,
                    comment.commentUserID
                )
        return query

    def updateComment(comment):
        assert comment is not None
        assert comment.commentID is not None
        query = 'UPDATE CommentTable SET ' \
                'CommentContent=\'%s\' WHERE' \
                'CommentID=%i' % (
            comment.commentContent,
            comment.commentID
        )
        return query

    def getCommentsByUser(user):
        assert user is not None
        assert user.userID is not None
        query = 'SELECT * FROM CommentTable WHERE UserID=%i' % (user.userID)
        return query

    def getCommentsByItem(item):
        assert item is not None
        assert item.itemID is not None
        query = 'SELECT * FROM CommentTable WHERE CardID=%i' % (item.itemID)
        return query

    def deleteComment(comment):
        assert comment is not None
        query = 'DELETE FROM CommentTable WHERE CommentID=%i' % (comment.commentID)
        return query

class ScrumblesData:
    def __init__(self, dbLoginInfo):
        self.ipaddress = dbLoginInfo.ipaddress
        self.userID = dbLoginInfo.userID
        self.password = dbLoginInfo.password
        self.defaultDB = dbLoginInfo.defaultDB
        self.dbConnection = None
        #This connect and close will check if the network is good
        #an excpetion will be thrown if unable to connect to server
        self.connect()
        self.close()
    def connect(self):
        self.dbConnection = MySQLdb.connect(self.ipaddress,self.userID,self.password,self.defaultDB)
		
    def getData(self,query):
        assert self.dbConnection is not None
        self.dbConnection.query(query)
        queryResult = self.dbConnection.store_result()
        maxRows = 0
        how = 1
        return queryResult.fetch_row(maxRows,how)
		
    def setData(self,query):
        assert self.dbConnection is not None
        self.dbConnection.query(query)
        self.dbConnection.commit()
	
    def close(self):
        assert self.dbConnection is not None
        self.dbConnection.close()

    def isConnected(self):
        return self.dbConnection.open == 1

class Password:
    password = None

    def __init__(self,password):
        self.password = password
    def __str__(self):
        return self.password

    def doesPasswordMeetComplexityRequirement(self):
        #must be 8 digits, 1 uppercase, 1 lowercase, and 1 digit
        if self.password == '':
            raise Exception('Password must not be blank')
        isLong = len(self.password) >= 8
        isNotAllLowercase = self.password.lower() != self.password
        isNotAllUppercase = self.password.upper() != self.password
        hasANumber = False
        for char in self.password:
            if char.isdigit():
                hasANumber = True

        goodPassword = isLong and isNotAllLowercase and isNotAllUppercase and hasANumber
        if not goodPassword:
            raise Exception('Password must be 8 digits long and contain at least 1 upper case, 1 lowercase and 1 number')


    def encrypt(self):
        #todo create function that will actually encrypt self.password
        pass
    def decrypt(self):
        #todo create function that will decrypt self.password
        pass
    __repr__ = __str__

class ObjectValidator:
    @staticmethod
    def validate(obj):
        if type(obj) == ScrumblesObjects.User:
            ObjectValidator.validateUser(obj)

    @staticmethod
    def validateUser(user):

        if len(user.userName) < 5:
            raise Exception('User Name too Short')
        if ' ' in user.userName:
            raise Exception('User Name must not contain spaces')

        validEmail  = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
        if re.search(validEmail,user.userEmailAddress) is None:
            raise Exception('Invalid Email address')

        password = Password(user.userPassword)
        password.doesPasswordMeetComplexityRequirement()

        userRoles = ('Admin', 'Scrum Master', 'Developer')
        if user.userRole not in userRoles:
            raise Exception('Invalid User Role')


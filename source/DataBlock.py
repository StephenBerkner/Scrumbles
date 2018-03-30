from ScrumblesData import DataBaseLoginInfo, ScrumblesData, debug_ObjectdumpList
from Query import *
import ScrumblesObjects, remoteUpdate
import logging, threading, time

def dbWrap(func):
    def wrapper(self,*args):
        self.conn.connect()
        func(self,*args)
        self.conn.close()
    return wrapper

class DataBlock:
    users = []
    items = []
    projects = []
    comments = []
    tags = []
    sprints = []
    updaterCallbacks = []


    def __init__(self):
        logging.info('Initializing DataBlock Object')
        self.alive = True
        self.dbLogin = DataBaseLoginInfo('login.txt')
        self.conn = ScrumblesData(self.dbLogin)
        self.listener = remoteUpdate.RemoteUpdate()
        self.lock = threading.Lock()
        self.updateAllObjects()
        self.size = self.getLen()
        self.updaterThread = threading.Thread(target = self.updater, args=())
        self.cv = threading.Condition()

        self.updaterThread.start()

    def __del__(self):
        self.shutdown()
        del self.listener

    def getLen(self):
        rv = len(self.items)
        return rv

    def debugDump(self):
        print('\nDumping Projects')
        debug_ObjectdumpList(self.projects)
        for P in self.projects:
            print('Dumping lists in ', P.projectName)
            print('Dumping assgined Users')
            debug_ObjectdumpList(P.listOfAssignedUsers)
            print('Dumping assinged Sprints')
            debug_ObjectdumpList(P.listOfAssignedSprints)
            print('Dumping assigned Items')
            debug_ObjectdumpList(P.listOfAssignedItems)
        print('\nDumping Sprints')
        debug_ObjectdumpList(self.sprints)
        for S in self.sprints:
            print('Dumping lists in ', S.sprintName)
            print('Dumping assigned Items')
            debug_ObjectdumpList(S.listOfAssignedItems)
            print('Dumping assigned Users')
            debug_ObjectdumpList(S.listOfAssignedUsers)
        print('\nDumping Users')
        debug_ObjectdumpList(self.users)
        for U in self.users:
            print('Dumping lists in ', U.userName)
            print('Dumping assigned items')
            debug_ObjectdumpList(U.listOfAssignedItems)
            print('Dumping comments')
            debug_ObjectdumpList(U.listOfComments)
            print('Dumping in projects')
            debug_ObjectdumpList(U.listOfProjects)
        print('\nDumping Items')
        debug_ObjectdumpList(self.items)
        for I in self.items:
            print('Dumping comments on item',I.itemTitle)
        print('\nDumping Comments')
        debug_ObjectdumpList(self.comments)




    def updateAllObjects(self):
        self.conn.connect()
        self.users.clear()
        self.items.clear()
        self.projects.clear()
        self.comments.clear()
        self.tags.clear()
        self.sprints.clear()
        userTable = self.conn.getData(Query.getAllUsers)
        itemTable = self.conn.getData(Query.getAllCards)
        projectTable = self.conn.getData(Query.getAllProjects)
        commentTable = self.conn.getData(Query.getAllComments)
        sprintTable = self.conn.getData(Query.getAllSprints)
        userToProjectRelationTable = self.conn.getData(Query.getAllUserProject)
        itemToProjectRelationTable = self.conn.getData(Query.getAllProjectItem)
        self.conn.close()
        for comment in commentTable:
            Comment = ScrumblesObjects.Comment(comment)
            self.comments.append(Comment)

        for item in itemTable:
            Item = ScrumblesObjects.Item(item)
            Item.listOfComments = [C for C in self.comments if C.commentItemID == Item.itemID]
            self.items.append(Item)


        for user in userTable:
            User = ScrumblesObjects.User(user)
            User.listOfAssignedItems = [ I for I in self.items if I.itemUserID == User.userID ]
            User.listOfComments = [ C for C in self.comments if C.commentUserID == User.userID ]
            self.users.append(User)

        for sprint in sprintTable:
            Sprint = ScrumblesObjects.Sprint(sprint)
            Sprint.listOfAssignedItems = [I for I in self.items if I.itemSprintID == Sprint.sprintID]
            Sprint.listOfAssignedUsers = [U for U in self.users if U.userID in [I.itemUserID for I in Sprint.listOfAssignedItems]]
            self.sprints.append(Sprint)

        for project in projectTable:
            Project = ScrumblesObjects.Project(project)
            Project.listOfAssignedSprints = [S for S in self.sprints if S.projectID == Project.projectID]
            self.projects.append(Project)



        for user in self.users:
            for dict in userToProjectRelationTable:
                if dict['UserID'] == user.userID:
                    for project in self.projects:
                        if dict['ProjectID'] == project.projectID:
                            user.listOfProjects.append(project)

        for project in self.projects:
            for dict in userToProjectRelationTable:
                if dict['ProjectID'] == project.projectID:
                    for user in self.users:
                        if dict['UserID'] == user.userID:
                            project.listOfAssignedUsers.append(user)

            for dict in itemToProjectRelationTable:
                if dict['ProjectID'] == project.projectID:
                    for item in self.items:
                        if dict['ItemID'] == item.itemID:
                            item.projectID = project.projectID

                            project.listOfAssignedItems.append(item)


        #self.debugDump()
        return True

    def validateData(self):
        return self.getLen() > 0

    @dbWrap
    def addUserToProject(self,project,user):
        logging.info('Adding User %s to project %s' % (user.UserName,project.projectName))
        if user not in project.listOfAssignedUsers:
            self.conn.setData(ProjectQuery.addUser(project,user))
        else:
            print('User already assigned to project')

    @dbWrap
    def removeUserFromProject(self,project,user):
        logging.info('Removing User %s from project %s' %(user.UserName,project.projectName) )
        for item in self.items:
            if item in project.listOfAssignedItems:
                if item.itemUserID == user.userID:
                    item.itemUserID = 0

            self.conn.setData(Query.updateObject(item))

        self.conn.setData(ProjectQuery.removeUser(project,user))


    ##### DUPLICATE CODE TODO Remove below and change callers to addNewScrumblesObject
    @dbWrap
    def addComment(self,comment):
        logging.warning('Depreciated function call: Adding Comment to database: %s' % comment.commentContent)
        self.conn.setData(Query.createObject(comment))


    @dbWrap
    def assignUserToItem(self,user,item):
        logging.info('Assigning User %s to item %s.'%(user.userName,item.itemTitle))
        item.itemUserID = user.userID
        item.itemStatus = 1
        self.conn.setData(Query.updateObject(item))
    @dbWrap
    def addItemToProject(self,project,item):
        logging.info('Adding item %s to project %s.' %(item.itemTitle,project.projectName))
        if item not in project.listOfAssignedItems:
            item.projectID = project.projectID
            self.conn.setData(ProjectQuery.addItem(project,item))
        else:
            print('Item already assigned to project')
    @dbWrap
    def removeItemFromProject(self,project,item):
        logging.info('Removing item %s from project %s.' % (item.itemTitle,project.projectName))
        item.projectID = 0
        self.conn.setData(ProjectQuery.removeItem(project,item))

    @dbWrap
    def addNewScrumblesObject(self,obj):
        logging.info('Adding new object %s to database' % repr(obj))
        self.conn.setData(Query.createObject(obj))

    @dbWrap
    def updateScrumblesObject(self,obj):
        logging.info('Updating object %s to database' % repr(obj))
        self.conn.setData(Query.updateObject(obj))

    @dbWrap
    def deleteScrumblesObject(self,obj):
        logging.info('Deleting object %s from database' % repr(obj))
        self.conn.setData(Query.deleteObject(obj))

    @dbWrap
    def modifiyItemPriority(self,item,priority):
        logging.info('Modifying item %s priority to %s' % (item.itemTitle,item.priorityEquivalents[priority]))
        assert priority in range(1,3)
        item.itemPriority = priority
        self.conn.setData(Query.updateObject(item))

    @dbWrap
    def modifyItemStatus(self,item,status):
        logging.info('Modifying item %s status to %s' % (item.itemTitle,item.statusEquivalents[status]))
        assert status in range(0,4)
        item.itemStatus = status
        self.conn.setData(Query.updateObject(item))

    @dbWrap
    def modifyItemStatusByString(self,item,status):
        logging.info('Modifying item %s to status %s.' % (item.itemTitle,status))
        item.itemStatus = item.statusEquivalentsReverse[status]
        self.conn.setData(Query.updateObject(item))

    @dbWrap
    def assignItemToSprint(self,item,sprint):
        logging.info('Assigning Item %s to Sprint %s.',(item.itemTitle,sprint.sprintName))
        item.itemSprintID = sprint.sprintID
        self.conn.setData(Query.updateObject(item))

    @dbWrap
    def removeItemFromSprint(self,item):
        logging.info('Removing Item %s from sprint %d.'%(item.itemTitle,item.itemSprintID))
        item.itemSprintID = 0
        self.conn.setData(Query.updateObject(item))




    def updater(self):
        logging.info('Updater Thread %s started' % threading.get_ident())
        threading.Thread(target=self.listener.start,args=()).start()

        while self.alive:
            time.sleep(2)
            if self.listener.isDBChanged:
                time.sleep(2)
                with self.cv:
                    self.cv.wait_for(self.updateAllObjects)

                    self.executeUpdaterCallbacks()
                    self.listener.isDBChanged = False


    def packCallback(self,callback):
        logging.info('Packing Callback %s' % str(callback))
        self.updaterCallbacks.append(callback)

    def executeUpdaterCallbacks(self):
        if len(self.updaterCallbacks) > 0:
            for func in self.updaterCallbacks:
                logging.info('Thread %s Executing Updater Func %s' % ( threading.get_ident(), str(func) ) )
                func()

    def shutdown(self):
        logging.info('Shutting down Thread %s'%threading.get_ident())
        self.alive = False
        self.listener.stop()

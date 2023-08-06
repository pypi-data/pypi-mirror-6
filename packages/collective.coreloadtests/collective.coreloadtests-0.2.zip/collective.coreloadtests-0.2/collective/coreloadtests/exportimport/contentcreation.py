from Products.CMFCore.utils import getToolByName

def setupUsers(context):
    """
    Add users for content create test scenario
    """    
    if not context.readDataFile('users_list.txt'):
        return 
       
    portal = context.getSite()
    user_list = context.readDataFile('users_list.txt')    
    users = user_list.split('\n')
    reg_tool = getToolByName(portal,'portal_registration')    
    for username in users:
        reg_tool.addMember(username, 'testpw', properties={'email':username + '@test.plone.org','fullname':username, 'username':username})

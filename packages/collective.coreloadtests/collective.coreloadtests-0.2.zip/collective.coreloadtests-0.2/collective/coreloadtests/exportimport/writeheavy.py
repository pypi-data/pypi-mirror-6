from plone.app.controlpanel.security import ISecuritySchema

def configureSecurity(context):
    """
    Setup portal security for heavy write test scenario
    """
    if not context.readDataFile('configure_security.txt'):
        return
    
    portal = context.getSite()
    security = ISecuritySchema(portal)
    
    #set anonymous registration
    security.set_enable_self_reg(True)
    
    #set email validation
    security.set_enable_user_pwd_choice(True)
    
    #set member area creation flag
    security.set_enable_user_folders(True)

    security.allow_anon_views_about = True

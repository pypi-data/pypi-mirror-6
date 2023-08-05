Introduction
============

The One Time Token PAS allows users to login using a special token. The token
is generated and can only be used one. This allows members to login without
supplying their username and password. You can send an e-mail with the special
login url, so the member can access the portal easily.


Installation
============

This product is written for Plone 2.5 but can easily be used for 3.x.

- Install thru the quick installer

- Activate Authentication and Extraction in the OTT plugin, move this plug-in 
  to the top.


Usage
=====

1. Generate a token::

    tokenTool = getToolByName(self, 'onetimetoken_storage')

    token = tokenTool.setToken(userId)

    'http://myplone/@@do_some_nice_stuff?token=%s' % token = token

2. Send url with logincode to user

The user can use the token only once and it's valid for three weeks. The expiration time
can be set in the tool.


Or you can generate temporary user and delete it later::

    tokenTool = getToolByName(self, 'onetimetoken_storage')

    # get token and create temporary user
    token = tokenTool.setToken()


    # user uses token to do some nice stuff
    'http://myplone/@@do_some_nice_stuff?token=%s' % token = token

    # inside that view
    userid = self.verifyToken(token)

    # do some stuff with user (login, get some girls, etc)
    # ...

    # delete temporary user
    tokenTool.deleteTemporaryUser(userid)
    

Manager's usage
===============

Users with Manage portal permission on Plone site root are allowed to login as
any other user by visiting @@login_as browser view and entering target user
name. This feature has been taken from niteoweb.loginas package and modified.

Safety
======

Why not let users login themselves instead of using this plug-in? In specific 
cases it's usefull to auto-login the user. For example; a member participates in a
program to save energy and keep track of his energy usage. Every month he receives
an email to auto-login and updates his usage. Another example; a portal is used 
for informing members of newly published newsletters, these letters aren't public. 
The member get's a link with auto-login to the newsletter so he can read it.

It's all about making it easier for the user and there's no obstacle to login. In 
above cases the members are normal users with no elevated rights. Ofcourse there
could be cases where a one time token is not usefull and/or safe.

The logincode that is included in the url contains the loginname and the token in 
base64. Every token is a uniquely generated md5 hash of random data and can only be used once. 
If there's is a succesfull match between the given username, token and the stored token 
with username you're authenticated. 

Clearing old tokens
===================
Old tokens can be cleared bij calling clearExpired on the token storage. Using crontick 
and cron4plone this job can be automated.

Add this call in cron4plone: portal/onetimetoken_storage/clearExpired

Todo
====

- Some doc or unit tests would be nice
- Control panel for setting expriation time.
- Checking a member is disabled when generating a token. This is because we had 
  performance problems with generating large amounts of keys (> 15,000) and SQL PAS. 
  Add this as an option in the control panel.

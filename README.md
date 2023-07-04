# InfrastructureSVG


------------------------------------------------------------------------------------------------------------------------

General:
========

Create requirements.txt:
----------------------------
- pip freeze > requirements.txt


Install requirements.txt:
----------------------------
- pip install -r requirements.txt


Uninstall requirements.txt:
----------------------------
- pip uninstall -r requirements.txt -y


Upgrade pip:
------------
- pip install pip --upgrade


Create wheel:
-------------
install .whl:
- pip install wheel

create .whl: 
- python setup.py sdist bdist_wheel (the file will be under dist - 2 file)

load .whl: 
- pip install http:path_to_file_name/wheel_file_name.whl
- pip install http://asil-dashboard/Repository/Automation_Infrastructure-2.0.59-py2.py3-none-any.whl

remove .whl:
- pip uninstall Automation_Infrastructure


General wheel install/uninstall:
---------------------------
jira (version 3.0.0):
- pip install git+git://github.com/pycontribs/jira.git@7fa3a454c08a14e2d7d7670fcfa87482e16936ba

Automation_Infrastructure:
- pip install http://asil-dashboard/Repository/Automation_Infrastructure-2.0.59-py2.py3-none-any.whl
- pip uninstall Automation_Infrastructure

RobotFrameworkSVGInfra:
- pip install http://asil-dashboard/Repository/RobotFrameworkSVGInfra-1.1.1-py3-none-any.whl
- pip uninstall RobotFrameworkSVGInfra

SwEngineTime:
- pip install http://asil-dashboard/Repository/SwEngineTime-1.0.2-py3-none-any.whl
- pip uninstall SwEngineTime


------------------------------------------------------------------------------------------------------------------------

GitHub:
=======

How to see commits per branch:
------------------------------
- https://github.com/{user}/{repo}/commit/{branch}
- For example: https://github.com/airspansvg/InfrastructureSVG/commit/master


------------------------------------------------------------------------------------------------------------------------

auto-py-to-exe:
===============

How to install auto-py-to-exe:
--------------------
- pip install auto-py-to-exe
- Enter "auto-py-to-exe" on the terminal


------------------------------------------------------------------------------------------------------------------------

LDAP:
=====

LDAP from terminal:
-----------------

ldapobj = ldap.initialize("ldap://IPAddress:PORT")
ldapobj.simple_bind_s(user, password)

ldapobj.search_s("OU=Israel,OU=UsersAirspan,DC=airspan,DC=com", ldap.SCOPE_SUBTREE, "(objectClass=user)")



------------------------------------------------------------------------------------------------------------------------

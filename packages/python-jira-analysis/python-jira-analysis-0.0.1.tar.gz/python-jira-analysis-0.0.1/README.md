README
==================

installation
------------------

* clone python-jira-analysis

    hg clone ssh://hg@bitbucket.org/fikander/python-jira-analysis

* create Python virtual environment and active it

    virtualenv venv    
    . venv/bin/activate    

* run setup package - it will download and install all dependencies in the virtual env

    cd python-jira-analysis    
    python ./setup.py install    

* NOTE: OSX: if installation of numpy module fails above due, try running this:

    ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install numpy    
    ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future python ./setup.py install    

* create SQLite database where stats will be saved. Database is created at ~/jira_analysis.sqlite3 (your home directory)

    jira_analysis_manage.py syncdb

* create config.ini file with your credentials (see FAQ below)

running server
-----------------

* activate virtual environment if not active

    . venv/bin/activate  

* run Django development server. IMPORTANT: config.ini should be in directory you're running jira_analysis_manage.py from

    jira_analysis_manage.py runserver

calculating stats
------------------

* make sure that server is running and navigate to `http://localhost:8000/infographics/`

FAQ
====

Q: How to manually modify SQLite DB
-----------------
use SQlite Database Browser to execute SQL, e.g.:

`ALTER TABLE project ADD COLUMN tag varchar(64)`

Q: What's the format of config.ini
------------------
    [general]
    default-jira-profile=jira

    [jira]
    url=https://jira.shazamteam.net
    user=JIRA_USERNAME
    pass=JIRA_PASSWORD

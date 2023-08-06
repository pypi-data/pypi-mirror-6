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

setting up project
------------------

* make sure that server is running and navigate to `http://localhost:8000/admin`

* create new Project definition object and fill all the fields. Example values for SOA project:

        "bugTypes": "Bug", 
        "updated": "2014-03-26T15:01:12.399Z", 
        "project_name": "Shazam on Android", 
        "endStatuses": "5,6", 
        "versions": "4.5.0,4.6.0", 
        "timestamp": "2014-03-26T15:01:12.399Z", 
        "startStatuses": "10033", 
        "project_key": "SOA", 
        "jql": "type NOT IN subTaskIssueTypes() AND (labels IS EMPTY OR labels NOT IN (old_for_review)) AND (Resolution IS EMPTY OR Resolution NOT IN (Duplicate))", 
        "histogramBins": 360, 
        "minLeadTime": 60, 
        "devStatuses": "10033,10035", 
        "qaStatuses": "10004,10003,10071,10038", 
        "owner": 1, 
        "statuses": "1,4,10089,10000,10048,10069,10068,10030,10076,10033,10035,10004,10003,10071,10038,5,6"

* NOTE: you can use /statuses URL to get a list of all available statuses with their ids

calculating stats
------------------

* make sure that server is running and navigate to `http://localhost:8000/`

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

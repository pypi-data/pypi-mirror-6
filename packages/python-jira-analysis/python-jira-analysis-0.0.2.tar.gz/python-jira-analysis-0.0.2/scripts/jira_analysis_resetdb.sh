#!/bin/bash


# 1. ./resetdb.sh save - saves JSON dump in datadumps/ directory
# 2. modify models
# 3. ./resetdb.sh reset JSON_DUMP_FILENAME

DB=~/jira_analysis.sqlite3
APP=analysis
MANAGE=jira_analysis_manage.py
tmpdate=$(date "+%Y%m%d-%H%M%S")

if [[ $1 = 'save' ]]; then
	mkdir datadumps 2>/dev/null
	echo "+ Dumping django project database to fixture DUMP-${tmpdate}.json ..."
	$MANAGE dumpdata $APP --format='json' --indent=4 --verbosity=1 > datadumps/DUMP-${tmpdate}.json
	echo "+ Backing up sqlite binary store..."
	cp $DB $DB.${tmpdate}
	echo "Saved to datadumps/DUMP-${tmpdate}.json"
fi

if [[ $1 = 'reset' ]]; then
	file=$2
	echo "+ Rebuilding database structure from model defs..."
	$MANAGE sqlclear $APP
	echo "+ Reloading project data from fixture dump $file ..."
	$MANAGE loaddata $file
fi

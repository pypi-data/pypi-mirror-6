import logging
import datetime
import pytz
import numpy as np
from collections import defaultdict
import itertools

from dateutil.parser import parse as dateparse
from jira.config import get_jira
from jira.exceptions import JIRAError

logger = logging.getLogger(__name__)

JIRA = get_jira()

def days_from_timedelta(dt):
    return float(dt.total_seconds())/86400

def get_JQL(context):
    base = 'project=' + context['project'][0] + ' AND ' + context['jql']
    if context['version']:
        return base + ' AND fixVersion="{}"'.format(context['version'])
    else:
        return base

STATUS_NAMES = {}

def get_status_names_map():
    if len(STATUS_NAMES) == 0:
        statuses = JIRA.statuses()
        for status in statuses:
            STATUS_NAMES[int(status.id)] = status.name
    return STATUS_NAMES

# issueCache = { (jql, fields, expand): (date_created, [issue, ...]) }
issueCache = {}

def issue_iterator_factory(jql, fields, expand):
    '''
    produces iterator with a simple memory cache
    '''
    def issue_iterator_jira():
        # try to hit the cache
        try:
            cached = issueCache[(jql, fields, expand)]
            age = datetime.datetime.now() - cached[0]
            if age.total_seconds() < 3600:
                for issue in cached[1]:
                    yield issue
                return
        except KeyError:
            logging.warning("Cache missed for JQL: " + jql)
            pass
        # no cache - need to actually go and fetch the data from JIRA
        finished = False
        startAt=0
        maxResults=50
        cache=[]
        while not finished:
            try:
                issues = JIRA.search_issues(
                    jql,
                    startAt=startAt,
                    maxResults=maxResults,
                    fields=fields,
                    expand=expand)
            except JIRAError, e:
                raise Exception("Error retrieving results " + str(e))
            startAt += len(issues)
            finished = len(issues) < maxResults
            for issue in issues:
                cache.append(issue)
                yield issue
        issueCache[(jql, fields, expand)] = (
            datetime.datetime.now(),
            cache
            )
    return issue_iterator_jira

def items_count(context):
    iterator = issue_iterator_factory(
        get_JQL(context),
        "summary,created,issuetype,components,versions", "changelog"
    )
    return len(list(iterator()))

class Phases(object):
    SPEC = 0
    DEV = 1
    QA = 2
    DONE = 3

class States(object):
    SPEC = 0
    DEV = 1
    FIXING = 2

def analyse_issue_for_fixing_time(issue, devStatuses, qaStatuses, doneStatuses, bugTypes):
    '''
    Results are:

    { (workitem):
        {
            'dev_time': X, # item moving forward in the workflow
            'fix_time': X, # item recovering after it's been moved back
            'loops': X, # how many times moved from QA to DEV or SPEC
            'type': X, # issue type
            'finished': X, # has it reached end state
        }
    }

    Items of type bugTypes don't have dev_time - all their time is added to fix_time
    '''

    def status_iterator(issue):
        for history in issue.changelog.histories:
            created = dateparse(history.created)
            for history_item in history.items:
                if history_item.field == 'status':
                    to = int(history_item.to)
                    if to in devStatuses:
                        phase = Phases.DEV
                    elif to in qaStatuses:
                        phase = Phases.QA
                    elif to in doneStatuses:
                        phase = Phases.DONE
                    else:
                        phase = Phases.SPEC
                    yield created, phase

    state = States.SPEC
    last_phase = Phases.SPEC
    dev_time = 0
    fix_time = 0
    fix_time_alt = 0 # This is a sum of dev and fix in case of Bugs.
    loops = 0
    last_time = dateparse(issue.fields.created)
    for created, phase in status_iterator(issue):
        #logging.error("{}: {}, {}".format(issue.key, phase, created))
        dt = created - last_time
        if state == States.DEV:
            dev_time += dt.total_seconds()
        elif state == States.FIXING:
            fix_time += dt.total_seconds()

        if phase == Phases.SPEC:
            state = States.SPEC
        elif phase == Phases.DEV:
            if last_phase == Phases.QA:
                state = States.FIXING
                loops += 1
            elif state != States.FIXING:
                state = States.DEV
        last_phase = phase
        last_time = created

    if last_phase != Phases.DONE:
        dt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - last_time
        if state == States.DEV:
            dev_time += dt.total_seconds()
        elif state == States.FIXING:
            fix_time += dt.total_seconds()

    # Calc alternative fix time, where Bugs don't have dev time
    if issue.fields.issuetype.name in bugTypes:
        fix_time_alt = dev_time + fix_time
    else:
        fix_time_alt = fix_time

    return {
        'loops': loops,
        'dev_time': dev_time,
        'fix_time': fix_time,
        'fix_time_alt': fix_time_alt,
        'finished': last_phase == Phases.DONE,
        'type': issue.fields.issuetype.name,
    }

def analyse_issues_for_fixing_time(context):
    '''
    '''
    iterator = issue_iterator_factory(
        get_JQL(context),
        "summary,created,issuetype,components,versions", "changelog"
    )
    results = {}
    for issue in iterator():
        results[issue.key] = analyse_issue_for_fixing_time(
            issue,
            context['devStatuses'],
            context['qaStatuses'],
            context['endStatuses'],
            context['bugTypes'],
        )
    bugs = [workitem for workitem in results.items() if workitem[1]['type'] in context['bugTypes']]
    nonbugs = [workitem for workitem in results.items() if workitem[1]['type'] not in context['bugTypes']]

    i = 0
    summary = []
    for work_items, work_items_type in [
                (nonbugs, 'Non bugs'),
                (bugs, 'Bugs'),
                (results.items(), 'Total')
            ]:
        summary.append({})
        summary[i]['type'] = work_items_type
        summary[i]['started_items'] = len([item for item in work_items if item[1]['dev_time']+item[1]['fix_time'] > 0])
        summary[i]['finished_items'] = len([item for item in work_items if item[1]['finished']])
        summary[i]['total_dev_time'] = sum(work_item[1]['dev_time'] for work_item in work_items)
        summary[i]['total_fix_time'] = sum(work_item[1]['fix_time'] for work_item in work_items)
        summary[i]['total_fix_time_alt'] = sum(work_item[1]['fix_time_alt'] for work_item in work_items)
        dev_and_fix_time = summary[i]['total_fix_time'] + summary[i]['total_dev_time']
        if dev_and_fix_time > 0:
            summary[i]['total_fix_time_p'] = 100.0 * summary[i]['total_fix_time'] / dev_and_fix_time
            summary[i]['total_fix_time_alt_p'] = 100.0 * summary[i]['total_fix_time_alt'] / dev_and_fix_time
        else:
            summary[i]['total_fix_time_p'] = 0.0
            summary[i]['total_fix_time_alt_p'] = 0.0
        summary[i]['items_needed_fixing'] = len([item for item in work_items if item[1]['loops']>0])
        summary[i]['qa_to_dev_move'] = sum(work_item[1]['loops'] for work_item in work_items)
        i += 1

    return results, summary


def issue_loops(issue, statuses, allLoops):
    '''
    a single loop is represented as:

    { (from, to): 
        { 'issues': [
          {from:X, to:X, start:X, key:X, summary:X, end:X, timedelta:X}, # closed loop
          {from:X, to:X, start:X, key:X, summary:X}, # open loop
          ],
          finished: {
            'min': X,
            'max': X,
            'stdDev': X,
            'mean': X,
            'median': X, 
          },
          unfinished: {
            'min': X,
            'max': X,
            'stdDev': X,
            'mean': X,
            'median': X, 
          },
        },
    ...
    }

    '''
    histories = issue.changelog.histories
    lastKnownStatusIndex = 0
    hasLoops = False
    loops=[] # stack of loops
    logger.info("==== ISSUE: {}: {}".format(issue.key, issue.fields.summary))
    for history in histories:
        for history_item in history.items:
            if history_item.field == 'status':
                logger.info('{}: by {}, from:{} {}, to:{} {}'.format(
                    history.created,
                    history.author.displayName,
                    history_item.__dict__['from'], #from is a keyword so cannot simply ready it
                    history_item.fromString,
                    history_item.to,
                    history_item.toString))
                try:
                    statusIndex = statuses.index(int(history_item.to))
                    if statusIndex < lastKnownStatusIndex:
                        logger.info("Moving back from {} to {}".format(lastKnownStatusIndex, statusIndex))
                        # new transition
                        loops.append({
                            'from': lastKnownStatusIndex,
                            'from_id': statuses[lastKnownStatusIndex],
                            'to': statusIndex,
                            'to_id': statuses[statusIndex],
                            'start': dateparse(history.created),
                            'key': issue.key,
                            'summary': issue.fields.summary,
                        })
                        logger.info("Created new transition: {}".format(loops[-1]))
                        hasLoops = True
                    else:
                        # check if last transition closed
                        for t in loops[::-1]:
                            if t['from'] <= statusIndex:
                                newLoop = loops.pop()
                                newLoop['end'] = dateparse(history.created)
                                td = newLoop['end'] - newLoop['start']
                                newLoop['timedelta'] = td
                                newLoop['days'] = days_from_timedelta(td)
                                logger.info("Closing loop: {}".format(newLoop))
                                key = (newLoop['from_id'], newLoop['to_id'])
                                if not allLoops.has_key(key):
                                    allLoops[key] = {}
                                    allLoops[key]['issues'] = []
                                allLoops[key]['issues'].append(newLoop)
                            else:
                                break
                    lastKnownStatusIndex = statusIndex
                except ValueError:
                    logger.warning("Unknown status: {}".format(history_item.to))
            else:
                # update of field different than status
                #print history_item['field']
                pass
    if len(loops) > 0:
        # add timedeltas and mark unfinished loops as such
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        for unfinishedLoop in loops:
            key = (unfinishedLoop['from_id'], unfinishedLoop['to_id'])
            if not allLoops.has_key(key):
                allLoops[key] = {}
                allLoops[key]['issues'] = []
            td = now - unfinishedLoop['start']
            unfinishedLoop['timedelta'] = td
            unfinishedLoop['days'] = days_from_timedelta(td)
            unfinishedLoop['unfinished'] = True
            allLoops[key]['issues'].append(unfinishedLoop)
    return hasLoops


def analyse_issues_for_loops(context):
    iterator = issue_iterator_factory(
        get_JQL(context),
        "summary,created,issuetype,components,versions", "changelog"
    )
    loops = {}
    for issue in iterator():
        hasLoops = issue_loops(issue, context['statuses'], loops)
    # calculate some extra parameters
    for key, loop in loops.items():
        days = [issue['days'] for issue in loop['issues'] if not issue.has_key('unfinished')]
        unfinishedDays = [issue['days'] for issue in loop['issues'] if issue.has_key('unfinished')]
        loop['finished'] = {}
        loop['unfinished'] = {}
        if len(days) > 0:
            loop['finished']['mean'] = np.mean(days)
            loop['finished']['median'] = np.median(days)
            loop['finished']['min'] = np.min(days)
            loop['finished']['max'] = np.max(days)
            loop['finished']['std'] = np.std(days)
            loop['finished']['sum'] = np.sum(days)
        if len(unfinishedDays) > 0:
            loop['unfinished']['mean'] = np.mean(unfinishedDays)
            loop['unfinished']['median'] = np.median(unfinishedDays)
            loop['unfinished']['min'] = np.min(unfinishedDays)
            loop['unfinished']['max'] = np.max(unfinishedDays)
            loop['unfinished']['std'] = np.std(unfinishedDays)
            loop['unfinished']['sum'] = np.sum(unfinishedDays)
    return loops


def issue_times_in_columns(issue, statuses):
    '''
    Result is:
    (issuekey, {status: time, ...})
    '''

    def status_iterator(issue):
        for history in issue.changelog.histories:
            created = dateparse(history.created)
            for history_item in history.items:
                if history_item.field == 'status':
                    to = int(history_item.to)
                    yield to, created

    times = {}
    currentStatus = statuses[0]
    last_time = dateparse(issue.fields.created)
    for to, moved in status_iterator(issue):
        dt = moved - last_time 
        try:
            times[currentStatus] += dt.total_seconds()
        except KeyError:
            times[currentStatus] = dt.total_seconds()
        currentStatus = to
        last_time = moved
    return times


def analyse_times_in_columns(context):
    '''
    Returns:
    - times: complete list of times in each column for every work item
    - results: array of tuples (status, summary dictionary)
    - summary: the same as results, but it's a dict of {status: summary}
    '''
    iterator = issue_iterator_factory(
        get_JQL(context),
        "summary,created,issuetype,components,versions", "changelog"
    )
    times = []
    for issue in iterator():
        times.append((issue.key, issue_times_in_columns(issue, context['statuses'])))

    times_lists = [ i[1].items() for i in times ]
    times_list = list(itertools.chain(*times_lists))
    summary = defaultdict(dict)
    for key, group in itertools.groupby(sorted(times_list), key=lambda x: x[0]):
        values = [i[1] for i in group] # times in this column for all tickets which have been here
        summary[key]['sum'] = np.sum(values)
        summary[key]['mean'] = np.mean(values)
        summary[key]['median'] = np.median(values)
        summary[key]['std'] = np.std(values)
        summary[key]['min'] = np.min(values)
        summary[key]['max'] = np.max(values)
        summary[key]['count'] = len(values)

    # prepare list ordered according to status ids
    results = []
    for status in context['statuses']:
        results.append((status, summary[status]))

    return times, results, summary


def issue_start_end_times(issue, statuses, startStatuses, endStatuses):

    def has_hit_status(history_item, statuses_to_find):
        '''
        are statuseToFind somewhere between 'from' and 'to' in history_item
        '''
        try:
            startStatusIndex = statuses.index(int(history_item.__dict__['from']))
            endStatusIndex = statuses.index(int(history_item.to))
        except ValueError:
            logging.error("Unknown status: {} or {}".format(history_item.fromString, history_item.toString))
            return False
        for i in xrange(startStatusIndex, endStatusIndex + 1):
            hit = statuses[i] in statuses_to_find
            if hit:
                return True
        return False

    def get_status_hit_time(histories, statuses_to_find):
        for history in histories:
            for history_item in history.items:
                if history_item.field == 'status':
                    if has_hit_status(history_item, statuses_to_find):
                        return dateparse(history.created)
        return None

    histories = issue.changelog.histories
    # find start time
    if 0 in [statuses.index(startStatus) for startStatus in startStatuses]:
        startTime = dateparse(issue.fields.created)
    else:
        startTime = get_status_hit_time(histories, startStatuses)
    # find end time
    if startTime:
        endTime = get_status_hit_time(histories, endStatuses)
    else:
        endTime = None
    # find length so far
    if endTime is not None:
        timedelta = endTime - startTime
    elif startTime is not None:
        # item hasn't finished, so assume it's still being worked on
        timedelta = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - startTime
    else:
        timedelta = None
    versions = []
    for version in issue.fields.versions:
        versions.append(version.name)
    return {
        'start': startTime,
        'end': endTime,
        'key': issue.key,
        'type': issue.fields.issuetype.name,
        'timedelta': timedelta.total_seconds() if timedelta is not None else None,
        'versions': versions,
    }


def analyse_issue_lead_times(context):
    '''
    Returns:
        lead_times: Array of dicts:
            [{'start', 'end', 'key', 'type', 'timedelta', 'versions'}, ...]
    '''
    iterator = issue_iterator_factory(
        get_JQL(context),
        "summary,created,issuetype,components,versions", "changelog"
    )
    lead_times = []
    for issue in iterator():
        lead_times.append(
            issue_start_end_times(
                issue,
                context['statuses'],
                context['startStatuses'],
                context['endStatuses'],
            )
        )
    # take only finished items into account
    cond = lambda t: t['end'] is not None and t['timedelta'] > context['minLeadTime']
    cond_bugs = lambda t: cond(t) and t['type'] in context['bugTypes']
    cond_nonbugs = lambda t: cond(t) and t['type'] not in context['bugTypes']
    # cond = lambda t: t['timedelta'] is not None # to take unfinished items into account
    finished_timedeltas = [t['timedelta'] for t in lead_times if cond(t)]
    finished_timedeltas_bugs = [t['timedelta'] for t in lead_times if cond_bugs(t)]
    finished_timedeltas_nonbugs = [t['timedelta'] for t in lead_times if cond_nonbugs(t)]
    values, bin_edges = np.histogram(
        finished_timedeltas,
        bins=context['histogramBins'],
        density=False)
    values_bugs, bin_edges_bugs = np.histogram(
        finished_timedeltas_bugs,
        bins=bin_edges,
        density=False)
    values_nonbugs, bin_edges_nonbugs = np.histogram(
        finished_timedeltas_nonbugs,
        bins=bin_edges,
        density=False)

    mean = np.mean(finished_timedeltas)
    median = np.median(finished_timedeltas)
    std = np.std(finished_timedeltas)
    mean_bugs = np.mean(finished_timedeltas_bugs)
    median_bugs = np.median(finished_timedeltas_bugs)
    std_bugs = np.std(finished_timedeltas_bugs)
    mean_nonbugs = np.mean(finished_timedeltas_nonbugs)
    median_nonbugs = np.median(finished_timedeltas_nonbugs)
    std_nonbugs = np.std(finished_timedeltas_nonbugs)

    #logger.error(np.sum(values*np.diff(bin_edges)))
    bin_centers = []
    for i in xrange(len(bin_edges)-1):
        bin_centers.append((bin_edges[i] + bin_edges[i+1]) / 2.0)
    return lead_times, bin_centers,\
        values,\
        values_bugs,\
        values_nonbugs,\
        mean, median, std,\
        mean_bugs, median_bugs, std_bugs,\
        mean_nonbugs, median_nonbugs, std_nonbugs

def analyse_breakdown_by_type(context):
    by_issuetype = {}
    by_component = {}
    total_count = 0
    iterator = issue_iterator_factory(
        get_JQL(context),
        "summary,created,issuetype,components,versions", "changelog"
    )
    for issue in iterator():
        total_count += 1
        try:
            by_issuetype[issue.fields.issuetype.name] += 1
        except KeyError:
            by_issuetype[issue.fields.issuetype.name] = 1
        for component in issue.fields.components:
            try:
                by_component[component.name] += 1
            except KeyError:
                by_component[component.name] = 1
    return by_issuetype, by_component, total_count

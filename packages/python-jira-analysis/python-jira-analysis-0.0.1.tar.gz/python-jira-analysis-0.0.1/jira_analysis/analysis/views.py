import logging
import datetime
import pytz
import numpy as np
import pickle

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden,\
    HttpResponseBadRequest, HttpResponseNotFound, Http404
from django.core.urlresolvers import reverse

from models import ProjectRecord

from dataminer import analyse_issues_for_loops,\
    analyse_issues_for_fixing_time,\
    analyse_times_in_columns,\
    analyse_issue_lead_times,\
    get_status_names_map,\
    analyse_breakdown_by_type,\
    items_count

log = logging.getLogger(__name__)

def get_histogram_bin(histogram_values, histogram_bins, percent):
    sum_to_reach = np.sum(histogram_values) * percent
    sum_so_far = 0.0
    i = 0
    while sum_so_far < sum_to_reach:
        sum_so_far += histogram_values[i]
        i += 1
    return histogram_bins[i-1]


def main(request):
    '''
    '''
    logging.log(logging.INFO, "home view")
    context = {
        # 'jql':  """project = SOA AND type not in subTaskIssueTypes() AND updated > startOfDay(-60d) AND 
        # (labels is EMPTY OR labels not in (old_for_review, technical_debt)) AND
        # (Resolution not in (Duplicate))
        #         """,
        'jql': """
        type NOT IN subTaskIssueTypes() AND
        (labels is EMPTY OR labels NOT IN (old_for_review)) AND
        (Resolution is EMPTY OR Resolution NOT IN (Duplicate)) 
        """,
        'project': ("SOA", "Shazam for Android"),
        'version': "4.5.0",
        #updated > startOfDay(-30d) AND
        'statuses': [
            1, #Open,
            4, #Reopened,
            10089, #Prioritised
            10000, # OLD: Awaiting Review 
            10048, # OLD: Defined but pickeable yet
            10069, #To Feature Kick Off
            10068, #In Design/Spec. Review
            10030, # OLD: Awaiting Definition
            10076, #Await Tech lead approval
            10033, #Awaiting Development
            10035, #In Development
            10004, #Awaiting Testing
            10003, #In Testing
            10071, #Broken
            10038, #UAT
            5, #Resolved
            6, #Closed
        ],
        'startStatuses': [10033], # used in lead time calculations
        'endStatuses': [5, 6],   # used in lead time calculations, fixing time calculations
        'devStatuses': [10033, 10035], # used in fixing time calculations
        'qaStatuses': [10004, 10003, 10071, 10038], # used in fixing time calculations
        'bugTypes': ['Bug'], # used in fixing time calculations
        'histogramBins': 360, # used in histogram calculations
        'minLeadTime': 60,# lead times smaller than this [s] will be ignored in histogram calculations
    }

    if request.GET.get('version'):
        context['version'] = request.GET['version']

    loops = analyse_issues_for_loops(context)

    fix_time_results, fix_time_summary = analyse_issues_for_fixing_time(context)
    fix_time_results_sorted_by_loops = fix_time_results.items()
    fix_time_results_sorted_by_loops.sort(key=lambda x: x[1]['loops'], reverse=True)
    fix_time_results_sorted_by_fix_time = fix_time_results.items()
    fix_time_results_sorted_by_fix_time.sort(key=lambda x: x[1]['fix_time'], reverse=True)

    times_in_columns,\
    times_in_columns_summary,\
    times_in_columns_dictionary = analyse_times_in_columns(context)

    lead_times,\
    histogram_bins,\
    histogram_values,\
    histogram_values_bugs,\
    histogram_values_nonbugs,\
    lead_times_mean,\
    lead_times_median,\
    lead_times_std,\
    lead_times_mean_bugs,\
    lead_times_median_bugs,\
    lead_times_std_bugs,\
    lead_times_mean_nonbugs,\
    lead_times_median_nonbugs,\
    lead_times_std_nonbugs = analyse_issue_lead_times(context)

    closed = [item for item in lead_times if item['end'] is not None]
    unfinished_count = len(lead_times) - len(closed)

    by_issuetype, by_component, total_count = analyse_breakdown_by_type(context)

    # get number of items closed within last 7 and 30 days based on the whole board
    global_context = dict(context)
    global_context['version'] = None
    global_context['jql'] += " AND updated > startOfDay(-30d)"

    global_lead_times,\
    global_histogram_bins,\
    global_histogram_values,\
    global_histogram_values_bugs,\
    global_histogram_values_nonbugs,\
    global_lead_times_mean,\
    global_lead_times_median,\
    global_lead_times_std,\
    global_lead_times_mean_bugs,\
    global_lead_times_median_bugs,\
    global_lead_times_std_bugs,\
    global_lead_times_mean_nonbugs,\
    global_lead_times_median_nonbugs,\
    global_lead_times_std_nonbugs = analyse_issue_lead_times(global_context)

    global_fifty_percent_bin = get_histogram_bin(global_histogram_values, global_histogram_bins, 0.5)
    global_ninety_percent_bin = get_histogram_bin(global_histogram_values, global_histogram_bins, 0.9)

    ago_7 = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(days=7)
    global_closed_7 = [item for item in global_lead_times if item['end'] and item['end'] > ago_7]
    global_throughput_7 = len(global_closed_7) / 7.0

    ago_30 = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - datetime.timedelta(days=30)
    global_closed_30 = [item for item in global_lead_times if item['end'] and item['end'] > ago_30]
    global_throughput_30 = len(global_closed_30) / 30.0

    if global_throughput_7 > 0:
        time_left_based_on_7_days_delivery_rate = 86400.0 * float(unfinished_count) / global_throughput_7
    else:
        time_left_based_on_7_days_delivery_rate = "infinity"
    if global_throughput_30 > 0:
        time_left_based_on_30_days_delivery_rate = 86400.0 * float(unfinished_count) / global_throughput_30
    else:
        time_left_based_on_30_days_delivery_rate = "infinity"
    bugs_affect_this_version = [item for item in lead_times \
        if item['type'] in context['bugTypes'] and \
        context['version'] in item['versions']]

    ctx_global = {
        'global_fifty_percent_bin': global_fifty_percent_bin,
        'global_ninety_percent_bin': global_ninety_percent_bin,

        'global_lead_times_mean': global_lead_times_mean,
        'global_lead_times_median': global_lead_times_median,
        'global_lead_times_std': global_lead_times_std,
        'global_lead_times_mean_bugs': global_lead_times_mean_bugs,
        'global_lead_times_median_bugs': global_lead_times_median_bugs,
        'global_lead_times_std_bugs': global_lead_times_std_bugs,
        'global_lead_times_mean_nonbugs': global_lead_times_mean_nonbugs,
        'global_lead_times_median_nonbugs': global_lead_times_median_nonbugs,
        'global_lead_times_std_nonbugs': global_lead_times_std_nonbugs,

        'global_throughput_7': global_throughput_7,
        'global_throughput_30': global_throughput_30,
    }

    ctx = {
        'context': context,
        'status_names': get_status_names_map(),

        'fix_time_summary': fix_time_summary,

        'times_in_columns_summary': times_in_columns_summary,
        'times_in_columns_dictionary': times_in_columns_dictionary,

        'lead_times_mean': lead_times_mean,
        'lead_times_median': lead_times_median,
        'lead_times_std': lead_times_std,
        'lead_times_mean_bugs': lead_times_mean_bugs,
        'lead_times_median_bugs': lead_times_median_bugs,
        'lead_times_std_bugs': lead_times_std_bugs,
        'lead_times_mean_nonbugs': lead_times_mean_nonbugs,
        'lead_times_median_nonbugs': lead_times_median_nonbugs,
        'lead_times_std_nonbugs': lead_times_std_nonbugs,

        'by_issuetype': by_issuetype,
        'by_component': by_component,
        'total_count': total_count,

        'unfinished_count': unfinished_count,
        'progress': len(closed) * 100.0 / len(lead_times),
        'time_left_based_on_7_days_delivery_rate': time_left_based_on_7_days_delivery_rate,
        'time_left_based_on_30_days_delivery_rate': time_left_based_on_30_days_delivery_rate,

        'bugs_affect_this_version': bugs_affect_this_version,
    }

    # create record in database for statistical calculations
    today = datetime.date.today()
    try:
        pr = ProjectRecord.objects.filter(
                version=context['version'],
                project=context['project'][0]
            ).filter(
                timestamp__gt=datetime.datetime(today.year, today.month, today.day)
            ).get().delete()
    except ProjectRecord.DoesNotExist:
        pass
    pr = ProjectRecord()
    pr.project = context['project'][0]
    pr.version = context['version']
    pr.data = pickle.dumps(ctx)
    pr.save()

    try:
        pr = ProjectRecord.objects.filter(
                version='',
                project=''
            ).filter(
                timestamp__gt=datetime.datetime(today.year, today.month, today.day)
            ).get().delete()
    except ProjectRecord.DoesNotExist:
        pass
    pr = ProjectRecord()
    pr.project = ''
    pr.version = ''
    pr.data = pickle.dumps(ctx_global)
    pr.save()

    ctx.update(ctx_global)

    ctx.update({
        'loops': loops,
        'statuses': context['statuses'],

        'fix_time_results': fix_time_results,
        'fix_time_results_sorted_by_loops': fix_time_results_sorted_by_loops,
        'top_fix_time_results_sorted_by_loops': fix_time_results_sorted_by_loops[:5],
        'fix_time_results_sorted_by_fix_time': fix_time_results_sorted_by_fix_time,
        'top_fix_time_results_sorted_by_fix_time': fix_time_results_sorted_by_fix_time[:5],

        'times_in_columns': times_in_columns,

        'histogram': zip(global_histogram_bins, global_histogram_values,
            global_histogram_values_bugs, global_histogram_values_nonbugs),

        'lead_times': lead_times,
        'global_lead_times': global_lead_times,

        'global_closed_within_7_days': global_closed_7,
        'global_closed_within_30_days': global_closed_30,
    })

    #fetch historical data from database
    q = ProjectRecord.objects.filter(
            version='',
            project=''
        )
    global_historical_data = []
    for record in q:
        global_historical_data.append((record.timestamp, pickle.loads(record.data)))

    q = ProjectRecord.objects.filter(
            version=context['version'],
            project=context['project'][0]
        )
    historical_data = []
    for record in q:
        historical_data.append((record.timestamp, pickle.loads(record.data)))

    ctx.update({
        'global_historical_data': global_historical_data,
        'historical_data': historical_data,
    })

    if request.path != '/':
        return render_to_response('infographics.html', RequestContext(request, ctx))
    else:
        return render_to_response('main.html', RequestContext(request, ctx))


def help(request):
    '''
    '''
    ctx = {}
    return render_to_response('help.html', RequestContext(request, ctx))

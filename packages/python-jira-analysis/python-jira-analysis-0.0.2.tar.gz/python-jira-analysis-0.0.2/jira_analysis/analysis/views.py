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

from models import ProjectRecord, ProjectDefinition

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


def getContextFromProjectDefinition(project):

    def toIntArray(s, sep=','):
        return [int(x) for x in s.split(sep)]

    return {
        'jql':project.jql,
        'project':(project.project_key, project.project_name),
        'version':None,
        'statuses':toIntArray(project.statuses),
        'startStatuses':toIntArray(project.startStatuses),
        'endStatuses':toIntArray(project.endStatuses),
        'devStatuses':toIntArray(project.devStatuses),
        'qaStatuses':toIntArray(project.qaStatuses),
        'bugTypes':project.bugTypes,
        'histogramBins':project.histogramBins,
        'minLeadTime':project.minLeadTime,
    }


def calculate_statistics(context):
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

    global_statistics = {
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

    project_statistics = {
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

    extended_statistics = {
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
    }

    return global_statistics, project_statistics, extended_statistics


def do_sample_project(project, version, force=False):
    # make sure we actually want to calculate stats
    today = datetime.date.today()
    project_record_exists = ProjectRecord.objects.filter(
            project=project.project_key,
            version=version
        ).filter(
            timestamp__gt=datetime.datetime(today.year, today.month, today.day)
        ).exists()

    if project_record_exists and not force:
        log.error("\tno need to sample")
        return

    if project_record_exists:
        pr = ProjectRecord.objects.filter(
                project=project.project_key,
                version__in=[version, '']
            ).filter(
                timestamp__gt=datetime.datetime(today.year, today.month, today.day)
            ).delete()

    context = getContextFromProjectDefinition(project)
    context['version'] = version

    global_statistics,\
    project_statistics,\
    extended_statistics = calculate_statistics(context)

    pr = ProjectRecord()
    pr.project = project.project_key
    pr.version = version
    pr.data = pickle.dumps(project_statistics)
    pr.save()

    try:
        pr = ProjectRecord.objects.filter(
            project=project.project_key,
            version=''
        ).filter(
            timestamp__gt=datetime.datetime(today.year, today.month, today.day)
        ).get()
    except ProjectRecord.DoesNotExist:
        pr = ProjectRecord()
        pr.project = project.project_key
        pr.version = ''
    pr.data = pickle.dumps(global_statistics)
    pr.save()


def sample_all(request):
    '''
    Should be called from cron once a day - updates all the projects with fresh stats
    if force=true specifiec as GET parameter - overwrites the stats for the day
    '''
    force = False
    if request.GET.get('force'):
        force = request.GET['force'].lower() == "true"

    for project in ProjectDefinition.objects.all():
        for version in project.versions:
            log.error('processing: {}, version {}'.format(project.project_key, version))
            do_sample_project(project, version, force)
    return HttpResponse("sampled all projects")


def infographics(request, project_id):
    '''
    Prints the main page with all stats for given project and version.
    '''
    project = get_object_or_404(ProjectDefinition, pk=project_id)

    context = getContextFromProjectDefinition(project)

    if request.GET.get('version'):
        context['version'] = request.GET['version']

    global_statistics,\
    project_statistics,\
    extended_statistics = calculate_statistics(context)

    ctx = dict()
    ctx.update(global_statistics)
    ctx.update(project_statistics)
    ctx.update(extended_statistics)

    #fetch historical data from database
    q = ProjectRecord.objects.filter(
            version='',
            project=context['project'][0]
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

    return render_to_response('infographics.html', RequestContext(request, ctx))


def main(request):
    pd = ProjectDefinition.objects.all()

    ctx = {
        'projects': pd,
    }

    return render_to_response('main.html', RequestContext(request, ctx))

def statuses(request):
    ctx = {
        'status_names': get_status_names_map(),
    }

    return render_to_response('statuses.html', RequestContext(request, ctx))


def help(request):
    '''
    '''
    ctx = {}
    return render_to_response('help.html', RequestContext(request, ctx))

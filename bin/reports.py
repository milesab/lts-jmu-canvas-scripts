import os, datetime, time
import urllib, urllib2, MultipartPostHandler, json
import api_local, api_canvas

config = api_local.get_config()
report_dir = config['local']['report_dir']
easel_home = config['local']['easel_home']

# List of reports to run - formatted as tuples of (report_type,report_parameters)
reports = [ \
    ('last_user_access_csv',{"parameters": {'Term':'All Terms'}}) \
    ]

# Generate new report
def report_generate(report,params):
    report_id_file = easel_home + 'data/temp/%s.txt' % report
    report_file = report_dir + '%s.csv' % report
    api_canvas.report_submit(report,params,report_id_file)
    report_id = int(open(report_id_file, 'r').read().strip())
    progress = 0
    while progress < 100:
        time.sleep(60)
        progress = api_canvas.job_status(report_id,report)['progress']
    file_url = api_canvas.job_status(report_id,report)['attachment']['url']
    try:
        api_canvas.report_download(file_url,report_file)
    except:
        print "Report download failed, keeping previous report"


if __name__ == '__main__':

    for report in reports:
        report_generate(report[0],report[1])
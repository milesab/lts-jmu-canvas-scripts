import os, fnmatch, zipfile
import urllib, urllib2, MultipartPostHandler, json, ssl
import api_local
import requests
requests.packages.urllib3.disable_warnings()

config = api_local.get_config()
account_id = config['canvas']['account_id']
access_token = config['canvas']['access_token']
base_url = config['canvas']['base_url']
export_dir = config['local']['export_dir']


# Break up data for multiple API calls
def chunks(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


# Return the status of a job - job_arg can be job ID or a path to a file containing a job ID
def job_status(job_arg,endpoint_arg):
    job = str(job_arg)
    if job.isdigit():
        job_id = int(job)
    elif os.path.isfile(job):
        job_id = int(open(job, 'r').read().strip())

    if endpoint_arg == 'import':
        endpoint = 'accounts/%s/sis_imports/%s.json?access_token=%s' % (account_id,job_id,access_token)
    elif endpoint_arg == 'export':
        endpoint = 'accounts/%s/reports/provisioning_csv/%s?access_token=%s' % (account_id,job_id,access_token)
    elif endpoint_arg == 'last_user_access_csv':
        endpoint = 'accounts/%s/reports/last_user_access_csv/%s?access_token=%s' % (account_id,job_id,access_token)
    else:
        endpoint = endpoint_arg

    if job_id:
        response = urllib2.urlopen(base_url + endpoint).read().strip()
        return json.loads(response)


# Clean up files from previous imports
def import_clear(import_file,import_id_file):
    try:
        os.remove(import_file)
    except OSError:
        pass
    try:
        os.remove(import_id_file)
    except OSError:
        pass


# Create a zip of the CSV files to import
def import_zip(import_file,import_dir):
    if os.listdir(import_dir):
		try:
			zip = zipfile.ZipFile(import_file, 'w', zipfile.ZIP_DEFLATED)
			for base, dirs, files in os.walk(import_dir):
				for d in dirs:
					dirs.remove(d)
				for fn in fnmatch.filter(files, '*.csv'):
					absfn = os.path.join(base, fn)
					zfn = absfn[len(os.path.join(import_dir)):]
					zip.write(absfn, zfn)
			zip.close()
		except:
			pass		


# Submit import to canvas and record the import ID
def import_submit(import_file,import_id_file):
    if os.path.isfile(import_file):
        params = {'attachment':open(str(import_file),'rb'),
            'access_token':str(access_token),
            'import_type':'instructure_csv',
            'extension': 'zip',
            }

        # MultipartPostHandler module is needed to post the CSV zip file
        opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
        urllib2.install_opener(opener)
        req = urllib2.Request(str(base_url + 'accounts/%s/sis_imports.json' % account_id),params)
        response = urllib2.urlopen(req).read().strip()
        response_data = json.loads(response)
        import_id = response_data['id']

        # Write import_id to text file for future reference
        id_file = open(import_id_file,'w')
        id_file.write("%s" % import_id)
        id_file.close()


# Submit export request to canvas using the provisioning report API
def export_submit(export_id_file):
    endpoint = base_url + 'accounts/%s/reports/provisioning_csv' % account_id
    params = {"parameters": {'terms':'1','courses':'1','sections':'1','enrollments':'1','users':'1','xlist':'1'}}
    params = json.dumps(params)
    request = urllib2.Request(endpoint,params,{'Content-type': 'application/json','Authorization':'Bearer %s' % access_token})
    response = urllib2.urlopen(request).read().strip()
    response_data = json.loads(response)
    export_id = response_data['id']

    # Write export_id to text file for future reference
    id_file = open(export_id_file,'w')
    id_file.write("%s" % export_id)
    id_file.close()


# Retrieve export and unzip it to the export directory
def export_download(file_url,export_file):
    headers = {'Authorization': 'Bearer %s' % access_token}
    export_request = requests.get(file_url,headers=headers)

    #export_data = urllib2.urlopen(file_url, context=ssl.ctx)
    with open(export_file, "wb+") as dl_file:
        dl_file.write(export_request.content)
        zip_file = zipfile.ZipFile(dl_file, "r")
        for subfile in zip_file.namelist():
            print('downloading ' + subfile)
            zip_file.extract(subfile,export_dir)
        dl_file.close()


# Submit report request to canvas, save most recent job_id to check status
def report_submit(report,params,report_id_file):
    endpoint = base_url + 'accounts/%s/reports/%s' % (account_id,report)
    params = json.dumps(params)
    request = urllib2.Request(endpoint,params,{'Content-type': 'application/json','Authorization':'Bearer %s' % access_token})
    response = urllib2.urlopen(request).read().strip()
    response_data = json.loads(response)
    report_id = response_data['id']

    # Write report_id to text file for future reference
    id_file = open(report_id_file,'w')
    id_file.write("%s" % report_id)
    id_file.close()


# Retrieve report 
def report_download(file_url,report_file):
    report_request = urllib2.Request(file_url,None,{'Authorization':'Bearer %s' % access_token})
    report_data = urllib2.urlopen(file_url)
    dl_file = open(report_file, 'w')
    dl_file.write(report_data.read())
    dl_file.close()


# Get list of sections in a course
def get_courseinfo(course_id):
    courseinfo_endpoint = base_url + 'courses/%s' % course_id
    courseinfo_request = urllib2.Request(courseinfo_endpoint,None,{'Authorization':'Bearer %s' % access_token})
    courseinfo_response = urllib2.urlopen(courseinfo_request).read().strip()
    return json.loads(courseinfo_response)


# Get list of students in a course
def get_students(course_id):
    students = []
    students_endpoint = base_url + 'courses/%s/users?enrollment_type=student&per_page=100' % course_id
    #students_endpoint = base_url + 'courses/%s/enrollments?type=StudentEnrollment&per_page=100&page=1' % course_id
    request_headers = {'Authorization':'Bearer %s' % access_token}
    url = students_endpoint
    more_pages = True
    while more_pages:
        student_request = requests.get(url,headers=request_headers)
        students+=student_request.json()
        if 'next' in student_request.links.keys():
            url = student_request.links['next']['url']
        else:
            more_pages = False
    return students


# Get list of sections in a course
def get_sections(course_id):
    section_endpoint = base_url + 'courses/%s/sections' % course_id
    section_request = urllib2.Request(section_endpoint,None,{'Authorization':'Bearer %s' % access_token})
    section_response = urllib2.urlopen(section_request).read().strip()
    return json.loads(section_response)


# Get scores for the course
def get_scores(student_data,course_id):
    scores = []
    student_ids = [s['id'] for s in student_data]
    submissions_endpoint = base_url + 'courses/%s/students/submissions' % course_id
    for group in chunks(student_ids, 10):
        submission_params = [ ('grouped',1)]
        submission_params.extend([('student_ids[]',s) for s in group])
        submission_params = urllib.urlencode(submission_params)
        req = urllib2.Request(submissions_endpoint + "?" +submission_params,None,{'Authorization':'Bearer %s' % access_token})
        score_response = urllib2.urlopen(req).read().strip()
        scores = scores + (json.loads(score_response))
    return scores

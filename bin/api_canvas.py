import os, fnmatch, zipfile
import urllib, urllib2, MultipartPostHandler, json
import api_local

config = api_local.get_config()


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
        endpoint = 'accounts/%s/sis_imports/%s.json?access_token=%s' % (config['account_id'],job_id,config['access_token'])
    elif endpoint_arg == 'export':
        endpoint = 'accounts/%s/reports/provisioning_csv/%s?access_token=%s' % (config['account_id'],job_id,config['access_token'])
    else:
        endpoint = endpoint_arg

    if job_id:
        response = urllib2.urlopen(config['base_url'] + endpoint).read().strip()
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
        zip = zipfile.ZipFile(import_file, 'w', zipfile.ZIP_DEFLATED)
        for base, dirs, files in os.walk(import_dir):
            for d in dirs:
                dirs.remove(d)
            for fn in fnmatch.filter(files, '*.csv'):
                absfn = os.path.join(base, fn)
                zfn = absfn[len(os.path.join(import_dir)):]
                zip.write(absfn, zfn)
        zip.close()


# Submit import to canvas and record the import ID
def import_submit(import_file,import_id_file):
    if os.path.isfile(import_file):
        params = {'attachment':open(import_file,'rb'),
            'access_token':config['access_token'],
            'import_type':'instructure_csv',
            }

        # MultipartPostHandler module is needed to post the CSV zip file
        opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
        urllib2.install_opener(opener)
        req = urllib2.Request(config['base_url'] + 'accounts/%s/sis_imports.json' % config['account_id'],params)
        response = urllib2.urlopen(req).read().strip()
        response_data = json.loads(response)
        import_id = response_data['id']

        # Write import_id to text file for future reference
        id_file = open(import_id_file,'w')
        id_file.write("%s" % import_id)
        id_file.close()


# Submit export request to canvas using the provisioning report API
def export_submit(export_id_file):
    endpoint = config['base_url'] + 'accounts/%s/reports/provisioning_csv' % config['account_id']
    params = {"parameters": {'terms':'1','courses':'1','sections':'1','enrollments':'1','users':'1','xlist':'1'}}
    params = json.dumps(params)
    request = urllib2.Request(endpoint,params,{'Content-type': 'application/json','Authorization':'Bearer %s' % config['access_token']})
    response = urllib2.urlopen(request).read().strip()
    response_data = json.loads(response)
    export_id = response_data['id']

    # Write import_id to text file for future reference
    id_file = open(export_id_file,'w')
    id_file.write("%s" % export_id)
    id_file.close()


# Retrieve export and unzip it to the export directory
def export_download(file_url,export_file):
    export_request = urllib2.Request(file_url,None,{'Authorization':'Bearer %s' % config['access_token']})
    export_data = urllib2.urlopen(file_url)
    with open(export_file, "wb+") as dl_file:
        dl_file.write(export_data.read())
        zip_file = zipfile.ZipFile(dl_file, "r")
        for subfile in zip_file.namelist():
            zip_file.extract(subfile,config['export_dir'])
        dl_file.close()
    try:
        os.remove(export_file)
    except OSError:
        pass


# Get list of students in a course
def get_students(course_id):
    students_endpoint = config['base_url'] + 'courses/%s/students' % course_id
    student_request = urllib2.Request(students_endpoint,None,{'Authorization':'Bearer %s' % config['access_token']})
    student_response = urllib2.urlopen(student_request).read().strip()
    return json.loads(student_response)


# Get scores for the course
def get_scores(student_data,course_id):
    scores = []
    student_ids = [s['id'] for s in student_data]
    submissions_endpoint = config['base_url'] + 'courses/%s/students/submissions' % course_id
    for group in chunks(student_ids, 50):
        submission_params = [ ('grouped',1)]
        submission_params.extend([('student_ids[]',s) for s in group])
        submission_params = urllib.urlencode(submission_params)
        req = urllib2.Request(submissions_endpoint + "?" +submission_params,None,{'Authorization':'Bearer %s' % config['access_token']})
        score_response = urllib2.urlopen(req).read().strip()
        scores = scores + (json.loads(score_response))
    return scores
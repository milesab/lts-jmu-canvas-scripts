import os, csv

def get_config():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    config = {}
    config_file = open("../conf/settings.conf")
    for line in config_file:
        line = line.strip()
        if line and line[0] is not "#" and line[-1] is not "=":
            key,val = line.rsplit("=",1)
            config[key.strip()] = val.strip()
    return config
    
config = get_config()


def read_csv(filename,sortkey):
    export_data = []
    current_row = 0
    export_file = open(config['export_dir'] + filename)
    reader = csv.DictReader(export_file, fieldnames=[], restkey='undefined-fieldnames', delimiter=',', quotechar='"')
    for row in reader:
        current_row += 1
        if current_row == 1:
            reader.fieldnames = row['undefined-fieldnames']
            continue
        if row[sortkey] and row['status'] and row['status'] == "active":
            export_data.append(row)
    export_file.close()
    export_data.sort(key=lambda x: x[sortkey])
    return export_data


# Check to see if course exists
def course_check(cid,course_list):
    check = cid in course_list
    return check


# Check to see if course,section exists
def section_check(cid,sid,section_list):
    check = (cid,sid) in section_list
    return check


# Enrollment Diff
def diff_enroll(first,second):
    second_users = []
    for user in second:
        second_users.append(user['user_id'])
    return [enroll for enroll in first if enroll['user_id'] not in second_users]
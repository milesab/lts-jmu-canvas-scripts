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


# Check to see if course exists
def course_check(cid,all_courses):
    status = cid in all_courses
    return status


# Check to see if course,section exists
def section_check(cid,sid,all_sections):
    status = (cid,sid) in all_sections
    return status


def read_csv(filename):
    export_dict = []
    current_row = 0
    export_file = open(config['export_dir'] + filename)
    reader = csv.DictReader(export_file, fieldnames=[], restkey='undefined-fieldnames', delimiter=',', quotechar='"')
    for row in reader:
        current_row += 1
        if current_row == 1:
            reader.fieldnames = row['undefined-fieldnames']
            continue
        if row['status'] and row['status'] == "active":
            export_dict.append(row)
    export_file.close()
    return export_dict


# Get list of terms
def get_terms():
    terms_list = []
    terms = open(config['export_dir'] + 'terms.csv', 'r')
    reader = csv.DictReader(terms, delimiter=',', quotechar='"')
    for row in reader:
        term_id = row["term_id"]
        if term_id.isdigit():
            term_id = int(term_id)
        term_name = row["name"]
        status = row["status"]
        if status == "active" and term_name != "Default Term":
            terms_list.append( (term_id, term_name) )
    terms.close()
    return terms_list


# Get list of courses
def get_courses():
    courses_list = []
    courses = open(config['export_dir'] + 'courses.csv', 'r')
    reader = csv.DictReader(courses, delimiter=',', quotechar='"')
    for row in reader:
        ccid = int(row["canvas_course_id"])
        cid = row["course_id"]
        status = row["status"]
        if status == "active":
            courses_list.append( cid )
    courses.close()
    return courses_list


# Get list of course sections
def get_sections():
    sections_list = []
    sections = open(config['export_dir'] + 'sections.csv', 'r')
    reader = csv.DictReader(sections, delimiter=',', quotechar='"')
    for row in reader:
        ccid = int(row["canvas_course_id"])
        cid = row["course_id"]
        sid = row["section_id"]
        status = row["status"]
        if status == "active":
            sections_list.append( (cid, sid) )
    sections.close()
    return sections_list


def get_xlist():
    xlist_list = []
    xlist = open(config['export_dir'] + 'xlist.csv', 'r')
    reader = csv.DictReader(xlist, delimiter=',', quotechar='"')
    for row in reader:
        sid = row["section_id"]
        status = row["status"]
        if status == "active":
            xlist_list.append( sid )
    xlist.close()
    return xlist_list


# Get enrollments for a course
def get_enrollments(cid,sid):
    enrollments_list = []
    enrollments = open(config['export_dir'] + 'enrollments.csv', 'r')
    reader = csv.DictReader(enrollments, delimiter=',', quotechar='"')
    for row in reader:
        if row["status"] == "active" and cid == row["course_id"] and \
           sid == row["section_id"] and row["user_id"]:
            enrollments_list.append((row["user_id"],row["role"]))
    enrollments.close()
    return enrollments_list


# Enrollment Diff
def diff_enroll(first,second):
    second = set(second)
    return [enroll for enroll in first if enroll not in second]
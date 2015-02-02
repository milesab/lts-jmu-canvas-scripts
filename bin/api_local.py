import csv


def get_config():
    config = {}
    config_file = open("../conf/settings.conf")
    for line in config_file:
        line = line.strip()
        if line and line[0] is not "#" and line[-1] is not "=":
            key,val = line.rsplit("=",1)
            config[key.strip()] = val.strip()
    return config


# Check to see if course exists
def course_check(cid,all_courses):
    status = cid in all_courses
    return status


# Check to see if course,section exists
def section_check(cid,sid,all_sections):
    status = (cid,sid) in all_sections
    return status


# Get list of courses
def get_courses():
    courses_list = []
    courses = open(config['export_dir'], 'r')
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
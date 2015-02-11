import os, sys, re, cgi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bin')))
import api_local
config = api_local.get_config()

def get_params(fieldStorage):
    params = {}
    for key in fieldStorage.keys():
        params[key] = fieldStorage[key].value
    return params

if __name__ == '__main__':

    params = get_params(cgi.FieldStorage())
    print params

    courses = cgi.FieldStorage().getvalue('id').rstrip().replace("default","").split(',')
    users = api_local.read_csv(config['export_dir'] + 'users.csv', 'canvas_user_id')
    user_index = api_local.build_index(users,key='canvas_user_id')
    xlist = api_local.read_csv(config['export_dir'] + 'xlist.csv', 'xlist_course_id')
    
    for course in xlist:
        if course['xlist_course_id'] in courses and course['section_id'] not in courses:
            courses.append(course['section_id'])

    output = []
    total = 0

    enrollments = api_local.read_csv(config['export_dir'] + 'enrollments.csv', 'course_id')
    enrollments.sort(key=lambda x: (x['course_id'],x['user_id']))

    for enrollment in enrollments:
        course_id = enrollment['course_id']
        role = enrollment['role']
        if role == "student" and course_id in courses:
            total += 1
            canvas_id = enrollment['canvas_user_id']
            user_record = user_index[canvas_id]
            output.append("\t<student username=\"%s\">" % user_record['login_id'])
            output.append("\t\t<autharg></autharg>\n\t\t<authtype>localauth</authtype>")
            output.append("\t\t<email>%s</email>\n\t\t<enddate></enddate>" % user_record['email'])
            output.append("\t\t<firstname>%s</firstname>" % user_record['first_name'])
            output.append("\t\t<groupID>%s</groupID>" % course_id)
            output.append("\t\t<lastname>%s</lastname>" % user_record['last_name'])
            output.append("\t\t<middlename></middlename>\n\t\t<startdate></startdate>")
            output.append("\t\t<studentID>%s</studentID>\n\t</student>" % user_record['login_id'])

print "X-Enrollment-count: %s" % total
print "Content-type: text/plain\n"
print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE text>\n<students>"
for line in output:
    print line
print "</students>\n";

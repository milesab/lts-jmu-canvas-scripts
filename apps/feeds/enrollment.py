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

    # Default parameters
    format = 'XML'
    include = ['student','teacher']

    params = get_params(cgi.FieldStorage())

    output = []

    if params:
        try:
            courses = params['id'].rstrip().replace("default","").split(',')
        except:
            output.append("No course_id specified - please specify a course with ?id=")
        try:
            format = params['format']
            include = params['include']
        except:
            pass

    users = api_local.read_csv(config['export_dir'] + 'users.csv', 'canvas_user_id')
    user_index = api_local.build_index(users,key='canvas_user_id')
    xlist = api_local.read_csv(config['export_dir'] + 'xlist.csv', 'xlist_course_id')
   
    for course in xlist:
        if course['xlist_course_id'] in courses and course['section_id'] not in courses:
            courses.append(course['section_id'])

    enrollments = api_local.read_csv(config['export_dir'] + 'enrollments.csv', 'course_id')

    if format == "XML":
        enrollments.sort(key=lambda x: (x['course_id'],x['user_id']))
    elif format == "flat":
        enrollments.sort(key=lambda x: x['user_id'])

    total = 0
    students = []
    teachers = []

    for enrollment in enrollments:
        course_id = enrollment['course_id']
        role = enrollment['role']
        if role == "student" and "student" in include and course_id in courses:
            total += 1
            canvas_id = enrollment['canvas_user_id']
            user_record = user_index[canvas_id]
            students.append((course_id,user_record))
        elif role == "teacher" and "teacher" in include and course_id in courses:
            total +=1
            canvas_id = enrollment['canvas_user_id']
            user_record = user_index[canvas_id]
            teachers.append((course_id,user_record)) 
    
    if format == "XML":
        output.append("X-Enrollment-count: %s\n" % total)
        output.append("Content-type: text/plain\n")
        output.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE text>")
        if teachers:
            output.append("<teachers>")
            for teacher in teachers:
                output.append("\t<teacher username=\"%s\">" % teacher[1]['login_id'])
                output.append("\t\t<autharg></autharg>\n\t\t<authtype>localauth</authtype>")
                output.append("\t\t<email>%s</email>\n\t\t<enddate></enddate>" % teacher[1]['email'])
                output.append("\t\t<firstname>%s</firstname>" % teacher[1]['first_name'])
                output.append("\t\t<groupID>%s</groupID>" % teacher[0])
                output.append("\t\t<lastname>%s</lastname>" % teacher[1]['last_name'])
                output.append("\t\t<middlename></middlename>\n\t\t<startdate></startdate>")
                output.append("\t\t<teacherID>%s</teacherID>\n\t</student>" % teacher[1]['login_id'])            
            output.append("</teachers>")
        if students:
            output.append("<students>")
            for student in students:
                output.append("\t<student username=\"%s\">" % student[1]['login_id'])
                output.append("\t\t<autharg></autharg>\n\t\t<authtype>localauth</authtype>")
                output.append("\t\t<email>%s</email>\n\t\t<enddate></enddate>" % student[1]['email'])
                output.append("\t\t<firstname>%s</firstname>" % student[1]['first_name'])
                output.append("\t\t<groupID>%s</groupID>" % student[0])
                output.append("\t\t<lastname>%s</lastname>" % student[1]['last_name'])
                output.append("\t\t<middlename></middlename>\n\t\t<startdate></startdate>")
                output.append("\t\t<studentID>%s</studentID>\n\t</student>" % student[1]['login_id'])
            output.append("</students>")


    if format == "flat":
        output.append("Content-type: text/plain")
        for teacher in teachers:
            entry = "instructor\t%s\t%s\t%s\t%s" % \
            (teacher[1]['login_id'],teacher[1]['email'],teacher[1]['first_name'],teacher[1]['last_name'])
            if not entry in output:
                output.append(entry)
        for student in students:
            entry = "student\t%s\t%s\t%s\t%s" % \
            (student[1]['login_id'],student[1]['email'],student[1]['first_name'],student[1]['last_name'])
            if not entry in output:
                output.append(entry)

    for line in output:
        print line

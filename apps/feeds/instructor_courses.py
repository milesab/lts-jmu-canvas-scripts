import os, sys, re, cgi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bin')))
import api_local
config = api_local.get_config()

if __name__ == '__main__':

    teacher_ids = cgi.FieldStorage().getvalue('id')
    teachers = teacher_ids.split(',')

    output = []

    enrollments = api_local.read_csv(config['export_dir'] + 'enrollments.csv', 'course_id')
    
    for teacher in teachers:
        output.append("\nTeacher: %s\n\ncourse_id (canvas_course_id)\tsection_id (canvas_section_id)" % teacher)
        for enrollment in enrollments:
            if enrollment['role'] == "teacher" and enrollment['user_id'] == teacher:
                cid = enrollment['course_id']
                ccid = enrollment['canvas_course_id']
                sid = enrollment['section_id']
                csid = enrollment['canvas_section_id']
                output.append("%s (%s)\t%s (%s)" % (cid,ccid,sid,csid))

    print "Content-type: text/plain\n";
    for line in output:
        print line

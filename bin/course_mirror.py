import zipfile, fnmatch, csv
import os, datetime
import urllib2, MultipartPostHandler, json
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import api_local, api_canvas

config = api_local.get_config()


import_file = config['local']['easel_home'] + 'data/temp/course_mirror.zip'
import_id_file = config['local']['easel_home'] + 'data/temp/course_mirror_id.txt'
temp_dir = config['local']['easel_home'] + 'data/temp/course_mirror/'


# Clear temp directory
def clear_tempfiles():
    api_canvas.import_clear(import_file,import_id_file)
    for file in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except OSError:
            pass


# Create or Remove Enrollments
def change_enroll(tcid,tsid,enrollments,status):
    for enrollment in enrollments:
        user = enrollment['user_id']
        role = enrollment['role']
        enroll_string.write("%s,%s,%s,%s,%s\n" % (tcid,user,role,tsid,status))    
    temp_fn = temp_dir + 'enrollments.csv'
    temp_file = open(temp_fn, "wb")
    temp_file.write(enroll_string.getvalue())
    temp_file.close()


# Create or Remove Section
def change_section(tcid,tsid,status):
    section_string.write("%s,%s,%s,%s,,\n" % (tsid,tcid,tsid,status))
    temp_fn = temp_dir + 'sections.csv'
    temp_file = open(temp_fn, "wb")
    temp_file.write(section_string.getvalue())
    temp_file.close()


if __name__ == '__main__':

    clear_tempfiles()

    course_list = []
    courses = api_local.read_csv(config['local']['export_dir'] + 'courses.csv','course_id')
    for course in courses:
        course_list.append(course['course_id'])

    section_list = []
    sections = api_local.read_csv(config['local']['export_dir'] + 'sections.csv','section_id')
    for section in sections:
        section_list.append((section['course_id'],section['section_id']))

    enrollments = api_local.read_csv(config['local']['export_dir'] + 'enrollments.csv','user_id')
    course_mirrors = api_local.read_csv(config['local']['easel_home'] + 'data/add_enroll/course_mirror.csv', 'target_course_id')

    section_string = StringIO()
    section_string.write("section_id,course_id,name,status,start_date,end_date\n")
    enroll_string = StringIO()
    enroll_string.write("course_id,user_id,role,section_id,status\n")


    for course_mirror in course_mirrors:
        tcid = course_mirror['target_course_id'].rstrip().replace(" ","")
        tsid = course_mirror['target_section_id'].rstrip().replace(" ","")
        scid = course_mirror['source_course_id'].rstrip().replace(" ","")
        ssid = course_mirror['source_section_id'].rstrip().replace(" ","")
        if tcid and tsid and scid and ssid and api_local.course_check(tcid,course_list):
            s_section = api_local.section_check(scid,ssid,section_list)
            t_section = api_local.section_check(tcid,tsid,section_list)
            if s_section:
                s_enroll = [e for e in enrollments if e['course_id'] == scid and e['section_id'] == ssid]
                if (not t_section and s_enroll):
                    change_section(tcid,tsid,"active")
                    change_enroll(tcid,tsid,s_enroll,"active")
                elif (t_section and s_enroll):
                    t_enroll = [e for e in enrollments if e['course_id'] == tcid and e['section_id'] == tsid]
                    to_add = api_local.diff_enroll(s_enroll,t_enroll)
                    to_del = api_local.diff_enroll(t_enroll,s_enroll)
                    if to_add:
                        change_enroll(tcid,tsid,to_add,"active")
                    if to_del:
                        change_enroll(tcid,tsid,to_del,"deleted")

            elif t_section:
                t_enroll = [e for e in enrollments if e['course_id'] == tcid and e['section_id'] == tsid]
                if t_enroll:
                    change_enroll(tcid,tsid,t_enroll,"deleted")
                change_section(tcid,tsid,"deleted")
                
    enroll_string.close()
    section_string.close()

    api_canvas.import_zip(import_file,temp_dir)
    api_canvas.import_submit(import_file,import_id_file)
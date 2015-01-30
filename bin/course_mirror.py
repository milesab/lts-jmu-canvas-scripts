import zipfile, fnmatch, csv
import os, datetime
import urllib2, MultipartPostHandler, json
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import config, api_canvas, api_local


import_file = config.easel_home + 'data/temp/course_mirror.zip'
import_id_file = config.easel_home + 'data/temp/course_mirror_id.txt'
temp_dir = config.easel_home + 'data/temp/course_mirror/'


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
    unique_enrollments = set(enrollments)
    for enrollment in unique_enrollments:
        user = enrollment[0]
        role = enrollment[1]
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

    all_courses = api_local.get_courses()
    all_sections = api_local.get_sections()

    section_string = StringIO()
    section_string.write("section_id,course_id,name,status,start_date,end_date\n")
    enroll_string = StringIO()
    enroll_string.write("course_id,user_id,role,section_id,status\n")

    mirror_file = open(config.easel_home + 'data/add_enroll/course_mirror.csv', 'r')
    mirror_lines = [line for line in mirror_file if line.strip()]
    mirror_file.close()
    mirror_lines.sort()

    for line in mirror_lines:
        if not line.strip():
            continue
        else:
            line = line.rstrip().replace(" ","")
            tcid,tsid,scid,ssid = line.split(",")
        if tcid and tsid and scid and ssid and api_local.course_check(tcid,all_courses):
            s_section = api_local.section_check(scid,ssid,all_sections)
            t_section = api_local.section_check(tcid,tsid,all_sections)
            if s_section:
                s_enroll = api_local.get_enrollments(scid,ssid)
                if (not t_section and s_enroll):
                    change_section(tcid,tsid,"active")
                    change_enroll(tcid,tsid,s_enroll,"active")
                elif (t_section and s_enroll):
                    t_enroll = api_local.get_enrollments(tcid,tsid)
                    to_add = api_local.diff_enroll(s_enroll,t_enroll)
                    to_del = api_local.diff_enroll(t_enroll,s_enroll)
                    if to_add:
                        change_enroll(tcid,tsid,to_add,"active")
                    if to_del:
                        change_enroll(tcid,tsid,to_del,"deleted")

            elif t_section:
                t_enroll = api_local.get_enrollments(tcid,tsid)
                if t_enroll:
                    change_enroll(tcid,tsid,t_enroll,"deleted")
                change_section(tcid,tsid,"deleted")
                
    enroll_string.close()
    section_string.close()

    api_canvas.import_zip(import_file,temp_dir)
    #api_canvas.import_submit()
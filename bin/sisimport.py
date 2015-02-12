import fileinput
import api_local, api_canvas

config = api_local.get_config()
easel_home = config['local']['easel_home']
import_file = easel_home + 'data/temp/sisimport.zip'
import_id_file = easel_home + 'data/temp/sisimport_id.txt'
import_dir = config['local']['import_dir']


# Return inverse status (active|deleted)
def reverse(status):
    if status == 'active':
        return 'deleted'
    elif status == 'deleted':
        return 'active'


# Make changes to enrollments based on enrollment_changes.csv in add_enroll
def enrollment_changes():
    matches = []
    enrollment_changes = api_local.read_csv(easel_home + 'data/add_enroll/enrollment_changes.csv', 'course_id')
    for enrollment_change in enrollment_changes:
        course_id = enrollment_change['course_id'].rstrip().replace(" ","")
        section_id = enrollment_change['section_id'].rstrip().replace(" ","")
        user_id = enrollment_change['user_id'].rstrip().replace(" ","")
        status = enrollment_change['status'].rstrip().replace(" ","")
        if course_id and section_id and user_id and status:
            linematch = course_id + ',' + user_id + ',student,' + section_id + ',' + reverse(status) + '\n'
            matches.append(linematch)

    for line in fileinput.input(import_dir + 'enrollments.csv', inplace=1):
        if line in matches:
            course_id,user_id,role,section_id,status = line.rstrip().split(",")
            print line.replace(status,reverse(status)),
        else:
            print line,


if __name__ == '__main__':

    api_canvas.import_clear(import_file,import_id_file)
    enrollment_changes()
    api_canvas.import_zip(import_file,import_dir)
    api_canvas.import_submit(import_file,import_id_file)

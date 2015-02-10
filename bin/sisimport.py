import fileinput
import api_local, api_canvas

config = api_local.get_config()


import_file = config['easel_home'] + 'data/temp/sisimport.zip'
import_id_file = config['easel_home'] + 'data/temp/sisimport_id.txt'


# Return inverse status (active|deleted)
def reverse(status):
    if status == 'active':
        return 'deleted'
    elif status == 'deleted':
        return 'active'


# Make changes to enrollments based on enrollment_changes.csv in add_enroll
def enrollment_changes():
    matches = []

    enrollment_changes = api_local.read_csv(config['easel_home'] + 'data/add_enroll/enrollment_changes.csv', 'course_id')
    for enrollment_change in enrollment_changes:
        course_id = enrollment_change['course_id'].rstrip().replace(" ","")
        section_id = enrollment_change['section_id'].rstrip().replace(" ","")
        user_id = enrollment_change['user_id'].rstrip().replace(" ","")
        status = enrollment_change['status'].rstrip().replace(" ","")
        if section_id and user_id and status:
            linematch = section_id + ',' + user_id + ',student,' + section_id + ',' + reverse(status) + '\n'
            matches.append(linematch)

    for line in fileinput.input(config['import_dir'] + 'enrollments.csv', inplace=1):
        if line in matches:
            course_id,user_id,role,section_id,status = line.rstrip().split(",")
            print line.replace(status,reverse(status)),
        else:
            print line,


if __name__ == '__main__':

    api_canvas.import_clear(import_file,import_id_file)
    enrollment_changes()
    api_canvas.import_zip(import_file,config['import_dir'])
    api_canvas.import_submit(import_file,import_id_file)

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


# Make changes to enrollments based on add_enroll CSV
def enrollment_changes():
    matches = []

    cf = open(config['easel_home'] + 'data/add_enroll/enrollment_changes.csv', 'r')
    for line in cf:
        if not line.strip():
            continue
        else:
            line = line.rstrip().replace(" ","")
            course,eid,status = line.split(",")
        if course and eid and status:
            linematch = course + ',' + eid + ',student,' + course + ',' + reverse(status) + '\n'
            matches.append(linematch)
    cf.close()

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
    #api_canvas.import_submit(import_file,import_id_file)

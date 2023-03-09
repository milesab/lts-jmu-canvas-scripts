# Python lib Used for easily writing over stdin or a list of files
import fileinput
# Modules created for simplifying interaction with local files and canvas API 
import api_local_three as api_local
import api_canvas_three
import trn_fyr

config = api_local.get_config() # Just retrieves "config.json" from ../conf/config.json
easel_home = config['local']['easel_home'] # "usr/local/easel/"
import_file = easel_home + 'data/temp/sisimport.zip' # "usr/local/easel/data/temp/sisimport.zip"
import_id_file = easel_home + 'data/temp/sisimport_id.txt' # "usr/local/easel/data/temp/sisimport_id.txt"
import_dir = config['local']['import_dir'] # "usr/local/easel/data/import/"

# Return inverse status (active|deleted)
def reverse(status):
    if status == 'active':
        return 'deleted'
    elif status == 'deleted':
        return 'active'

# Make changes to enrollments based on enrollment_changes.csv in add_enroll
def enrollment_changes():
    matches = []
    # Initializes enrollment_changes to list of dicts derived from file at "usr/local/easel/data/add_enroll/enrollment_changes.csv"
    # dict items are sorted by course_id
    enrollment_changes = api_local.read_csv(easel_home + 'data/add_enroll/enrollment_changes.csv', 'course_id')
    # For every item in every dict in enrollment changes, remove leading whitespace and any spaces
    for enrollment_change in enrollment_changes:
        course_id = enrollment_change['course_id'].rstrip().replace(" ","")
        section_id = enrollment_change['section_id'].rstrip().replace(" ","")
        user_id = enrollment_change['user_id'].rstrip().replace(" ","")
        status = enrollment_change['status'].rstrip().replace(" ","")
        # If the item has every field filled out, intialize linematch to concatenation of course_id, user_id, ',student', section_id, ',', and a REVERSAL of the current status
        # Why is this status reversed? 
        if course_id and section_id and user_id and status:
            linematch = f'{course_id},{user_id},student,{section_id},{reverse(status)}'
            # Add linematch to matches
            matches.append(linematch)
   # Iterates over each line of enrollments.csv
    for line in fileinput.input(import_dir + 'enrollments.csv', inplace=1):
        # If the enrollment was in matches
        line = line.strip('\n')
        if line in matches:
            # Strip leading whitespace in course_id, user_id, role, section_id, status.
            # Then split the line into an array with ',' as delimiter 
            course_id,user_id,role,section_id,status = line.rstrip().split(",")
            # Print out the line TO THE FILE, but replace every status with its reverse. 
            print(line.replace(status,reverse(status)))
        else:
            # if the line isn't in matches, then print it TO THE FILE without reversing status.
            print(line)
            
# So... say every status in "matches" was ACTIVE but is now DELETED after line 34. We go over every line in
# the enrollments.csv file, and if it's in matches, (meaining the status was changed to DELETED), do some formatting
# and split the diff attributes (course_id, user_id...) into an array, and replace status with its reverse.
# So the point of the reversing is to make sure that the operation being ordered in "enrollment changes" won't be done
# if the change has already happened, or if the status is already where the change wants it to be. We're
# just filtering out operations that wouldn't actually do anything...? by matching the opposite of the 
# intended status to the current status, we ensure that the current status facilitates the operation to be done. 


if __name__ == '__main__':

    # Just deletes temp files
    api_canvas_three.import_clear(import_file,import_id_file)
    
    # Prints out enrollments after changes applied
    enrollment_changes()
    trn_fyr.run_trn_fyr(config)
    
    # Takes import file (usr/local/easel/data/temp/sisimport.zip) and import dir 
    # (usr/local/easel/data/import/) and if the import directory has files in it, zip all .csv's together
    api_canvas_three.import_zip(import_file,import_dir)
    # If import_file exists, open it and use it to populate "params" dict. Use MultipartPostHandler 
    # to make request to "https://canvas.jmu.edu/api/v1/accounts/(ACCOUNT ID FROM CONFIG)/sis_imports.json"
    # get response and remove whitespace. Load response into json object, get import ID from this json
    # write this id to a text file and save it into the import ID file... 
    api_canvas_three.import_submit(import_file,import_id_file)
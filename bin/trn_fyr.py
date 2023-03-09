import csv

# I have not tested this on the hub. I also haven't tested this with the un-altered sisimpory.py file (that still uses urllib2, etc). 
# Even running the code on Python 2.7 didn't eliminate the issues with the imports.
def run_trn_fyr(config):
    trn_fyr_home = config['local']['trn_fyr_home']
    import_dir = config['local']['import_dir']
# .csv containing only FYR data
    finalFYR = import_dir + 'FYRcomplete.csv'
# Contains data from SA to be loaded into Canvas
# How will data be loaded in? What will the naming convention be? How should we keep logs? How do we handle old .csvs?
    inputFromSA = trn_fyr_home + 'FYR.csv'
    with open(finalFYR, 'w', newline='') as output:
        headers = 'course_id', 'user_id', 'role', 'section_id', 'status'
        writer = csv.writer(output)
        writer.writerow(headers)
    # Read the FYR file supplied by SA, add eIDs and the rest of the fields to .csv
        with open(inputFromSA, 'r') as SA_input:
            # If file doesn't have headers, start reading on line 0
            lines = SA_input.readlines()[1:]
            for line in lines:
                eId = line.strip("\n")
                completed_line = [
                    'Transfer_Enrollment_Modules_Fall_2023', eId, 'student', '', 'active']
                writer.writerow(completed_line)
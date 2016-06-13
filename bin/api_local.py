import os, json, csv, datetime

# Load local application settings
def get_config():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    config = json.loads(open("../conf/settings.json").read())
    return config
    

# Read CSV file into list of dicts
def read_csv(filepath,sortkey):
    csv_data = []
    current_row = 0
    csv_file = open(filepath, 'r')
    reader = csv.DictReader(csv_file, fieldnames=[], restkey='undefined-fieldnames', delimiter=',', quotechar='"')
    for row in reader:
        current_row += 1
        if current_row == 1:
            reader.fieldnames = row['undefined-fieldnames']
            continue
        if row[sortkey]:
            csv_data.append(row)
    csv_file.close()
    csv_data.sort(key=lambda x: x[sortkey])
    return csv_data


# Enrollment Diff
def diff_enroll(first,second):
    second_users = []
    for user in second:
        second_users.append(user['user_id'])
    return [enroll for enroll in first if enroll['user_id'] not in second_users]


# Build index from data and key
def build_index(data,key):
    return dict((d[key], dict(d, index=i)) for (i,d) in enumerate(data))


# Return number of hours since file was last modified
def file_age(filename):
    if os.path.isfile(filename):
        filename_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
        current_time = datetime.datetime.today()
        file_age = (current_time - filename_time).total_seconds() / 3600
        return int(file_age)
    else:
        return None
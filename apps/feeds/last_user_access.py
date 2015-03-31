import os, sys, cgi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bin')))
import api_local

config = api_local.get_config()
export_dir = config['local']['export_dir']
report_dir = config['local']['report_dir']


if __name__ == '__main__':

    search = cgi.FieldStorage().getvalue('search')
    search_strings = search.split(',')

    users = api_local.read_csv(export_dir + 'users.csv', 'login_id')
    user_index = api_local.build_index(users,key='canvas_user_id')

    lastaccess = api_local.read_csv(report_dir + 'last_user_access_csv.csv', 'user id')
    lastaccess_index = api_local.build_index(lastaccess,key='user id')

    output = []
    canvas_ids = []


    # Build array of canvas_user_ids with corresponding login_ids matching a search string
    for search_string in search_strings:
        for canvas_user_id in user_index:
            login_id = user_index[canvas_user_id]['login_id']
            if search_string.lower() in login_id:
                canvas_ids.append(canvas_user_id)

    # Build output from last access records for matching canvas_user_ids, referencing login_id
    for lastaccess_record in lastaccess:
        key = lastaccess_record['user id']
        if key in canvas_ids:
            output.append(user_index[key]['login_id'] + ',' + lastaccess_record['last access at'])

    print "Content-type: text/plain\n"
    output.sort()
    for line in output:
        print line

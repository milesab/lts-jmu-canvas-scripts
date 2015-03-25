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

    lastaccess = api_local.read_csv(report_dir + 'last_user_access.csv', 'user id')
    lastaccess_index = api_local.build_index(lastaccess,key='user id')

    output = []
    canvas_ids = []


    for user in search_strings:
        for canvas_user_id in user_index:
            login_id = user_index[canvas_user_id]['login_id']
            if user in login_id:
                canvas_ids.append((canvas_user_id,login_id))

    for record in canvas_ids:
        canvas_user_id = record[0]
        login_id = record[1]
        for lastaccess_record in lastaccess:
            if lastaccess_record['user id'] == canvas_user_id:
                output.append(login_id + ',' + lastaccess_record['last access at'])
                
    print "Content-type: text/plain\n"
    output.sort()
    for line in output:
        print line

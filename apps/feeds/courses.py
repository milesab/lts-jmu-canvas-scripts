import os, sys, re, cgi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bin')))
import api_local
config = api_local.get_config()


def default_terms(terms):
    def_terms = []
    for t in terms[-2:]:
        def_terms.append(t['term_id'])
    return def_terms


def get_term_id(sem,terms):
    full_names = { 'SP': 'Spring Semester 20', 'SM': 'Summer Session 20', 'FA': 'Fall Semester 20'}
    for short, full in full_names.iteritems():
        sem = sem.replace(short,full)
    term_id = [t['term_id'] for t in terms if t['name'] == sem]
    return term_id


def xlist_courses():
    xlc = []
    xlist = api_local.read_csv(config['local']['export_dir'] + 'xlist.csv','section_id')
    for xl in xlist:
        if xl['section_id']:
            xlc.append(xl['section_id'])
    return xlc


if __name__ == '__main__':

    terms = api_local.read_csv(config['local']['export_dir'] + 'terms.csv','term_id')
    courses = api_local.read_csv(config['local']['export_dir'] + 'courses.csv','course_id')
    exclude = xlist_courses()

    sem = cgi.FieldStorage().getvalue('sem')
    
    if sem:
        req_terms = get_term_id(sem,terms)
    else:
        req_terms = default_terms(terms)

    show_courses = []

    for course in courses:
        if course['status'] == "active" and course['term_id'] in req_terms and course['long_name'] and \
        course['course_id'] and course['course_id'] not in exclude:
            show_courses.append(course)
    
    print "Content-type: text/plain\n";

    for course in show_courses:
        try:
            print "%s %s" % (course['course_id'], course['long_name'])
            sys.stdout.flush()
        except IOError:
            pass
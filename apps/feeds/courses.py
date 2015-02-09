import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bin')))
import api_local
config = api_local.get_config()


def default_terms(terms):
    def_terms = []
    for t in terms[-2:]:
        def_terms.append(t['term_id'])
    return def_terms

def xlist_courses():
    xlc = []
    xlist = api_local.read_csv('xlist.csv')
    for xl in xlist:
        if xl['section_id']:
            xlc.append(xl['section_id'])
    return xlc


if __name__ == '__main__':

    terms = api_local.read_csv('terms.csv')
    req_terms = default_terms(sorted(terms))
    exclude = xlist_courses()
    courses = api_local.read_csv('courses.csv')
    show_courses = []

    print "Content-type: text/plain\n";

    for course in courses:
        if course['term_id'] in req_terms and course['long_name'] and course['course_id'] and course['course_id'] not in exclude:
            show_courses.append(course)
    
    show_courses.sort(key=lambda x: x['course_id'])
    for course in show_courses:
        try:
            print "%s %s" % (course['course_id'], course['long_name'])
            sys.stdout.flush()
        except IOError:
            pass
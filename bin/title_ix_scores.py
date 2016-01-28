from datetime import datetime
import pytz, logging
import json
import shutil, re, os
import api_local, api_canvas

config = api_local.get_config()
easel_home = config['local']['easel_home']
import_dir = config['local']['import_dir']
scores_file = easel_home + 'data/temp/title_ix_scores.txt'
logging.basicConfig(filename=config['local']['log_dir'] + 'title_ix_scores.log',level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
title_ix_course_id = config['title_ix']['course_id']
title_ix_quiz_id = config['title_ix']['quiz_id']

# Time Zone Definitions
gmt = pytz.timezone('GMT')
ltz = pytz.timezone(config['local']['timezone'])


# Pull time from filename
def date_from_filename(filename):
    m = re.search(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})-(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})", filename)
    if not m:
        return None
    return datetime(int(m.group('year')), int(m.group('month')), int(m.group('day')),
                    int(m.group('hour')), int(m.group('minute')), int(m.group('second')))


# Determine timestamp of most recent scorefile
def last_score():
    scorefiles = sorted([ f for f in os.listdir(easel_home + 'data/title_ix/') if f.startswith('scores-')])
    if scorefiles:
        lastscore = ltz.localize(date_from_filename('%s' % scorefiles[-1],))
        return lastscore
    else:
        logging.info('No Score files found, using course start_at value')
        course_start = api_canvas.get_courseinfo(title_ix_course_id)['start_at']
        lastscore = ltz.localize(datetime.strptime(course_start, '%Y-%m-%dT%H:%M:%SZ'))
        return lastscore


# Determine timestamp of last title_ix enrollment run
def last_run():
    lastrunfile = import_dir + 'title_ix/timestamp.txt'
    if os.path.isfile(lastrunfile):
        lastrun = ltz.localize(datetime.strptime(open(lastrunfile, 'r').read().strip(), '%Y%m%d-%H%M%S'))
        return lastrun
    else:
        logging.info('No lastrun file found, using course start_at value')
        course_start = api_canvas.get_courseinfo(title_ix_course_id)['start_at']
        lastrun = ltz.localize(datetime.strptime(course_start, '%Y-%m-%dT%H:%M:%SZ'))
        return lastrun


# Populate score file with new scores only
def create_scorefile():
    if lastscore > lastrun:
        logging.info('Appending to scorefile - lastscore: %s - lastrun  : %s' % (lastscore, lastrun))
        file = open(scores_file, 'a')
    else:
        logging.info('Writing new scorefile  - lastscore: %s - lastrun  : %s' % (lastscore, lastrun))
        file = open(scores_file, 'w')
    for student in score_data:
        if not student['user_id'] == teststudent_id:
            tixscore = None
            section_id = section_ids[student['section_id']]
            student_id = student_ids[student['user_id']]
            for sub in student['submissions']:
                user_id, quiz, qscore, qtime, = sub['user_id'], sub['assignment_id'], sub['score'], sub['submitted_at']
                if user_id == student['user_id']:
                    if int(quiz) == int(title_ix_quiz_id):
                        tixscore, tixtime = qscore, qtime
        if not None in (tixscore, tixtime):
            gmt_timestamp = datetime.strptime(tixtime, '%Y-%m-%dT%H:%M:%SZ')
            title_ix_timestamp = gmt.localize(gmt_timestamp).astimezone(ltz)
            if title_ix_timestamp > lastscore:
                if student_id in open(scores_file).read():
                    logging.info('Skipping duplicate score - %s' % student_id)
                else:
                    logging.info('Adding new score - %s' % student_id)
                    quiz_time = datetime.strptime(tixtime, '%Y-%m-%dT%H:%M:%SZ').strftime('%m%d%Y')
                    file.write('%s,%s,%s\n' % (student_id, quiz_time, section_id))
    file.close()


# Archive and publish score file
def publish_scorefile(timestamp):
    shutil.copy2(scores_file,import_dir + 'title_ix/titleix_jhr078.dat')
    if os.stat(scores_file).st_size > 0:
        shutil.copy2(scores_file,easel_home + 'data/title_ix/scores-%s.txt' % timestamp)


if __name__ == '__main__':

    lastscore = last_score()
    lastrun = last_run()

    # Map student ID to sis_user_id
    teststudent_id = None
    student_ids = {}
    student_data = api_canvas.get_students(title_ix_course_id)

    # Save students data for troubleshooting
    fout = open(easel_home + 'data/temp/title_ix_student_data.json', 'w')
    json.dump(student_data,fout)
    fout.close

    for student in student_data:
        if not student['name'] == "Test Student":
            key, value = student['id'], student['sis_user_id']
            student_ids[key] = value
        else:
            teststudent_id = student['id']

    # Map section ID to sis_section_id
    section_ids = {}
    section_data = api_canvas.get_sections(title_ix_course_id)

    # Save section data for troubleshooting
    fout = open(easel_home + 'data/temp/title_ix_section_data.json', 'w')
    json.dump(section_data,fout)
    fout.close

    for section in section_data:
        key, value = section['id'], section['sis_section_id']
        section_ids[key] = value

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    score_data = api_canvas.get_scores(student_data,title_ix_course_id)

    # Save grades data for troubleshooting
    fout = open(easel_home + 'data/temp/title_ix_score_data.json', 'w')
    json.dump(score_data,fout)
    fout.close

    create_scorefile()
    publish_scorefile(timestamp)

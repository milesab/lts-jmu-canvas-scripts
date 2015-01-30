#!/usr/bin/python
from datetime import datetime
import pytz
import json
import shutil, re, os
import config, api_canvas


# Time Zone Definitions
gmt = pytz.timezone('GMT')
ltz = pytz.timezone(config.local_timezone)


scores_file = config.easel_home + 'data/temp/scores.txt'


# Pull time from filename
def date_from_filename(filename):
	m = re.search(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})-(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})", filename)
	if not m:
		return None
	return datetime(int(m.group('year')), int(m.group('month')), int(m.group('day')),
                    int(m.group('hour')), int(m.group('minute')), int(m.group('second')))


# Determine timestamp of most recent scorefile
def last_score():
    scorefiles = sorted([ f for f in os.listdir(config.easel_home + 'data/mpe/') if f.startswith('scores-')])
    if scorefiles:
    	lastscore = ltz.localize(date_from_filename('%s' % scorefiles[-1],))
        return lastscore
    else:
    	print "No Score files found, exiting"
    	exit(1)


# Determine timestamp of last mpe enrollment run
def last_run():
    lastrunfile = config.import_dir + 'math_placement/timestamp.txt'
    if lastrunfile:
        lastrun = ltz.localize(datetime.strptime(open(lastrunfile, 'r').read().strip(), '%Y%m%d-%H%M%S'))
        return lastrun
    else:
        print "No lastrun file found, exiting"
        exit(1)


# Populate score file with new scores only
def create_scorefile():
    if lastscore > lastrun:
        print "Appending to scorefile\n  lastscore: %s\n  lastrun  : %s" % (lastscore, lastrun)
        file = open(scores_file, 'a')
    else:
        print "Writing new scorefile\n  lastscore: %s\n  lastrun  : %s" % (lastscore, lastrun)
        file = open(scores_file, 'w')
    for student in grade_data:
        if not student['user_id'] == teststudent_id:
                p1score, p2score, p3score, p4score = None, None, None, None
                key = student['user_id']
                student_id = student_ids[key]
                for sub in student['submissions']:
                    user_id, quiz, qscore, qtime = sub['user_id'], sub['assignment_id'], sub['score'], sub['submitted_at']
                    if user_id == key:
                        if quiz == config.mpe_quiz1:
                            p1score, p1time = qscore, qtime
                        if quiz == config.mpe_quiz2:
                            p2score, p2time = qscore, qtime
                        if quiz == config.mpe_quiz3:
                            p3score, p3time = qscore, qtime
                        if quiz == config.mpe_quiz4:
                            p4score, p4time = qscore, qtime
	if not None in (p1score, p2score, p3score, p4score):
	    gmt_timestamp = datetime.strptime(max(p1time, p2time, p3time, p4time), '%Y-%m-%dT%H:%M:%SZ')
	    mpe_timestamp = gmt.localize(gmt_timestamp).astimezone(ltz)
            if mpe_timestamp > lastscore:
                if student_id in open(scores_file).read():
                        print "Skipping duplicate score - %s" % student_id
                else:
                        print "Adding new score - %s" % student_id
                        calc_score = str(int(p1score) + int(p2score) + int(p3score)).zfill(4) + '00'
                        calc_time = datetime.strptime(max(p1time, p2time, p3time), '%Y-%m-%dT%H:%M:%SZ').strftime('%m%d%Y')
                        stat_score = str(int(p4score)).zfill(4) + '00'
                        stat_time = datetime.strptime(p4time, '%Y-%m-%dT%H:%M:%SZ').strftime('%m%d%Y')
                        file.write('%-11sMATHP      %s            CALC %s\n' % (student_id, calc_time, calc_score))
                        file.write('%-11sMATHP      %s            STAT %s\n' % (student_id, stat_time, stat_score))
    file.close()


# Archive and publish score file
def publish_scorefile():
    shutil.copy2(scores_file, config.import_dir + 'math_placement/mathp_jsa0005.dat')
    if os.stat(scores_file).st_size > 0:
        shutil.copy2(scores_file, config.easel_home + 'data/mpe/scores-%s.txt' % datetime.now().strftime('%Y%m%d-%H%M%S'))


if __name__ == '__main__':

    lastscore = last_score()
    lastrun = last_run()

    # Map student ID to sis_id
    teststudent_id = None
    student_ids = {}
    student_data = api_canvas.get_students(config.mpe_course_id)
    for student in student_data:
        if not student['name'] == "Test Student":
            key, value = student['id'], student['sis_user_id']
            student_ids[key] = value
        else:
            teststudent_id = student['id']

    grade_data = api_canvas.get_grades(student_data,config.mpe_course_id)
    create_scorefile()
    publish_scorefile()

    # Save students data for troubleshooting
    fout = open(config.log_dir + 'mpe_student_data.json', 'w')
    json.dump(student_data,fout)
    fout.close

    # Save grades data for troubleshooting
    fout = open(config.log_dir + 'mpe_grade_data.json', 'w')
    json.dump(grade_data,fout)
    fout.close

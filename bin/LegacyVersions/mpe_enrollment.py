import api_local, api_canvas
import shutil, os
from datetime import datetime
from exceptions import Exception
import logging

config = api_local.get_config()
easel_home = config['local']['easel_home']
import_file = config['local']['import_dir'] + 'math_placement/mathp_enrollment.csv'
import_id_file = easel_home + 'data/temp/mpe_importid.txt'
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
temp_dir = os.path.join(easel_home, 'data', 'temp')
export_dir = config['local']['export_dir']
waiting_file = os.path.join(temp_dir, 'mpe_waiting_to_load.csv')
temp_import_file = os.path.join(temp_dir, 'mpe_import_temp.csv')


if __name__ == '__main__':

    
    # Archive a copy of the MPE enrollment file
    if os.stat(import_file).st_size > 41:
        shutil.copy2(import_file,easel_home + 'data/mpe/enrollments/mathp_enrollment-%s.csv' % timestamp)

    # Prepare logger
    FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
    logging.basicConfig(format=FORMAT,
                        filename=os.path.join(temp_dir, 'mpe_compare.log'),
                        level=logging.INFO)
    logger = logging.getLogger('mpe_enrollment')

    # copy the incoming peoplesoft data file to a new file so we don't mess it up
    shutil.copy2(import_file, temp_import_file)

    # load ALL Canvas users into memory
    with open(export_dir + 'users.csv') as users:
              users_clob = users.read()

    # if mpe_waiting_to_load exists, open it and append to import file
    try:
        waiting_to_load = open(waiting_file, 'r')
    except:
        logger.info('Error opening mpe_waiting_to_load.csv')
    else:
        count = 0
        with open(temp_import_file, 'a') as appended:
            for line in waiting_to_load:
                count += 1
                appended.write(line)
            logger.info('{} lines added to new import file from waiting file'.format(count))
        waiting_to_load.close()
        
    # store entire newly appended import file in memory
    imported_lines = []
    with open(temp_import_file) as imported_file:
        for line in imported_file.readlines():
            imported_lines.append(line)
            
    # now look at newly appended import file, check each user against canvas users,
    # and open both files and write to each, as appropriate
    wait_count = 0
    import_count = 0
    with open(temp_import_file, 'w') as imported_file:
        with open(waiting_file, 'w') as waiting_to_load:
            for line in imported_lines:
                eid = line.split(',')[1]
                if eid not in users_clob:
                    waiting_to_load.write(line)
                    wait_count += 1
                else:
                    imported_file.write(line)
                    import_count += 1
        if os.stat(waiting_file).st_size > 0:
             shutil.copy2(waiting_file,easel_home + 'data/mpe/enrollments/archive/waiting_to_load-%s.csv' % timestamp)
        logger.info('{} lines added to clean import file'.format(import_count))
        logger.info('{} lines added to waiting file'.format(wait_count))

    api_canvas.import_submit(temp_import_file,import_id_file)

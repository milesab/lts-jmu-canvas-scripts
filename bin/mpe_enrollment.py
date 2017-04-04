import api_local, api_canvas
import shutil, os
from datetime import datetime

config = api_local.get_config()
easel_home = config['local']['easel_home']
import_file = config['local']['import_dir'] + 'math_placement/mathp_enrollment.csv'
import_id_file = easel_home + 'data/temp/mpe_importid.txt'
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')


if __name__ == '__main__':

    # Archive a copy of the MPE enrollment file
    if os.stat(import_file).st_size > 0:
        shutil.copy2(import_file,easel_home + 'data/mpe/enrollments/mathp_enrollment-%s.csv' % timestamp)

    #api_canvas.import_submit(import_file,import_id_file)

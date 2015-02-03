import api_local, api_canvas

config = api_local.get_config()


import_file = config['import_dir'] + 'math_placement/mathp_enrollment.csv'
import_id_file = config['easel_home'] + 'data/temp/mathp_importid.txt'


if __name__ == '__main__':

    api_canvas.import_submit(import_file,import_id_file)
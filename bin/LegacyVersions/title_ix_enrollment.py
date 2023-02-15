import api_local, api_canvas

config = api_local.get_config()
easel_home = config['local']['easel_home']
import_file = config['local']['import_dir'] + 'title_ix/enrollments.csv'
import_id_file = easel_home + 'data/temp/title_ix_importid.txt'


if __name__ == '__main__':

    api_canvas.import_submit(import_file,import_id_file)

import os, datetime, time
import api_local, api_canvas

config = api_local.get_config()
easel_home = config['local']['easel_home']
export_file = easel_home + 'data/temp/sisexport.zip'
export_id_file = easel_home + 'data/temp/sisexport_id.txt'
export_dir = config['local']['export_dir']
export_age = int(config['local']['export_age'])
export_checkfile = export_dir + 'courses.csv'

# Generate new export
def generate_export():
    #api_canvas.export_submit(export_id_file)
    export_id = int(open(export_id_file, 'r').read().strip())
    progress = 0
    while progress < 100:
        time.sleep(60)
        progress = api_canvas.job_status(export_id,'export')['progress']
    file_url = api_canvas.job_status(export_id,'export')['attachment']['url']
    try:
        api_canvas.export_download(file_url,export_file)
    except Exception as e:
        print("error: " + str(e))
        print("Export download failed, keeping previous export")


if __name__ == '__main__':
    if api_local.file_age(export_checkfile) is None or api_local.file_age(export_checkfile) > export_age:
        generate_export()
		
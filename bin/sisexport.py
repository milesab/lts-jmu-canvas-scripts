import os, datetime, time
import api_local, api_canvas
config = api_local.get_config()


export_file = config['easel_home'] + 'data/temp/sisexport.zip'
export_id_file = config['easel_home'] + 'data/temp/sisexport_id.txt'


# Generate new export
def generate_export():
    api_canvas.export_submit(export_id_file)
    export_id = int(open(export_id_file, 'r').read().strip())
    progress = 0
    while progress < 100:
        time.sleep(60)
        progress = api_canvas.job_status(export_id,'export')['progress']
    file_url = api_canvas.job_status(export_id,'export')['attachment']['url']
    try:
        api_canvas.export_download(file_url,export_file)
    except:
        print "Export download failed, keeping previous export"


# Check if export has been updated in the last 5 hours
def export_time():
    t = os.path.getmtime(config['export_dir'])
    if (datetime.datetime.today() - datetime.datetime.fromtimestamp(t)) < datetime.timedelta(hours=0):
        return False
    else:
        return True


if __name__ == '__main__':

    if export_time():
        generate_export()
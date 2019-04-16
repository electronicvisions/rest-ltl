import requests
import os
import json

 
def upload_files(experiment_name, persist_filename, experiment_filename):
    persist_file = os.path.basename(persist_filename)
    experiment_file = os.path.basename(experiment_filename)

    multipart_form_data = {
        'wafer_config': (persist_filename, open(persist_file, 'rb')),
        'wafer_script': (experiment_filename, open(experiment_file, 'rb')),
    }

    response = requests.post('http://hel.kip.uni-heidelberg.de:22066/upload/{}'.format(experiment_name),
                             files=multipart_form_data)
    print(response.status_code)

def query_status(user_name):
    response = requests.get('http://hel.kip.uni-heidelberg.de:22066/status/{}'.format(user_name))
    print(response.status_code)
    data = response.json()
    print len(data)
    if len(data) > 0:
        print(data[0]['slurm_state'])
        print(int(data[0]['job_id']))

def download_file(experiment_name, filename):
    response = requests.get('http://hel.kip.uni-heidelberg.de:22066/download/{}/{}'.format(experiment_name, filename))
    if response.status_code == 200:
        with open(filename, 'wb') as fd:
            fd.write(response.content)

def submit(experiment_name):
    # all optional?
    payload = {'wafer_module': 33, 'command': r'-c \"print(\'Here I AM\')\"', 'software_version': 'nmpm_software/current'}
    headers = {'content-type': 'application/json'}

    response = requests.post('http://hel.kip.uni-heidelberg.de:22066/submit/{}'.format(experiment_name), data=json.dumps(payload), headers=headers)

    print(response.content)
    print(response.status_code)

#upload_files('cpehle_hats_im_griff', 'shit.txt', 'shit2.txt')

#query_status('nmpi')

#download_file('cpehle_hats_im_griff', 'shit.txt')

submit('cpehle_hats_im_griff')

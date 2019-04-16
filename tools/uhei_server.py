import flask
import json
import os
import logging
import shlex
import time
from datetime import datetime, timedelta

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload'

@app.route('/status/<user_name>')
def status(user_name):
    d = datetime.today() - timedelta(days=2)
    start_time = d.strftime('%Y-%m-%d')
    partition = 'experiment'

    result = os.popen('sacct -S {} -u {} -b -n -P -r {}'.format(start_time, user_name, partition)).read()
    response = []

    for row in result.split('\n')[:-1]:
        job_id, state, _ = row.split('|')
        response.append({'job_id': job_id, 'slurm_state': state})

    response = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/download/<experiment_name>/<file_name>')
def download(experiment_name, file_name):
    working_dir = os.path.join(app.config['UPLOAD_FOLDER'], experiment_name)
    return flask.send_from_directory(working_dir, file_name)

@app.route('/submit/<experiment_name>', methods=['POST'])
def submit(experiment_name):
    config = flask.request.get_json()
    wafer_module = config['wafer_module']
    command = config['command']
    software_version = config.get('software_version', 'nmpm_software/current')
    working_directory = os.path.join(app.config['UPLOAD_FOLDER'], experiment_name)

    app.logger.info(json.dumps(config))
    app.logger.info(working_directory)

    cwd = os.getcwd()
    os.chdir(working_directory)

    output = ''
    try:
        command = shlex.split(command)
        shell_command = ['sbatch', '-p', 'experiment', '--wmod', str(wafer_module), '../../wafer_wrap.sh', 'singularity', 'exec', '--app',
              'visionary-wafer', '$CONTAINER_IMAGE_NMPM_SOFTWARE', 'python'] + command
        start_time = time.time()

        out = os.popen(' '.join(shell_command))
        output = out.read()
        slurm_jobid = int(output.split(' ')[3])
        data = {'result': 'ok', 'job_id': slurm_jobid, 'start_time': start_time }

    except:
        data = {'result': 'failed', 'output': output}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )

    os.chdir(cwd)
    return response



@app.route('/upload/<experiment_name>', methods=['POST'])
def upload(experiment_name):
    wafer_config = flask.request.files['wafer_config']
    wafer_script = flask.request.files['wafer_script']
    os.mkdir(os.path.join('upload', experiment_name))
    wafer_config.save(os.path.join(app.config['UPLOAD_FOLDER'], experiment_name, wafer_config.filename))
    wafer_script.save(os.path.join(app.config['UPLOAD_FOLDER'], experiment_name, wafer_script.filename))

    data = {'result': 'ok'}

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == "__main__":
    app.run()

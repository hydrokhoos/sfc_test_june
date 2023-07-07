import subprocess
import os
from flask import Flask, send_file, request
import json

from ndn.encoding import Name


app = Flask(__name__)


RUNNING = {}


@app.route("/download", methods=["GET"])
def cat_content():
    if request.get_json()["contentname"] == None:
        contentname = '/sample.txt'
    contentname = request.get_json()["contentname"]
    output_file = os.path.join('/', contentname.split('/')[-1])
    with open(output_file, 'wb') as f:
        subprocess.run(['ndncatchunks', contentname], stdout=f)
    return send_file(output_file)


@app.route('/put_data', methods=["POST"])
def put_data():
    contentname = request.get_json()["contentname"]
    contentname = Name.to_str(Name.normalize(contentname))
    content = request.get_json()["content"]
    with open('/src/' + contentname.replace('/', '-')[1:], 'w') as f:
        f.write(content)
    print(contentname, ':', content)
    with open('/src/' + contentname.replace('/', '-')[1:], "r") as f:
        process = subprocess.Popen(
            ['ndnputchunks', contentname, '-q'], stdin=f)
    return json.dumps({
        "message": "OK",
        "contentname": contentname,
        "content": content
    })


@app.route('/put_service', methods=["POST"])
def put_service():
    service_name = str(request.get_json()["service_name"])
    service_ip = str(request.get_json()["service_ip"])
    service_port = str(request.get_json()["service_port"])
    service_process = subprocess.Popen(
        ['python3', '/src/service_agent.py', service_name, service_ip, service_port])
    subprocess.run(['nlsrc', 'advertise', service_name])
    RUNNING[service_name] = {
        'process': service_process,
        'ip': service_ip,
        'port': service_port
    }
    return json.dumps({
        "message": "OK",
        "service_name": service_name,
        "service_ip": service_ip,
        "service_port": service_port
    })


@app.route('/del_service', methods=["DELETE"])
def del_service():
    service_name = request.get_json()["service_name"]
    try:
        process = RUNNING[service_name]["process"]
    except KeyError:
        return json.dumps({
            "message": "Service not found",
            "service_name": service_name
        })
    process.kill()
    del (RUNNING[service_name])
    subprocess.run(['nlsrc', 'withdraw', service_name])
    return json.dumps({
        "message": "Service deleted",
        "service_name": service_name
    })


@app.route('/', methods=["GET"])
def get_top():
    return 'can you see me?\n'


@app.route('/running', methods=["GET"])
def get_running():
    print([str(s) for s in RUNNING.keys()])
    return json.dumps([str(s) for s in RUNNING.items()])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)

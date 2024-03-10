from flask import Blueprint, render_template, request, url_for, flash, redirect
import json
import subprocess
from subprocess import check_output
from subprocess import Popen
import time

views = Blueprint(__name__, "views")

@views.route("/", methods=['GET','POST'])
def home():
    sys = dict()
    sys['status'] = 0
    sys['ip'] = "0.0.0.0"

    if request.method == 'GET':
        ret = subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/status_artnet.sh")
        sys['status'] = ret.returncode

        get_ipp_cmd = "/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/get_ipaddr.sh"
        p = subprocess.Popen([get_ipp_cmd], stdout=subprocess.PIPE)
        out, err = p.communicate()
        sys['ip'] = str(out.decode("utf-8"))
        
        return render_template("index.html", sys = sys)

@views.route("/matrix-config", methods=['GET','POST'])
def matrix_config():
    new_config = ''
    if request.method == 'GET':
        with open('/home/dietpi/rpi-red-led-matrix/bindings/python/samples/fixture-config.json', 'r') as f:
            config = json.load(f)

        return render_template("matrix-config.html", config_data = config)

@views.route('/submit_config', methods=['GET','POST'])
def submit_config():
    with open('/home/dietpi/rpi-red-led-matrix/bindings/python/samples/fixture-config.json', 'r') as f:
        config = json.load(f)
    
    for section in config:
        for parameter in config[section]:
            #print("Key: {} Value: {}".format(parameter,config[section][parameter]))
            new_value = request.form[parameter]
            print("{}:{}".format(parameter,new_value))
            config[section][parameter] = new_value
        
    with open('/home/dietpi/rpi-red-led-matrix/bindings/python/samples/fixture-config.json', 'w') as f:
        json.dump(config, f)
    
    return redirect(url_for('views.matrix_config'))

@views.route('/submit_defaults', methods=['GET','POST'])
def submit_defaults():
    # Not implemented
    return redirect(url_for('views.matrix_config'))

@views.route('/sys_test', methods=['GET','POST'])
def sys_test():
    print ("Testing fixture...")
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/run_test.sh")
    return redirect(url_for('views.home'))

@views.route('/sys_test_stop', methods=['GET','POST'])
def sys_test_stop():
    print ("Stopping test fixture...")
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/stop_test.sh")
    return redirect(url_for('views.home'))

@views.route('/sys_start', methods=['GET','POST'])
def sys_start():
    print ("Starting...")
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/run_artnet.sh")
    return redirect(url_for('views.home'))

@views.route('/sys_stop', methods=['GET','POST'])
def sys_stop():
    print ("Stopping...")
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/stop_artnet.sh")
    return redirect(url_for('views.home'))

@views.route('/sys_restart', methods=['GET','POST'])
def sys_restart():
    print ("Restarting firmware...")
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/stop_artnet.sh")
    time.sleep(2)
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/run_artnet.sh")
    return redirect(url_for('views.home'))

@views.route('/sys_reboot', methods=['GET','POST'])
def sys_reboot():
    #if request.method == 'POST':
    print ("Rebooting System...")
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/stop_artnet.sh")
    time.sleep(1)
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/scripts/stop_test.sh")
    time.sleep(2)
    subprocess.call(["sudo","reboot"])
    return redirect(url_for('views.home'))

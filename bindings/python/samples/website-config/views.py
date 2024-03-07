from flask import Blueprint, render_template, request, url_for, flash
import json
import subprocess
from subprocess import Popen
import time

views = Blueprint(__name__, "views")

@views.route("/", methods=['GET','POST'])
def home():
    system_status = 0

    if request.method == 'POST':
        #new_config = request.form['form-config']
        #print(new_config)
        return render_template('index.html')
    else:
        ret = subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/status_artnet.sh")
        system_status = ret.returncode
        print("System status: {}".format(system_status))
        return render_template("index.html", status = system_status)

@views.route("/matrix-config", methods=['GET','POST'])
def matrix_config():
    new_config = ''
    if request.method == 'GET':
        with open('../fixture-config.json', 'r') as f:
            config = json.load(f)

        return render_template("matrix-config.html", config_data = config)

@views.route('/submit_config', methods=['GET','POST'])
def submit_config():
    with open('../fixture-config.json', 'r') as f:
        config = json.load(f)
    
    for section in config:
        for parameter in config[section]:
            #print("Key: {} Value: {}".format(parameter,config[section][parameter]))
            new_value = request.form[parameter]
            print("{}:{}".format(parameter,new_value))
            config[section][parameter] = new_value
        
    with open('../fixture-config.json', 'w') as f:
        json.dump(config, f)

    # Now get the dictionary and put it into a json
    # Save json to new fixture-config.json
    
    return render_template("matrix-config.html", config_data = config)

@views.route('/sys_test', methods=['GET','POST'])
def sys_test():
    print ("Testing fixture...")
    return render_template("index.html", status = 1)

@views.route('/sys_start', methods=['GET','POST'])
def sys_start():
    print ("Starting...")
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/run_artnet.sh")
    return render_template("index.html", status = 0)

@views.route('/sys_stop', methods=['GET','POST'])
def sys_stop():
    print ("Stopping...")
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/stop_artnet.sh")
    return render_template("index.html", status = 1)

@views.route('/sys_restart', methods=['GET','POST'])
def sys_restart():
    print ("Restarting firmware...")
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/stop_artnet.sh")
    time.sleep(2)
    subprocess.run("/home/dietpi/rpi-red-led-matrix/bindings/python/samples/run_artnet.sh")
    return render_template("index.html", status = 0)

@views.route('/sys_reboot', methods=['GET','POST'])
def sys_reboot():
    #if request.method == 'POST':
    print ("Rebooting System...")
    return render_template("index.html", status = 1)




    
    
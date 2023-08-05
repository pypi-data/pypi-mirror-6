import datetime
import os
import sys

def setup_config():
    config_path = os.path.expanduser(os.path.join('~', '.config', 'timetracker'))
    config_filename = 'timetracker.conf'

    if not os.path.exists(config_path):
        os.makedirs(config_path)

    config_path = os.path.join(config_path, config_filename)
    
    if not os.path.exists(config_path):
        config_file = open(config_path, 'w+')
        config_file.write("root = '~/timetracker'\n")
        config_file.write("time_format = '%H:%M'\n")
        config_file.close()

setup_config()
settings_path = os.path.expanduser(os.path.join('~', '.config', 'timetracker', 'timetracker.conf'))
config = {}
execfile(settings_path, config)

if ('root' not in config) or (type(config['root']) != str):
    print "Couldn't parse root in config file."
    sys.exit()
if ('time_format' not in config) or (type(config['time_format']) != str):
    print "Couldn't parse time_format in config file."
    sys.exit()


def get_file():
    global config

    root = config['root'] 
    root = os.path.expanduser(root)

    month = str(datetime.datetime.now().month)
    year = str(datetime.datetime.now().year)
    day = str(datetime.datetime.now().day)

    filename = day + '.log'

    full_path = os.path.join(root, year, month)

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    full_path = os.path.join(full_path, filename)
    
    f = open(full_path, 'a+')

    return f

def log(note):
    time_format = config['time_format']

    f = get_file()
     
    date = datetime.datetime.now().strftime(time_format)
    note = "{0}: {1}\n".format(date, note)
    
    f.write(note)
    f.close()


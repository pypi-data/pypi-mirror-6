#!C:\Python27\python.exe
# -*- coding: utf-8 -*-


import os
import sys
import shutil
import pkgutil

##===============================================================
##     INSTALL DJANGO AND EXTENSIONS TO BE SURE
##===============================================================

import subprocess
from PyQt4.QtCore import QSettings
QSettings('pyinstruments', 'pyinstruments').setValue('database_file', '')

#def set_environment_variable_on_windows(name, value):
#    subprocess.call(['setx', name, value])
#    os.environ[name] = value

subprocess.call(['pip', 'install', 'django'])
#set_environment_variable_on_windows('DJANGO_SETTINGS_MODULE', 
#                                    'pyinstruments.datastore.settings')
subprocess.call(['pip', 'install', 'django-model-utils'])
subprocess.call(['pip', 'install', 'django-utils'])
subprocess.call(['pip', 'install', 'django_evolution'])

##===============================================================
##     CREATE DESKTOP SHORTCUT
##===============================================================
curvefinder = pkgutil.get_loader("pyinstruments.curvefinder")
pyinstrumentsdb = pkgutil.get_loader("pyinstruments.pyhardwaredb")

try:
    DESKTOP_FOLDER = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
except NameError:
    print 'could not locate windows desktop folder, no shortcuts will be created'
else:
    CURVEFINDER_NAME = 'curvefinder.lnk'
    PYINSTRUMENTSDB_NAME = 'pyinstrumentsdb.lnk'
    
    create_shortcut(
            os.path.join(sys.prefix, 'python.exe'), # program
            'Description of the shortcut', # description
            CURVEFINDER_NAME, # filename
            os.path.join(curvefinder.filename, 'run.py'), # parameters
            ''#, # workdir
            #os.path.join(os.path.dirname(my_package.__file__), 'favicon.ico'), # iconpath
        )
    create_shortcut(
            os.path.join(sys.prefix, 'python.exe'), # program
            'Description of the shortcut', # description
            PYINSTRUMENTSDB_NAME, # filename
            os.path.join(pyinstrumentsdb.filename, 'run.py'), # parameters
            ''#, # workdir
            #os.path.join(os.path.dirname(my_package.__file__), 'favicon.ico'), # iconpath
        )
    
    # move shortcut from current directory to DESKTOP_FOLDER
    shutil.move(os.path.join(os.getcwd(), CURVEFINDER_NAME),
                os.path.join(DESKTOP_FOLDER, CURVEFINDER_NAME))
    shutil.move(os.path.join(os.getcwd(), PYINSTRUMENTSDB_NAME),
                os.path.join(DESKTOP_FOLDER, PYINSTRUMENTSDB_NAME))
    # tell windows installer that we created another
    # file which should be deleted on uninstallation
    file_created(os.path.join(DESKTOP_FOLDER, CURVEFINDER_NAME))
    file_created(os.path.join(DESKTOP_FOLDER, PYINSTRUMENTSDB_NAME))
    
    
    
    




#build_folder = os.path.join(os.environ['TEMP'], 'pip_build_' + os.environ['USERNAME'], 'pyhardware')
#if os.path.exists(build_folder):
#    shutil.rmtree(build_folder)    
#if subprocess.call(['pip', 'install','pyhardware', '-I', '-U']):
#    raise RuntimeError('problem installing pyhardware')
#if subprocess.call(['pip', 
#                     'install',
#                     'pyinstruments-curve', 
#                     '-I', 
#                     '-U']):
#    raise RuntimeError('problem installing pyinstruments-curve')
==========================
pyBM: Python Build Monitor
==========================

Welcome to pyBM!

A python build monitor. Initially written to work on a Raspberry Pi and monitor Jenkins jobs

Home page:
    https://bitbucket.org/jhendriks/pybm

Raspian quick start:
    sudo apt-get update
    sudo apt-get install python-setuptools
    sudo easy_install pip
    sudo pip install setuptools --no-use-wheel --upgrade (needed on raspian 2013-12-20 image)
    sudo pip install pybm
    python pyBM.py <jenkins url> <view to visualise>
    Press "i" to see ip information and use Esc to exit the application

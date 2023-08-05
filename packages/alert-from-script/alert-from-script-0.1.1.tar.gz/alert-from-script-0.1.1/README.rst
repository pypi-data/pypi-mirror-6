alert_from_script
=================

Generate SNS alerts from any command.

Installation
============

::

$ sudo python setup.py install

Usage
=====

::

  usage: alert-from-script [-h] sns_topic sns_subject script

  Runs a script and sends the stdout and stderr to SNS in case exit != 0.

  positional arguments:
    sns_topic    ARN of SNS topic to publish to.
    sns_subject  Subject used for SNS messages.
    script       The script to run. Includes all args to run.

  optional arguments:
    -h, --help   show this help message and exit

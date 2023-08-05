import os
import argparse
import subprocess
import tempfile

import boto

def main():
    parser = argparse.ArgumentParser(description='Runs a script and sends the stdout and stderr to SNS in case exit != 0.')
    
    parser.add_argument('sns_topic', type=str, help='ARN of SNS topic to publish to.')
    parser.add_argument('sns_subject', type=str, help='Subject used for SNS messages.')
    parser.add_argument('script', type=str, help='The script to run. Includes all args to run.')
    parser.add_argument('--aws-access-key-id',type=str, help='Optional AWS Access Key Id.  Will use environment variables and instance profiles if not set.')
    parser.add_argument('--aws-secret-access-key-id',type=str, help='Optional AWS Access Key Id.  Will use environment variables and instance profiles if not set.')
    
    if args.aws_access_key_id:
        os.environ
    
    args = parser.parse_args()

    stdout = tempfile.TemporaryFile()
    stderr = tempfile.TemporaryFile()
    
    return_code = subprocess.call(args.script, shell=True, stdout=stdout, stderr=stderr)
    
    if return_code != 0:
        stdout.seek(0)
        stderr.seek(0)
        
        message = "COMMAND:\n%s\n\nSTDOUT:\n%s\n\nSTDERR:\n%s" % (args.script, stdout.read(), stderr.read())
        
        sns_conn.publish(topic=args.sns_topic, message=message, subject=args.sns_subject)
    
if __name__ == '__main__':
    main()
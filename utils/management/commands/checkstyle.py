import os
import subprocess

from django.core.management.base import BaseCommand

VALIDATOR_ARGS = {
    'pep8': ['--repeat', '--ignore', 'E501,E128'],
    'pyflakes': [],
}

DIR_INCLUDES = []
DIR_EXCLUDES = ['.git', '.elasticbeanstalk', '.ebextensions', 'migrations']
FILE_INCLUDES = ['.py']
FILE_EXCLUDES = ['settings.py', 'settings_local', 'manage.py', '.pyc']


class Command(BaseCommand):
    help = 'Checks code for errors'

    def handle(self, *args, **options):
        for root, dirs, files in os.walk('.'):
            dir_included = [dirname for dirname in DIR_INCLUDES if dirname in root]
            dir_excluded = [dirname for dirname in DIR_EXCLUDES if dirname in root]

            if dir_excluded and not dir_included:
                continue

            for filename in files:
                filetype_included = [filetype for filetype in FILE_INCLUDES if filetype in filename]
                filetype_excluded = [filetype for filetype in FILE_EXCLUDES if filetype in filename]

                if filetype_included and not filetype_excluded:
                    path = os.path.join(root, filename)
                    output = ''
                    for validator in 'pyflakes', 'pep8':
                        cmd = [validator, path]
                        cmd.extend(VALIDATOR_ARGS[validator])
                        cmd_output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                        output += ''.join(cmd_output)
                    if output:
                        print output

import shlex
import subprocess


def exec_command(cmd: str):
    command = shlex.split(cmd)
    result = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)

    return result.stdout.read()

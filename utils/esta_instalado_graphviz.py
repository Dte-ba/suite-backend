import sys

from subprocess import Popen, PIPE

def check_program_exists(name):
    p = Popen(['/usr/bin/which', name], stdout=PIPE, stderr=PIPE)
    p.communicate()
    return p.returncode == 0

if not check_program_exists("dot"):
    rojo = "[00;31m"
    negro = "[00;00m"
    print(rojo + "No tienes instalado graphviz (ver README.md)" + negro)
    sys.exit(1)

sys.exit(0)



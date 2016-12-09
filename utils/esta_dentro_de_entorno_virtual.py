import sys

if not hasattr(sys, 'real_prefix'):
    rojo = "[00;31m"
    negro = "[00;00m"
    print(rojo + "No estas en un entorno virtual (ver README.md)" + negro)
    sys.exit(1)

sys.exit(0)

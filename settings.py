import sys

system = sys.platform

global cls

cls = "cls"

if system == 'linux' or system == 'darwin':
    cls = "clear"
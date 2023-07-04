import subprocess
import sys
import os

project_path = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
subprocess.run(['autopep8', "--recursive", "--in-place",
               "--aggressive", "--aggressive", "."], cwd=project_path)

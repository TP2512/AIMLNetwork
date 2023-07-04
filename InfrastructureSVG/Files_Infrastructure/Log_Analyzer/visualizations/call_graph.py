import subprocess
import os

project_name = 'Log_Analyzer'
project_path = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
project_python_files_path = '**/*.py'
dot_file_store_folder_path = os.path.realpath(
    os.path.join(os.path.dirname(__file__)))
dot_file_name = project_name + '_call_graph.dot'
png_file_name = project_name + '_call_graph.png'
dot_file_path = os.path.join(dot_file_store_folder_path, dot_file_name)
png_file_path = os.path.join(dot_file_store_folder_path, png_file_name)

dot_file = open(dot_file_path, "w")

result = subprocess.run(
    [r'C:\Users\rblumberg\main\projects\InfrastructureSVG\venv\Scripts\pyan3.exe',
     project_python_files_path,
     '--uses',
     '--defines',
     '--colored',
     '--grouped',
     '--dot'],
    stdout=dot_file,
    cwd=project_path,
)
subprocess.run(['dot', '-T', 'png', '-Granksep=2.0',
               '-Grankdir=LR', dot_file_path, '-o', png_file_path])

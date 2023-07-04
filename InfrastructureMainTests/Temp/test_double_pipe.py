import subprocess

some_string = b'input_data'

sort_out = open('outfile.txt', 'wb', 0)
sort_in = subprocess.Popen('sort', stdin=subprocess.PIPE, stdout=sort_out).stdin
subprocess.Popen(['awk', '-f', 'script.awk'], stdout=sort_in,
                 stdin=subprocess.PIPE).communicate(some_string)

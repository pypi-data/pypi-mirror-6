import subprocess

def read_in_chunks(path, size=2048):
    with open(path, 'rb') as stream:
        while True:
            data = stream.read(size)

            if data:
                yield data
            else:
                break

def has_program(program):
    try:
        subprocess.check_call('which %s >/dev/null 2>&1' % program, shell=True)
    except subprocess.CalledProcessError:
        return False
    else:
        return True

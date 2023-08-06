import subprocess


def perform_action(directory, action):
    p = subprocess.Popen('ls -d {}'.format(directory), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        path = line.decode().rstrip()
        cmd_cd = 'cd {}'.format(path)
        print(action)
        subprocess.call(cmd_cd + ';' + action, shell=True)

    p.wait()
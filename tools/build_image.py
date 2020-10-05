from pathlib import Path
import os
import subprocess

config = {

}

def system(cmd, capture=False, cwd=None, daemon=False):
    if capture:
        stdout = subprocess.PIPE
    else:
        stdout = None
    if daemon:
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=stdout,
                                stderr=subprocess.STDOUT,
                                cwd=cwd,
                                encoding='utf8')
        return proc
    else:
        proc = subprocess.run(cmd,
                              shell=True,
                              stdout=stdout,
                              stderr=subprocess.STDOUT,
                              cwd=cwd,
                              encoding='utf8')
        if proc.returncode != 0:
            raise RuntimeError(f'external command "{cmd}" failed. output="{proc.stdout}"')
        return proc


def build_docker_image():
    os.chdir(config['REPO_APP_DIR'])
    system('pipenv lock -r > requirements.txt')
    system('docker build -f Dockerfile.awsdev -t asobann_awsdev:latest .')


def push_docker_image():
    system('docker tag asobann_awsdev 550251267268.dkr.ecr.us-east-1.amazonaws.com/asobann_awsdev')
    system('aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 550251267268.dkr.ecr.us-east-1.amazonaws.com/asobann_awsdev')
    system('docker push 550251267268.dkr.ecr.us-east-1.amazonaws.com/asobann_awsdev')


def main():
    build_docker_image()
    push_docker_image()


if __name__=='__main__':
    config['REPO_APP_DIR'] = (Path(__file__).absolute().parent.parent.parent / 'asobann_app').absolute()
    main()

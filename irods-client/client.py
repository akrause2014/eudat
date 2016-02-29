import os
from subprocess import Popen, PIPE

class Client(object):
    
    def __init__(self, auth):
        self.auth = auth
        self.create_irods_environment()
    
    def list(self, directory):
        command = ["ils", directory]
        process = self.run_iRODS_command(command)
        stdoutdata, stderrdata = process.communicate()
        return [line.strip() for line in stdoutdata.splitlines()]
    
    def put(self, file, destination):
        command = ['iput', '-f', file, destination]
        process = self.run_iRODS_command(command)
        return process.wait()

    def rm(self, file):
        command = ['irm', file]
        process = self.run_iRODS_command(command)
        return process.wait()

    def run_iRODS_command(self, command):
        process = Popen(command, env=self.irods_env, stdout=PIPE)
        return process

    def create_irods_environment(self):
        self.irods_env = os.environ.copy()
        self.irods_env['irodsUserName'] = self.auth['username']
        self.irods_env['irodsHost'] = os.environ['RODSERVER_ENV_IRODS_HOST']
        self.irods_env['irodsPort'] = os.environ['RODSERVER_ENV_IRODS_HOST']
        self.irods_env['irodsZone'] = 'tempZone'
        self.irods_env['irodsAuthScheme'] = "gsi"
        self.irods_env['X509_USER_PROXY'] = self.auth['proxy']

if __name__ == '__main__':
    auth = {'username': 'newuser', 'proxy': '/tmp/x509up_u0'}
    client = Client(auth)
    homedir = '/tempZone/home/newuser'
    files = client.list(homedir)
    print('Listing: %s' % files)
    testfile = '/tmp/test.txt'
    with open(testfile, 'w') as f:
        f.write('Hello World!')
    client.put(testfile, homedir)
    files = client.list(homedir)
    print('Listing after put: %s' % files)
    client.rm(homedir+'/test.txt')
    files = client.list(homedir)
    print('Listing after rm: %s' % files)

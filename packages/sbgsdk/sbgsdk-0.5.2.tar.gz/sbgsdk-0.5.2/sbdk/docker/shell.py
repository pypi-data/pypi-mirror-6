import os

from sbdk.error import SbdkError
from sbdk.docker.container import Container

class Shell(object):

    def run_shell(self):
        raise NotImplementedError(self._message('run_shell'))

    def run_command(self, command):
        raise NotImplementedError(self._message('run_command'))

    def _message(self, method):
        return "Method '%s' not implemented for class %s." % method, self.__class__.__name__


class Bash(Shell):

    def __init__(self, project, docker):
        self.project = project
        self.cid_file = os.path.join(self.project.project_data, 'cid')
        self.docker = docker

    def run_shell(self):
        pid = os.fork()
        if not pid:
            self.sh()
        else:
            os.wait()
            with open(self.cid_file) as cid_file:
                cid = cid_file.read()
            os.remove(self.cid_file)
            return Container(self.docker.client, self.project, {'Id': cid})

    def sh(self):
        args = ['docker', 'run', '-i', '-t']
        args += ['-v', '%s:/sbgenomics:rw' % self.project.project_dir]
        args += ['-v', '%s:/sb:rw' % self.project.sb_home]
        args += ['-cidfile', self.cid_file]
        args += [self.project.state['image_id'], '/bin/bash']

        os.execvp('docker', args)

    def run_command(self, command):
        cont = self.docker.run(['/bin/bash', '-c', command])
        cont.print_log()
        return cont


class SSH(Shell):
    def run_shell(self):
        raise NotImplementedError(self._message('run_shell'))

    def run_command(self, command):
        raise NotImplementedError(self._message('run_command'))
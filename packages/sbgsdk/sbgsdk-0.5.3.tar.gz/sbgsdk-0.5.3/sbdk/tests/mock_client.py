__author__ = 'luka'


class MockClient(object):

    def __init__(self, *args, **kwargs):
        pass

    def attach(self, container):
        yield u"Mock output"

    def attach_socket(self, container, params=None, ws=False):
        pass

    def build(self, path=None, tag=None, quiet=False, fileobj=None,
              nocache=False, rm=False, stream=False):
        return u'0123456789ab', u"Mock message"

    def commit(self, container, repository=None, tag=None, message=None,
               author=None, conf=None):
        return {u'Id': u'0123456789ab'}

    def containers(self, quiet=False, all=False, trunc=True, latest=False,
                   since=None, before=None, limit=-1):
        return [{u'Command': u'/bin/bash ',
                 u'Created': 1390325161,
                 u'Id': u'2dcb4ff19477720b4cb1d04d80b11ccf6f3bce327ca5d37e265fcb4ba10a3485',
                 u'Image': u'ubuntu:12.04',
                 u'Names': [u'/kickass_albattani'],
                 u'Ports': None,
                 u'SizeRootFs': 0,
                 u'SizeRw': 0,
                 u'Status': u'Up 17 minutes'}]

    def copy(self, container, resource):
        return u"Mock raw result"

    def create_container(self, image, command=None, hostname=None, user=None,
                         detach=False, stdin_open=False, tty=False,
                         mem_limit=0, ports=None, environment=None, dns=None,
                         volumes=None, volumes_from=None, privileged=False,
                         name=None):
        return {u'Id': u'0123456789ab'}

    def create_container_from_config(self, config, name=None):
        return {u'Id': u'0123456789ab'}

    def diff(self, container):
        pass

    def events(self):
        yield {u'from': u'ubuntu:12.04',
               u'id': u'2dcb4ff19477720b4cb1d04d80b11ccf6f3bce327ca5d37e265fcb4ba10a3485',
               u'status': u'die',
               u'time': 1390326539}

    def export(self, container):
        return u"Mock raw result"

    def history(self, image):
        return u'[{"Id":"This json is left unparsed"}]'

    def images(self, name=None, quiet=False, all=False, viz=False):
        return [{u'Created': 1364102658,
                 u'Id': u'0123456789ab9a3c593ef05b4332b1d1a02a62b4accb2c21d589ff2f5f2dc',
                 u'Repository': u'ubuntu',
                 u'Size': 24653,
                 u'Tag': u'quantal',
                 u'VirtualSize': 180116135}]

    def import_image(self, src, data=None, repository=None, tag=None):
        pass

    def info(self):
        return {u'Containers': 25,
                u'Debug': 0,
                u'Driver': u'aufs',
                u'DriverStatus': [[u'Root Dir', u'/var/lib/docker/aufs'], [u'Dirs', u'65']],
                u'IPv4Forwarding': 1,
                u'Images': 11,
                u'IndexServerAddress': u'https://index.docker.io/v1/',
                u'InitPath': u'/usr/bin/docker',
                u'InitSha1': u'',
                u'KernelVersion': u'3.5.0-45-generic',
                u'LXCVersion': u'0.8.0-rc1',
                u'MemoryLimit': 1,
                u'NEventsListener': 3,
                u'NFd': 11,
                u'NGoroutines': 16,
                u'SwapLimit': 1}

    def insert(self, image, url, path):
        pass

    def inspect_container(self, container):
        return {u'Args': [],
                u'Config': {u'AttachStderr': True,
                            u'AttachStdin': True,
                            u'AttachStdout': True,
                            u'Cmd': [u'/bin/bash'],
                            u'CpuShares': 0,
                            u'Dns': None,
                            u'Domainname': u'',
                            u'Entrypoint': None,
                            u'Env': None,
                            u'ExposedPorts': {},
                            u'Hostname': u'2dcb4ff19477',
                            u'Image': u'ubuntu',
                            u'Memory': 0,
                            u'MemorySwap': 0,
                            u'NetworkDisabled': False,
                            u'OpenStdin': True,
                            u'PortSpecs': None,
                            u'StdinOnce': True,
                            u'Tty': True,
                            u'User': u'',
                            u'Volumes': {},
                            u'VolumesFrom': u'',
                            u'WorkingDir': u''},
                u'Created': u'2014-01-21T17:26:01.421055749Z',
                u'Driver': u'aufs',
                u'HostConfig': {u'Binds': None,
                                u'ContainerIDFile': u'',
                                u'Links': None,
                                u'LxcConf': [],
                                u'PortBindings': {},
                                u'Privileged': False,
                                u'PublishAllPorts': False},
                u'HostnamePath': u'/var/lib/docker/containers/2dcb4ff19477720b4cb1d04d80b11ccf6f3bce327ca5d37e265fcb4ba10a3485/hostname',
                u'HostsPath': u'/var/lib/docker/containers/2dcb4ff19477720b4cb1d04d80b11ccf6f3bce327ca5d37e265fcb4ba10a3485/hosts',
                u'ID': u'2dcb4ff19477720b4cb1d04d80b11ccf6f3bce327ca5d37e265fcb4ba10a3485',
                u'Image': u'8dbd9e392a964056420e5d58ca5cc376ef18e2de93b5cc90e868a1bbc8318c1c',
                u'Name': u'/kickass_albattani',
                u'NetworkSettings': {u'Bridge': u'',
                                     u'Gateway': u'',
                                     u'IPAddress': u'',
                                     u'IPPrefixLen': 0,
                                     u'PortMapping': None,
                                     u'Ports': None},
                u'Path': u'/bin/bash',
                u'ResolvConfPath': u'/var/lib/docker/containers/2dcb4ff19477720b4cb1d04d80b11ccf6f3bce327ca5d37e265fcb4ba10a3485/resolv.conf',
                u'State': {u'ExitCode': 0,
                           u'FinishedAt': u'2014-01-21T17:48:59.923387731Z',
                           u'Ghost': False,
                           u'Pid': 0,
                           u'Running': False,
                           u'StartedAt': u'2014-01-21T17:26:01.483899231Z'},
                           u'Volumes': {},
                           u'VolumesRW': {}}

    def inspect_image(self, image_id):
        return {u'Size': 522943178,
                u'architecture': u'x86_64',
                u'config': {u'AttachStderr': False,
                            u'AttachStdin': False,
                            u'AttachStdout': False,
                            u'Cmd': None,
                            u'CpuShares': 0,
                            u'Dns': None,
                            u'Domainname': u'',
                            u'Entrypoint': None,
                            u'Env': None,
                            u'ExposedPorts': None,
                            u'Hostname': u'',
                            u'Image': u'',
                            u'Memory': 0,
                            u'MemorySwap': 0,
                            u'NetworkDisabled': False,
                            u'OpenStdin': False,
                            u'PortSpecs': None,
                            u'StdinOnce': False,
                            u'Tty': False,
                            u'User': u'',
                            u'Volumes': None,
                            u'VolumesFrom': u'',
                            u'WorkingDir': u''},
                u'container': u'd61fc212316b7812410364b1c6e6859eb0d2ed47c49b821fe70fac3273d340b1',
                u'container_config': {u'AttachStderr': True,
                                      u'AttachStdin': True,
                                      u'AttachStdout': True,
                                      u'Cmd': [u'/bin/bash'],
                                      u'CpuShares': 0,
                                      u'Dns': [u'8.8.8.8', u'8.8.4.4'],
                                      u'Domainname': u'',
                                      u'Entrypoint': [],
                                      u'Env': None,
                                      u'ExposedPorts': {},
                                      u'Hostname': u'd61fc212316b',
                                      u'Image': u'ubuntu:12.04',
                                      u'Memory': 0,
                                      u'MemorySwap': 0,
                                      u'NetworkDisabled': False,
                                      u'OpenStdin': True,
                                      u'PortSpecs': None,
                                      u'StdinOnce': True,
                                      u'Tty': True,
                                      u'User': u'',
                                      u'Volumes': {},
                                      u'VolumesFrom': u'',
                                      u'WorkingDir': u''},
                u'created': u'2013-11-04T17:18:41.638987857+01:00',
                u'docker_version': u'0.6.5',
                u'id': u'9c7d47054d404c3f1273df8d6dd544937084fa0b4c4afbc79b8b2cc035417a2e',
                u'parent': u'8dbd9e392a964056420e5d58ca5cc376ef18e2de93b5cc90e868a1bbc8318c1c'}

    def kill(self, container, signal=None):
        pass

    def login(self, username, password=None, email=None, registry=None):
        return {'Status': 'Login Succeeded'}

    def logs(self, container):
        return '{"message":"logs"}'

    def port(self, container, private_port):
        return 10666

    def pull(self, repository, tag=None, stream=False):
        return u'{"status": "another unparsed json"}'

    def push(self, repository, stream=False):
        return u'{"status": "another unparsed json"}'

    def remove_container(self, container, v=False, link=False):
        pass

    def remove_image(self, image):
        pass

    def restart(self, container, timeout=10):
        pass

    def search(self, container, timeout=10):
        return []

    def start(self, container, binds=None, port_bindings=None, lxc_conf=None,
              publish_all_ports=False, links=None):
        pass

    def stop(self, container, timeout=10):
        pass

    def tag(self, image, repository, tag=None, force=False):
        return True

    def top(self, container):
        return {u'Processes': [[u'root',
                u'14810',
                u'14786',
                u'0',
                u'18:26',
                u'pts/5',
                u'00:00:00',
                u'/bin/bash']],
                u'Titles': [u'UID', u'PID', u'PPID', u'C', u'STIME', u'TTY', u'TIME', u'CMD']}

    def version(self):
        return {u'Arch': u'amd64',
                u'GitCommit': u'bc3b2ec',
                u'GoVersion': u'go1.2',
                u'KernelVersion': u'3.5.0-45-generic',
                u'Os': u'linux',
                u'Version': u'0.7.6'}

    def wait(self, container):
        return 0


class OutJson(MockClient):

    def create_container_from_config(self, config, name=None):
        if config['Cmd'][0] != 'chown':
            with open('__out__.json', 'w') as f:
                    f.write('{}')
        return {u'Id': u'0123456789ab'}
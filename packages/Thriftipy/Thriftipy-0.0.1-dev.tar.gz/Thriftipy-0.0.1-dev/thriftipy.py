from __future__ import print_function
import glob
import subprocess


class ThriftGenerator(object):
    idl_ext = '*.thrift'
    dep_dir = 'dep_idls'

    def __init__(self, idl_dir, gen_dir, deps=None):
        self.idl_dir = idl_dir
        self.gen_dir = gen_dir
        self.deps = deps

    def _get_thrift_idls(self):
        return glob.glob(self.idl_dir + '/' + self.idl_ext)

    def _get_dependent_idls(self):
        try:
            list_dir = [__import__(i).__path__[0] for i in self.deps
                        if self is not None
                        ]
            list_files = []
            for i in list_dir:
                list_files.extend(glob.glob(i + '/*.thrift'))
            return list_files
        except ImportError, e:
            raise e

    def generate(self):
        print('> Starting thrift generation!')
        idls = self._get_thrift_idls()
        dep_idls = []
        if self.deps is not None:
            dep_idls = self._get_dependent_idls()

        if len(idls) == 0:
            print('no idls found in %s' % self.idl_dir)
            print('skipping thrift generation')
            return

        subprocess.call(['rm', '-rf', self.gen_dir, self.dep_dir])
        subprocess.call(['mkdir', '-p', self.gen_dir, self.dep_dir])

        # copy project idls to gen_dir
        for idl in idls:
            subprocess.call(['cp', idl, self.gen_dir])
        # copy dependent idls to dep_dir
        for dep_idl in dep_idls:
            subprocess.call(['cp', dep_idl, self.dep_dir])
        # execute thrift
        for idl in idls:
            thrift_cmd = [
                'thrift', '--gen', 'py',
                '-I', self.dep_dir,
                '--out', self.gen_dir
            ]
            thrift_cmd.append(idl)
            subprocess.call(thrift_cmd)
        print('> Thrift generation finished!')


#class generate_thrift(Command):
#    description = ""
#    user_options = []
#
#    def initialize_options():
#        self.idl_dir = 'idl_dir'
#        self.gen_dir = 'gen_dir'
#        self.gen = ThriftGenerator(self.idl_dir, self.gen_dir)
#
#    def finalize_options(self):
#        pass
#
#    def run(self):
#        self.gen.generate()

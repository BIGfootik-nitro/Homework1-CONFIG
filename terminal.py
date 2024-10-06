import json
import tarfile
from datetime import datetime


class MyTerminal:
    def __init__(self, user_name, file_system, log_file, start_script):
        self.us_name = user_name
        self.fs = file_system
        self.log_f = log_file
        self.st_script = start_script

        self.cur_d = ''
        self.polling = False
        self.log = dict()
        self.log['id'] = dict()
        self.cnt = 0

        self.deleted = set()

    def make_log(self):
        with open(self.log_f, 'w') as f:
            json.dump(self.log, f)

    def output(self, message, end='\n'):
        print(message)
        return message

    def start_polling(self):
        self.polling = True
        while self.polling:
            message = f'{self.us_name}:~{self.cur_d}$ '
            enter = input(message).strip()
            if len(enter) > 0:
                self.command_dispatcher(enter)
        self.output('stop polling...')
        self.make_log()

    def command_dispatcher(self, command):
        self.log['id'][self.cnt] = {'user': self.us_name, 'time': str(datetime.now()), 'command': command}
        self.cnt += 1

        params = command.split()
        if params[0] == 'exit':
            self.polling = False
        elif params[0] == 'cd':
            self.cd(params[1:])
        elif params[0] == 'ls':
            self.ls(params[1:])
        elif params[0] == 'tac':
            self.output(self.tac(params[1:]))
        elif params[0] == 'rmdir':
            self.rmdir(params[1:])
        else:
            self.output("Command not found")

    def rmdir(self, params):
        dr = params[-1]
        d_name = self.find_path(dr)
        new_deleted = set()
        is_dir = False
        if d_name is not None and d_name != '':
            with tarfile.open(self.fs, 'r') as tar:
                for d in tar:
                    if d.name == d_name and d.type == tarfile.DIRTYPE:
                        is_dir = True
                    if d.name.startswith(d_name):
                        new_deleted.add(d.name)
        else:
            self.output('Wrong directory name')
        if is_dir:
            self.deleted |= new_deleted
        else:
            self.output('Not a directory')

    def exec_start_script(self):
        try:
            with open(self.st_script, 'rt') as f:
                for s in f:
                    s = s.strip()
                    if len(s) > 0:
                        self.command_dispatcher(s)
        except:
            self.output('Failed opening start script')

    def find_path(self, path):
        current_path = self.cur_d

        while '//' in path:
            path = path.replace('//', '/')
        if path[-1] == '/':
            path = path[:-1]

        path = path.split('/')
        if path[0] == '/':
            current_path = ''
            path.pop(0)

        while path:
            name = path.pop(0)
            if name == '.':
                current_path = self.cur_d
            elif name == '..':
                index = current_path.rfind('/')
                if index > -1:
                    current_path = current_path[:index]
                else:
                    current_path = ''
            else:
                if current_path:
                    current_path += '/' + name
                else:
                    current_path += name
                with tarfile.open(self.fs, 'r') as tar:
                    paths = [member.name for member in tar]
                    if current_path not in paths:
                        return None

        if current_path in self.deleted:
            current_path = None
        return current_path

    def ls(self, prmtrs):
        message = ""

        def ls_names(c_directory):
            m_names = set()
            with tarfile.open(self.fs, 'r') as tar:
                for member in tar:
                    m_name = member.name
                    if m_name.find(c_directory) > -1 and m_name not in self.deleted:
                        if m_name == c_directory:
                            if member.type == tarfile.DIRTYPE:
                                continue
                            return (c_directory[c_directory.rfind('/') + 1:],)

                        m_name = m_name[len(c_directory):]
                        if m_name[0] == '/':
                            m_name = m_name[1:]
                        erase = m_name.find('/')
                        if erase > -1:
                            m_name = m_name[:m_name.find('/')]
                        m_names.add(m_name)
            return sorted(m_names)

        if len(prmtrs) > 1:
            prmtrs.sort()
            while prmtrs:
                directory = self.find_path(prmtrs[0])
                name = prmtrs.pop(0)
                if directory is None:
                    self.output(f"ls: cannot access '{name}': No such file or directory")
                    continue

                message += self.output(f'{name}:') + '\n'
                names = ls_names(directory)
                if names:
                    message += self.output(' '.join(names)) + '\n'
                if prmtrs:
                    message += self.output('') + '\n'

            return message

        directory = self.cur_d
        if len(prmtrs) == 1:
            directory = self.find_path(prmtrs[0])
            if directory is None:
                message += self.output(f"ls: cannot access '{prmtrs[0]}': No such file or directory") + '\n'
                return message

        names = ls_names(directory)
        if names:
            message += self.output('\n'.join(names)) + '\n'
        return message

    def cd(self, prmtrs):
        if not prmtrs:
            self.cur_d = ''
            return 'root directory'

        if len(prmtrs) > 1:
            return self.output("cd: too many arguments")

        new_directory = self.find_path(prmtrs[0])
        if new_directory is None:
            return self.output(f"cd: {prmtrs[0]}: No such file or directory")
        if new_directory == '':
            self.cur_d = new_directory
            return f"change to " + new_directory

        with tarfile.open(self.fs, 'r') as tar:
            for member in tar:
                if member.name == new_directory and member.name not in self.deleted:
                    if member.type != tarfile.DIRTYPE:
                        return self.output(f"cd: {prmtrs[0]}: Not a directory")
                    self.cur_d = new_directory
                    return f"change to " + new_directory

    def tac(self, params):
        file = params[-1]
        f_name = self.find_path(file)
        try:
            with tarfile.open(self.fs, 'r') as tar:
                for f in tar:
                    if f.name == f_name and f.type != tarfile.DIRTYPE and f.name not in self.deleted:
                        with tar.extractfile(f) as read_file:
                            lines = []
                            for i in read_file:
                                lines.append(i.decode('UTF-8').replace('\r', ''))
                            return ''.join(lines[::-1])
                    else:
                        return 'Is directory'
        except:
            return 'Wrong file name'
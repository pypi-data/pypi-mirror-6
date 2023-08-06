import pickle as p
import getpass
import threading
import platform
import copy
from Saffron.security import security
from Saffron.database import database, Pointer
from Saffron.functions import pretty_print

class SAF(object):
    def __init__(self, setup=False, print_out=True, file_ext=None):
        build = '0.5.1'
        global error
        code = 1
        if print_out:
            print 'Saffron Version', build
        if setup and not file_ext:
            self.setup()
        elif setup and file_ext:
            self.setup(file_ext)

    def setup(self, file_extension = '.saf', alias = {'x':'exit'}):
        global error
        error = 2
        self.file_extension = file_extension
        try:
            my_data = p.load(open('setup.p' + self.file_extension.strip('.'), 'r')) # [security key, user_dict, auth_dict, default_file, log, db_dict, autorun]
        except:
            my_data = []
            my_data.append('root')
            my_data.append({'root':user('root', 99, security('root'))})
            my_data.append({})
            my_data.append('Untitled' + self.file_extension)
            my_data.append([])
            my_data.append([])
            my_data.append(True)
            p.dump(my_data, open('setup.p' + self.file_extension.strip('.'), 'w'))
        
        error = 3
        
        self.user_dict = my_data[1]
        self.default_file = my_data[3]
        self.log = my_data[4]
        self.__hash = my_data[0]
        self.db_list = my_data[5]
        self.autorun = my_data[6]
        self.file_name = self.default_file
        self.secure = security(self.__hash)
        self.temp_user_dict = {}
        self.auth = 0
        self.os = platform.release()
        self.username = getpass.getuser().lower()
        global db_dict
        db_dict = {}
        for f in self.db_list:
            db_dict[f] = database(f)
        error = 5
        
        try:
            open(self.file_name, 'r')
        except:
            self.create(self.file_name)
            
        error = 6
        
        if self.autorun:
            try:  
                data_file = open('autorun.txt', 'r')
            except:
                data_file = open('autorun.txt', 'w')
                data_file.write('')
            
        error = 4
        
        self.commands = {}
        self.add_command('au', lambda x: self.add_user(x), 99)
        self.add_command('du', lambda x: self.delete_user(x), 99)
        self.add_command('login', lambda x: self.login(x))
        self.add_command('pu', lambda x: self.print_users(x))
        self.add_command('exit', lambda x: self.x(x)) 
        self.add_command('debug', lambda x: self.debug(x)) 
        self.add_command('ch', lambda x: self.change_hash(x))
        self.add_command('pyrun', lambda x: self.pyrun(x), 99)
        self.add_command('run', lambda x: self.run(x), 99)
        self.add_command('finport', lambda x: self.finport(x), 99)
        self.add_command('create', lambda x: self.create(x))
        self.add_command('autorun', lambda x: self.autorun_func(x))
        self.add_command('db', lambda x: self.db_func(x))
        self.add_command('help', lambda x: self.help_print(x))
        self.add_command('log', lambda x: self.log_func(x))
        self.add_command('cf', lambda x: self.change_file(x))
        self.add_command('use', lambda x: self.use(x))
        
        for f in alias.keys():
            try:
                self.commands[f] = copy.deepcopy(self.commands[alias[f]])
                self.commands[f].description = 'Alias for ' + alias[f]
                self.commands[f].name = f
            except:
                pass
        
        if 'save' not in self.commands.keys():
            self.add_command('save', lambda x: self.save(None))
        
        return self.use(self.file_name)

    def main(self):
        global error
        error = 7
        self.debug_mode = False
        self.quit_state = False
        self.autoquit = True
        self.run('autorun run')
        while not self.quit_state:
            mode_l = raw_input((self.username + '@' + self.file_name + ': ').replace(self.file_extension, ""))
            self.run(mode_l)
            
        return self.autoquit
    
    def x(self, key):
        global error
        error = 8
        if key in ['x', 'quit']:
            self.autoquit = False
        self.quit_state = True

    def run(self, mode_l):
        global error
        error = 9
        if mode_l in [None, '', ' ']:
            return
        mod_list = []
        doas_state = False
        ignore_state = False
        user = self.username
        try:
            if mode_l.startswith('doas'):
                user_data = mode_l.split(' ')[1].split(';')
                mode_l = ' '.join(mode_l.split(' ')[2:len(mode_l)])
                user = user_data[0].strip()
                if user in self.user_dict.keys():
                    if user in self.temp_user_dict.keys():
                        password = self.temp_user_dict[user]
                    elif len(user_data) == 1:
                        password = getpass.getpass()
                    else:
                        password = user_data[1].strip()
                    if password == self.secure.descramble(self.user_dict[user].password):
                        doas_state = True
                        old_auth = self.auth
                        self.auth = self.user_dict[user].auth

                else:
                    print 'User not found!\n'
                    return None
        except:
            print 'doas error!\n'
            return None
                
        if doas_state:
            if user not in self.temp_user_dict.keys() and user != 'root':
                self.temp_user_dict[user] = password
                
        error = 10
            
        mode = mode_l.split(' ')[0].strip()
        oper = mode_l.lstrip(mode).strip()
        try:
            while mode[0] in ['*', '?', '>']:
                mod_list.append(mode[0])
                mode = mode[1:len(mode)]
                
        except:
            pass
            
        if '*' in mod_list:
            ignore_state = True
            
        if '?' in mod_list:
            print 'User:', user, '\n Command:', mode, oper, '\n'
            
        if '>' in mod_list:
            oper = mode + ' ' +oper
            mode = 'pyrun'
        
        error = '10a'
        
        try:
            self.my_auth = self.auth >= self.commands[mode].auth
        except:
            print 'Command:', mode, 'not found!'

        if mode in self.commands.keys():
            if self.my_auth:
                if not self.debug_mode and mode != 'debug' and self.os != 'XP' and not ignore_state:
                    try:
                        t = threading.Thread(self.commands[mode].execute(oper))
                        t.daemon = True
                        t.start()
                    except:
                        print 'Unexpected error!\nError code:', error
                        
                else:
                    self.commands[mode].execute(oper)
                    
            else:
                print 'Not authorized!'
                
            self.log.append(user + '@' + self.file_name + ': ' + mode_l)
            
        else:
            pass
            
        error = 11

        if doas_state:
            self.auth = old_auth
        
        print 

    def file_strip(self, name):
        global error
        error = 12
        if not name.endswith(self.file_extension):
            name += self.file_extension
        return name
            
    def use(self, file_name):
        global error
        error = 13
        file_name = self.file_strip(file_name)
        try:
            my_data = p.load(open(file_name, 'r'))
            self.file_name = file_name
            return my_data
        except:
            print 'File not found!'
            self.create('Untitled')
            self.use("Untitled")

    def create(self, name):
        global error
        error = 14
        try:
            if name in ['', ' ', None]:
                print 'Name error!'
                return None
            name = self.file_strip(name)
            p.dump(None, open(name, 'w'))
        except:
            print 'Name error!'

    def save(self, data_in):
        global error
        error = 15
        global db_dict
        #try:
        p.dump([self.secure.hash, self.user_dict, None, self.default_file, self.log, db_dict.keys(), self.autorun], 
                open('setup.p' + self.file_extension.strip('.'), 'w'))
        p.dump(data_in, open(self.file_name, 'w'))
        '''
        except:
            try:
                print 'Unable to write to setup file!'
                p.dump(data_in, open(self.file_name, 'w'))
            except:
                print 'Unable to write to data file!'
        '''

    def print_users(self, name):
        global error
        error = 16
        if not name:
            print 'Registered Users:'
            for u in self.user_dict.keys():
                print u,
        else:
            print 'Matching users:'
            for u in self.user_dict.keys():
                if u.startswith(name):
                    print u,

        print '\nCurrent User:', self.username
        print 'Current auth level:', self.auth

    def add_user(self, key):
        global error
        error = 17
        try:
            hold = key.split(';')
            name = hold[0]
            password1 = hold[1]
            auth = hold[2]
        except:
            name = raw_input('New Username: ')
            password1 = getpass.getpass()
            password2 = getpass.getpass('Confirm password: ')
            auth = raw_input('New auth level: ')
            if password1 != password2:
                print 'Passwords do not match!'
                return None
        if auth > 99:
            auth = 99
        if name == 'root':
            print 'Cannot edit root!'
            return None
        self.user_dict[name] = user(password1, auth, self.secure)

    def delete_user(self, key):
        global error
        error = 19
        if key in self.user_dict.keys():
            del self.user_dict[key]
        else:
            print 'User does not exist!'

    def login(self, key):
        global error
        error = 20
        if key not in [None, '', ' ']:
            key = key.split(';')
            user = key[0]
            try:
                password = key[1]
            except:
                if user in self.user_dict.keys():
                    password = getpass.getpass()
                else:
                    print 'User not found...'
                    return None
        else:
            user = raw_input('Username: ')
            password = getpass.getpass()
        self.password = password
        if user in self.user_dict.keys():
            if password == self.secure.descramble(self.user_dict[user].password):
                print 'Now using as', user
                self.username = user
                self.auth = self.user_dict[user].auth
                return None
        print 'Login not succesful...'

    def log_func(self, key):
        global error
        error = 21
        if key == 'dump':
            open('log.txt', 'w').write('\n'.join(self.log))
            
        elif key == 'print':
            print '\nLog:'
            for f in self.log:
                print '\t', f
        else:
            print 'Invalid command!'

    def debug(self, key):
        global error
        error = 22
        if key in ['On', 'on', 'true', 'True', '', ' ', None]:
            print 'Debugging mode on!'
            self.debug_mode = True
        else:
            print 'Debugging mode off!'
            self.debug_mode = False

    def change_hash(self, new_hash):
        global error
        error = 23
        if len(new_hash) < 4:
            print 'Invalid hash!'
            return None
        old_hash = self.secure.hash
        self.secure.hash = new_hash
        try:
            my_sample = self.secure.scramble('test')
            test = self.secure.descramble(my_sample)
            self.user_dict['root'].password = self.secure.scramble(new_hash)
        except:
            print 'Invalid hash!'
            self.secure.hash = old_hash
            return None
        if test != 'test':
            print 'Invalid hash!'
            self.secure.hash = old_hash
            return None

    def pyrun(self, command):
        global error
        error = 25
        if not self.debug_mode:
            try:
                exec command
            except:
                print 'Invalid command!'
                print 'Error code:', error
        else:
            exec command

    def finport(self, fin):
        global error
        error = 26
        globals()[fin] = __import__(fin)

    def run_file(self, program_file):
        global error
        error = 27
        program_file += '.txt'
        try:
            program = open(program_file, 'r')
        except:
            print 'File not found!'
            return None
        print 'executing', program_file.rstrip('.txt') + '...'
        my_program = []
        for line in program:
            mode_l = line.strip()
            my_program.append(mode_l)
        f = 0
        my_command = ''
        error = 28
        while f != len(my_program):
            if my_program[f].startswith('if'):
                thing = my_program[f].strip('if ')
                exec 'self.if_state = ' + thing.split('|')[0]
                if self.if_state:
                    my_command = thing.split('|')[1]
            if my_program[f].startswith('goto') or my_command.startswith('goto'):
                f = int(my_command.split(' ')[1])
                my_command = my_program[f]
            else:
                my_command = my_program[f]
            if not my_command.startswith('//'):
                self.run(my_command)
            f += 1

        print program_file.rstrip('.txt'), 'finished!'

    def run_if(self, key):
        global error
        error = 29
        new = key.split('|')
        condition = new[0]
        result = new[1]
        exec 'self.if_state = ' + condition
        if self.if_state:
            self.run(result)
    
    def autorun_func(self, key):
        global error
        error = 55

        if key == 'run':
            if self.autorun:
                self.run_file('autorun')
                
        elif key == 'enable' and self.auth == 99:
            self.autorun = True
            print 'Autorun enabled!'
                
        elif key == 'disable' and self.auth == 99:
            self.autorun = False
            print 'Autorun disabled!'
            
        else:
            print 'Invalid argument!'

    def help_print(self, key):
        global error
        error = 57        
        print 'Matching commands:'
        for command in sorted(self.commands.keys()):
            if command.startswith(key):
                print self.commands[command]

    def add_command(self, name, function, auth=0, description=''):
        self.commands[name] = command(name, function, auth, description)
        
    def change_file(self, name):
        self.default_file = name + self.file_extension
        
    def db_func(self, key):
        spaces = key.split(' ')
        mode = spaces[0]
        del spaces[0]
        x = ' '.join(spaces)
        if mode == 'c':
            self.create_database(x)
        elif mode == 'ex':
            self.database_exectute(x)
        elif mode == 'mt':
            self.database_maketable(x)
        elif mode == 'ud':
            self.database_update(x)
        elif mode == 'in':
            self.database_insert(x)
        elif mode == 'pt':
            self.database_print(x)
        elif mode == 'del':
            self.database_delete(x)
        else:
            print 'Invalid mode!'

    def create_database(self, name):
        global error
        error = 30
        global db_dict
        if name not in ['', ' ', None]:
            db_dict[name] = database(name)
        else:
            print "Can't create a data base without a name!"

    def database_execute(self, key):
        global error
        error = 31
        global db_dict
        name = key.split(';')[0]
        command = key.split(';')[1]
        
        if name in db_dict.keys():
            db_dict[name].execute(command)
        else:
            print 'Database not found!'

    def database_maketable(self, key):
        global error
        error = 32
        global db_dict
        data = key.split(';')
        name = data[0]
        tname = data[1]
        atts = []
        for f in range(2, len(data)):
            atts.append(data[f])

        if name in db_dict.keys():
            try:
                db_dict[name].maketable(tname, atts)
            except:
                pass

        else:
            print 'Database not found!'

    def database_update(self, key):
        global error
        error = 33
        global db_dict
        data = key.split(';')
        name = data[0]
        
        if name in db_dict.keys():
            db_dict[name].update(data[1], data[2], data[3], data[4], data[5])

        else:
            print 'Database not found!'

    def database_print(self, key):
        global error
        error = 34
        global db_dict
        data = key.split(';')
        name = data[0]
        table = data[1]
        
        if name in db_dict.keys():
            db_dict[name].printtable(table)

        else:
            print 'Database not found!'
            
    def database_insert(self, key):
        global error
        error = 35
        global db_dict
        if isinstance(key, str):
            data = key.split(';')
        elif isinstance(key, list):
            data = key
        else:
            print 'Invalid input type!'
            return
        name = data[0]
        tname = data[1]
        atts = []
        for f in range(2, len(data)):
            atts.append(data[f])

        if name in db_dict.keys():
            db_dict[name].insert(tname, atts)

        else:
            print 'Database not found!'
    
    def database_delete(self, key):
        global error
        error = 54
        global db_dict
        try:
            del db_dict[key]
            print key, 'deleted!'
                
        except:
            print 'Database does not exist!'

class user(object):
    def __init__(self, password, auth, security):
        global error
        error = 40
        self.auth = auth
        self.password = security.scramble(password)

class command(object):
    def __init__(self, name, function, auth = 0, description = ''):
        self.name = name
        self.function = function
        self.auth = auth
        self.description = description

    def __str__(self):
        if self.description not in ['', ' ', None]:
            return self.name + ': ' + self.description
        else:
            return self.name

    def execute(self, x):
        try:
            self.function(x)
        except:
            self.function()
        

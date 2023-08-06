import random

class security(object):
    def __init__(self, my_key):
        global error
        error = 36
        self.hash = my_key
    
    def scramble(self, key):
        global error
        error = 37
        hash_list = []
        for f in key:
            hash_list += [(((ord(f) + ord(self.hash[0]) + ord(self.hash[1])) * (ord(self.hash[2]) + \
                                                                                ord(self.hash[3]))) * 10) + random.randint(0,9)]
        return hash_list

    def descramble(self, hash_list):
        global error
        error = 38
        key = ''
        for f in hash_list:
            key += chr((int(str(f)[0:len(str(f))-1])) / (ord(self.hash[2]) + \
                                                         ord(self.hash[3])) - ord(self.hash[0]) - ord(self.hash[1]))
        return key

    def key(self):
        global error
        error = 39
        return self.scramble(self.hash)
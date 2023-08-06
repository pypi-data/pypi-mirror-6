import sqlite3

class database(object):
    def __init__(self, name):
        global error
        error = 41
        self.conn = sqlite3.connect(name + '.db')
        self.conn.row_factory = sqlite3.Row
        self.curs = self.conn.cursor()

    def maketable(self, tablename, feildnames):
        global error
        error = 42
        if len(feildnames) == 0:
            print 'No feilds specified!'
            return None
        
        makestring = 'create table ' + tablename + ' ('
        for f in range(0, len(feildnames)):
            if f != len(feildnames) - 1:
                makestring += (feildnames[f] + ', ')
            else:
                makestring += (feildnames[f])

        makestring += ')'
        self.conn.execute(makestring)
        self.conn.commit()

    def execute(self, command):
        global error
        error = 43
        self.curs.execute(command)
        self.conn.commit()

    def update(self, tablename, update_feild, update_value, new_feild, new_value):
        global error
        error = 44
        self.curs.execute("UPDATE " + tablename + ' SET ' + new_feild + "= '" + new_value \
                          + "' WHERE " + update_feild + "='" + update_value + "'")
        self.conn.commit()

    def printtable(self, tablename):
        global error
        error = 45
        big_data  = []
        little_data = []
        headers = []
        headers_data = []
        self.curs.execute('SELECT * FROM ' + tablename)
        rows = self.curs.fetchall()
        for f in rows:
            for m in f:
                little_data.append(m)
            big_data.append(little_data)
            little_data = []
            
        self.curs.execute('PRAGMA table_info(' + tablename + ')')
        headers_data = self.curs.fetchall()
        for h in headers_data:
            headers.append(h[1])
        pretty_print(headers, big_data)
        
    def insert(self, tablename, feildnames):
        global error
        error = 46
        insertstring = " VALUES ('"
        for f in range(0, len(feildnames)):
            if f != len(feildnames) - 1:
                insertstring += (feildnames[f] + "', '")
            else:
                insertstring += (feildnames[f])

        insertstring += "')"
        self.execute('INSERT INTO ' + tablename + insertstring)
            
    def get(self, table, feild, value, retrieve):
        global error
        error = 47
        self.execute("SELECT * FROM "+ table + " WHERE " + feild + "='" + value + "'")
        return self.curs.fetchone()[retrieve]
        
    def close(self):
        global error
        error = 48
        self.conn.commit()
        self.conn.close()
        
    def col_names(self, tablename):
        headers = []
        self.curs.execute('PRAGMA table_info(' + tablename + ')')
        headers_data = self.curs.fetchall()
        for h in headers_data:
            headers.append(h[1])
            
        return headers
    
class Pointer(object):
    def __init__(self, _database, table, feild, value, retrieve):
        global error
        error = 49
        self._database = _database
        self.table = table
        self.feild = feild
        self.value = value
        self.retrieve = retrieve
        
    def __get__(self):
        global error
        error = 50
        return db_dict[self._database].get(self.table, self.feild, self.value, self.retrieve)
    
    def __set__(self, other):
        global error
        error = 51
        db_dict[self._database].update(self.table, self.feild, self.value, self.retrieve, str(other))
        if self.feild == self.retrieve:
            self.value = str(other)
            
    def __neg__(self):
        global error
        error = 56
        db_dict[self._database].execute("DELETE FROM "+ self.table + " WHERE " + self.feild + "='" + self.value + "'")
        
    def __pos__(self):
        global error
        error = 52
        return db_dict[self._database].get(self.table, self.feild, self.value, self.retrieve)
    
    def __add__(self, other):
        global error
        error = 53
        db_dict[self._database].update(self.table, self.feild, self.value, self.retrieve, str(other))
        if self.feild == self.retrieve:
            self.value = str(other)

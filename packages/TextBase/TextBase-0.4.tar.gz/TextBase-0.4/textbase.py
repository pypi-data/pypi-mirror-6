'''
textbase - A Python library to manipulate Inmagic/DBText style data files

The main utitlity class is TextBase.
It can be initialised with an open file, or a string buffer, named sourcefile.
Sourcefile is iterated over, splitting the contents into chunks.
Each chunk is parsed and added to an internal buffer list.
The internal buffer contains a dict for each record. Each entry in the dict
is keyed on the DBText record fieldname, the entry itself is a list of the values.

The TextBase object can be used as a generator to iterate over the contents,
or the Textbase object can be index-addressed like a list.

Example Usage:
--------------

import textbase
t = textbase.TextBase(somebuf)

print len(t)

for x in t[10:20]:
    print x.keys()

print t[0]


If you do not want the records parsed into Python dictionaries and just want 
to muck about with the records as text blobs, initialise like this:
  t = textbase.TextBase(somebuf, parse=False)

Please send me feedback if this is useful for you, or suggestions etc.
Author: Etienne Posthumus
Mail: ep@epoz.org
Dev started: 17 November 2004

4. Allow comments and skip empty records.
---
3. Add utility function 'parse' to main module to make opening a file shorter/less typing.
---
2. Added keep_original flag at init to keep original text chunks. 
---
1. First version
'''

__version__ = 4
__date__ = '20121018'

def parse(filename):
    return TextBase(open(filename))
    
class TextBase:
    def __init__(self, sourcefile=None, separator='$', parse=True, keep_original=False, encoding='utf8'):
        self.separator = separator
        self.__entries__ = []
        self.keep_original = keep_original
        self.encoding = encoding
        if type(sourcefile) == str:
            import cStringIO
            self.sourcefile = cStringIO.StringIO(sourcefile)
        elif type(sourcefile) == file:
            self.sourcefile = sourcefile
        if parse:
            self.process = self.parse
        else:
            self.process = self.dontparse
        BOMcheck = self.sourcefile.read(3)
        if BOMcheck != '\xef\xbb\xbf':
            self.sourcefile.seek(0)
        self.split()
        

    def dontparse(self, chunk):
        self.__entries__.append(''.join(chunk))

    def parse(self, chunk):
        lastField = ''
        datadict = {}
        for x in chunk:
            if x[0] == '#':
                continue
            spacepos = x.find(' ')
            if spacepos == -1:
                continue
            if x[0] != ';' and spacepos > 0:
                lastField = x[0:spacepos]
                if lastField.endswith(':'):
                    lastField = lastField[:-1]
            data = x[spacepos:].strip()
            if self.encoding is not None:
                data = data.decode(self.encoding)
            if lastField in datadict.keys():
                if spacepos == 0:
                    datadict[lastField][-1] = datadict[lastField][-1] + ' ' + data 
                else:
                    datadict[lastField].append(data)
            else:        
                datadict[lastField] = [data]
        if self.keep_original:
            datadict['__original__'] = (''.join(chunk))
        if datadict:
            self.__entries__.append(datadict)
        
    def split(self):
        chunk = []
        for line in self.sourcefile:
            if line.strip() == self.separator:
                if chunk:
                    self.process(chunk)
                    chunk = []
            else:
                chunk.append(line)
        if chunk:
            self.process(chunk)

    def dump(self, filename):
        with open(filename, 'w') as F:
            for x in self.__entries__:
                for k, v in x.items():
                    F.write('\n%s ' % k.encode('utf8'))
                    tmp = u'\n; '.join(v)
                    F.write(tmp.encode('utf8'))
                F.write('\n$')

    def __getitem__(self, key):
        return self.__entries__[key]

    def __iter__(self):
        return iter(self.__entries__)

    def __len__(self):
        return len(self.__entries__)

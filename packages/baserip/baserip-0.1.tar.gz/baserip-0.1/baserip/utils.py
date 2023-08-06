class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Node(object):
    def __init__(self, name, parent=None):
        self._name = name
        self._children = []
        self._parent = parent
        
        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        return "NODE"

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        
        if position < 0 or position > len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None

        return True

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    name = property(getName, setName)

    def child(self, row):
        try:
            return self._children[row]
        except (IndexError):
            return None
    
    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

class FreqTable(object):
    def __init__(self):
        self.table = {}
        
    def mark(self, val, inc=1):
        if val in self.table:
            self.table[val] += inc
        else:
            self.table[val] = inc
            
    def max(self):
        valmax = curmax = 0
        for val in self.table:
            if self.table[val] > curmax:
                curmax = self.table[val]
                valmax = val
        return valmax

if __name__ == '__main__':
    class MyClass(metaclass=Singleton):
        pass
        
    print(MyClass() is MyClass())
    

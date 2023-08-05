from posix import listdir
from posixpath import dirname, splitext
from inspect import getmembers, getmodule, isclass


from mio import runtime
from mio.object import Object


class Core(Object):

    def __init__(self):
        super(Core, self).__init__()

        self.create_objects()

        self.create_methods()
        self.parent = runtime.find("Object")

    def load_objects(self):
        for filename in listdir(dirname(__file__)):
            name, ext = splitext(filename)
            if ext == ".py" and name != "__init__":
                module = __import__("mio.core.{0:s}".format(name), fromlist=["mio.core"])
                predicate = lambda x: isclass(x) and issubclass(x, Object) and getmodule(x) is module and x is not Core
                for name, object in getmembers(module, predicate):
                    yield name, object

    def create_objects(self):
        for name, object in self.load_objects():
            self[name] = object()

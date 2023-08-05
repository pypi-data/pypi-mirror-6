from quixote.directory import Directory, export, subdir

class BaseDir(Directory):

    _q_exports = ['a']

    @export(name='')
    def index(self):
        pass


class SubDir(BaseDir):

    #@export
    def b(self):
        pass



def test_decorator():
    s = SubDir()
    print s._q_exports


test_decorator()

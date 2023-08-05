import py


class TidyChecker(py.test.collect.Item):

    def run(self):
        tidy = py.path.local.sysfind('tidy')
        if not tidy:
            py.test.skip("tidy not installed")
        tidy.sysexec('-qe', self.fspath)


class Module(py.test.collect.Module):

    def run(self):
        #html = self.fspath.read()
        # find links, somehow...
        return ['tidy']

    def join(self, name):
        if name == 'tidy':
            return TidyChecker(self.name, parent=self)


class Directory(py.test.collect.Directory):

    def run(self):
        results = super(Directory, self).run()
        for x in self.fspath.listdir('*.html', sort=True):
            results.append(x.basename)
        return results

    def join(self, name):
        if not name.endswith('.html'):
            return super(Directory, self).join(name)
        p = self.fspath.join(name)
        if p.check(file=1):
            return Module(p, parent=self)

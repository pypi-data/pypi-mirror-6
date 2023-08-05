from pydoctor import epydoc2stan
from pydoctor.test.test_astbuilder import fromText

def test_multiple_types():
    mod = fromText('''
    def f(a):
        """
        @param a: it\'s a parameter!
        @type a: a pink thing!
        @type a: no, blue! aaaargh!
        """
    class C(object):
        """
        @ivar a: it\'s an instance var
        @type a: a pink thing!
        @type a: no, blue! aaaargh!
        """
    class D(object):
        """
        @cvar a: it\'s an instance var
        @type a: a pink thing!
        @type a: no, blue! aaaargh!
        """
    ''')
    # basically "assert not fail":
    epydoc2stan.doc2stan(mod.contents['f'])
    epydoc2stan.doc2stan(mod.contents['C'])
    epydoc2stan.doc2stan(mod.contents['D'])

def test_summary():
    mod = fromText('''
    def single_line_summary():
        """
        Lorem Ipsum

        Ipsum Lorem
        """
    def no_summary():
        """
        Foo
        Bar
        Baz
        Qux
        """
    def three_lines_summary():
        """
        Foo
        Bar
        Baz

        Lorem Ipsum
        """
    ''')
    def get_summary(func):
        def part_flat(x):
            if isinstance(x, list):
                return ''.join(map(part_flat, x))
            else:
                return x
        return part_flat(
            epydoc2stan.doc2stan(
                mod.contents[func],
                summary=True)[0].children)
    assert u'Lorem Ipsum' == get_summary('single_line_summary')
    assert u'Foo Bar Baz' == get_summary('three_lines_summary')
    assert u'No summary' == get_summary('no_summary')

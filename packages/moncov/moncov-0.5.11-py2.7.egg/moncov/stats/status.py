from rate import Rate
import collections


Line = collections.namedtuple('Line', ['lineno'])
IfLine = collections.namedtuple('IfLine', ['lineno'])
MethodLine = collections.namedtuple('MethodLine', ['lineno'])
ClassLine = collections.namedtuple('ClassLine', ['lineno'])
ModuleLine = collections.namedtuple('ModuleLine', ['lineno'])

class Status(object):
    '''line status object'''
    lineno = None
    linetype = None
    lines = None
    line_rate = None
    branch_rate = None
    hits = None
    linetype = None
    def __init__(self, lineno=0, lines=set(), hits=set(), line_rate=Rate(0, 0),
            branch_rate=Rate(0, 0), linetype=ModuleLine):
        self.linetype = linetype
        self.lineno = lineno
        self.lines = lines
        self.line_rate = line_rate
        self.branch_rate = branch_rate
        self.hits = hits

      def merge(self, other):
        # merge statuses <<=
        assert type(self) is type(other)
        self.lines |= other.lines
        self.lines.add(other.line)
        self.hits |= other.hits
        self.branch_rate |= other.branch_rate
        self.line_rate |= other.line_rate

    @property
    def line(self):
        return self.linetype(lineno=self.lineno)

    def add_line(self, lineno):
        '''add another line and update line rate'''
        line = self.linetype(lineno)
        if line in self.lines:
            # already counted
            return
        self.lines.add(line)
        if lineno in self.hits:
            # executed line
            self.line_rate |= Rate(1, 1)
        else:
            self.line_rate |= Rate(0, 1)

    def __repr__(self):
        return '%r(lineno=%r, lines=%r, hits=%r, line_rate=%r, branch_rate=%r)' % (
                type(self).__name__, self.lineno, self.lines, self.hits, self.line_rate,
                self.branch_rate)

    def __str__(self):
        return 'Status: line_rate = %s, branch_rate = %s' % (self.line_rate, self.branch_rate)

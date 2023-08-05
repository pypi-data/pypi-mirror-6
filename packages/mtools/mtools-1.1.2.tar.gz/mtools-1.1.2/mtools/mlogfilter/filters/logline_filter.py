from mtools.util.logline import LogLine
from base_filter import BaseFilter

class LogLineFilter(BaseFilter):
    """ 
    """
    filterArgs = [
        ('--namespace', {'action':'store', 'metavar':'NS', 'help':'only output log lines matching operations on NS.'}),
        ('--operation', {'action':'store', 'metavar':'OP', 'help':'only output log lines matching operations of type OP.'}),
        ('--thread',    {'action':'store', 'help':'only output log lines of thread THREAD.'})
    ]

    def __init__(self, mlogfilter):
        BaseFilter.__init__(self, mlogfilter)

        self.namespace = None
        self.operation = None
        self.thread = None

        if 'namespace' in self.mlogfilter.args and self.mlogfilter.args['namespace']:
            self.namespace = self.mlogfilter.args['namespace']
            self.active = True
        if 'operation' in self.mlogfilter.args and self.mlogfilter.args['operation']:
            self.operation = self.mlogfilter.args['operation']
            self.active = True
        if 'thread' in self.mlogfilter.args and self.mlogfilter.args['thread']:
            self.thread = self.mlogfilter.args['thread']
            self.active = True

    def accept(self, logline):
        if self.namespace and logline.namespace == self.namespace:
            return True
        if self.operation and logline.operation == self.operation:
            return True
        if self.thread and logline.thread == self.thread:
            return True

        return False

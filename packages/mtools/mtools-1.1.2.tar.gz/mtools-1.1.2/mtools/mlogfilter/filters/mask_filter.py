from datetime_filter import DateTimeFilter
from datetime import MINYEAR, timedelta
from mtools.util.logline import LogLine
from mtools.util.logfile import LogFile



class MaskFilter(DateTimeFilter):
    """ This filter takes an argument `--mask <LOGFILE>` and another optional argument
        `--mask-size <SECS>`. It will read <LOGFILE> and for each of the lines extract
        the datetimes (let's call these "events"). It will add some padding for each
        of these events, <SECS>/2 seconds on either side. MaskFilter will then accept
        every line from the original log file (different to <LOGFILE>), that lies within
        one of these masked intervals.

        This feature is very useful to find all correlating lines to certain events.

        For example, find all assertions in a log file, then find all log lines 
        surrounding these assertions:

            grep "assert" mongod.log > assertions.log
            mlogfilter mongod.log --mask assertions.log --mask-size 60

        """


    filterArgs = [
       ('--mask', {'action':'store', 'help':'log file to use for creating the filter mask.'}), 
       ('--mask-size', {'action':'store',  'type':int, 'default':60, 'help':'mask size in seconds around each filter point (default: 60 secs, 30 on each side of the event)'}),
       ('--mask-center', {'action':'store',  'choices':['start', 'end', 'both'], 'default':'end', 'help':'mask center point for events with duration (default: end). If both is chosen, all events from start to end are returned.'})
    ]


    def __init__(self, mlogfilter):
        """ constructor, init superclass and mark this filter active if `mask` argument is present. """
        DateTimeFilter.__init__(self, mlogfilter)
        self.active = ('mask' in self.mlogfilter.args and self.mlogfilter.args['mask'] != None)
        if self.active:
            self.mask_end_reached = False
            self.mask_file = open(self.mlogfilter.args['mask'], 'r')
            self.mask_list = []

    def setup(self):
        """ create mask list consisting of all tuples between which this filter accepts lines. """
        
        # get start and end of the mask log file and set a start_limit
        lfinfo = LogFile(self.mask_file)
        if not lfinfo.start:
            raise SystemExit("Can't parse format of %s. Is this a log file?" % self.mlogfilter.args['mask'])

        self.mask_half_td = timedelta( seconds=self.mlogfilter.args['mask_size'] / 2 )

        # load filter mask file
        logline_list = [ LogLine(line) for line in self.mask_file ]

        # define start and end of total mask
        self.mask_start = lfinfo.start - self.mask_half_td
        self.mask_end = lfinfo.end + self.mask_half_td
        
        # consider --mask-center
        if self.mlogfilter.args['mask_center'] in ['start', 'both']:
            if logline_list[0].duration:
                self.mask_start -= timedelta(milliseconds=logline_list[0].duration)

        if self.mlogfilter.args['mask_center'] == 'start':
            if logline_list[-1].duration:
                self.mask_end -= timedelta(milliseconds=logline_list[-1].duration)

        self.start_limit = self.mask_start

        # event_list = [ll.datetime for ll in logline_list if ll.datetime]

        # different center points
        if 'mask_center' in self.mlogfilter.args:
            if self.mlogfilter.args['mask_center'] in ['start', 'both']:
                starts = [(ll.datetime - timedelta(milliseconds=ll.duration)) if ll.duration else ll.datetime for ll in logline_list if ll.datetime]

            if self.mlogfilter.args['mask_center'] in ['end', 'both']:
                ends = [ll.datetime for ll in logline_list if ll.datetime]

            if self.mlogfilter.args['mask_center'] == 'start':
                event_list = sorted(starts)
            elif self.mlogfilter.args['mask_center'] == 'end':
                event_list = sorted(ends)
            elif self.mlogfilter.args['mask_center'] == 'both':
                event_list = sorted(zip(starts, ends))

        mask_list = []

        if len(event_list) == 0:
            return

        start_point = end_point = None
        
        for e in event_list:
            if start_point == None:
                start_point, end_point = self._pad_event(e)
                continue

            next_start = (e[0] if type(e) == tuple else e) - self.mask_half_td
            if next_start <= end_point:
                end_point = (e[1] if type(e) == tuple else e) + self.mask_half_td
            else:
                mask_list.append((start_point, end_point))
                start_point, end_point = self._pad_event(e)

        if start_point:
            mask_list.append((start_point, end_point))

        self.mask_list = mask_list


    def _pad_event(self, event):
        if type(event) == tuple:
            start_point = event[0] - self.mask_half_td
            end_point = event[1] + self.mask_half_td
        else:
            start_point = event - self.mask_half_td
            end_point = event + self.mask_half_td

        return start_point, end_point


    def accept(self, logline):
        """ overwrite this method in subclass and return True if the provided 
            logline should be accepted (causing output), or False if not.
        """
        dt = logline.datetime
        if not dt:
            return False

        mask = next( (mask for mask in self.mask_list if mask[0] < dt and mask[1] > dt), None )
        
        return True if mask else False


    def skipRemaining(self):
        """ overwrite this method in sublcass and return True if all lines
            from here to the end of the file should be rejected (no output).
        """
        return self.mask_end_reached


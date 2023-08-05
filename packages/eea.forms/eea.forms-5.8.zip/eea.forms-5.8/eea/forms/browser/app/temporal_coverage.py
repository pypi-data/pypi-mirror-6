""" Temporal coverage widget
"""

try:
    from Products.EEAContentTypes.interfaces import ITemporalCoverageAdapter
    HAS_TEMPORALCOVERAGE_ADAPTER = True
except ImportError:
    HAS_TEMPORALCOVERAGE_ADAPTER = False

class FormatTempCoverage(object):
    """ Format temporal coverage display
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        data = []
        if HAS_TEMPORALCOVERAGE_ADAPTER:
            try:
                adapter = ITemporalCoverageAdapter(self.context)
                data = adapter.value()
            except (AttributeError, TypeError):
                return False
        else:
            field = self.context.getField('temporalCoverage')
            if field:
                data = field.getAccessor(self.context)()
                if not data:
                    return False

        data = sorted(list(data))

        #in one odd case, the data is sorted in the wrong way, so we reverse
        #only if we need to
        if len(data) > 1 and (int(data[-1]) < int(data[0])):
            data.reverse()

        tmp_res = []
        res = ''

        for index, year in enumerate(data):
            if len(tmp_res) == 0:
                tmp_res.append(str(year))
            else:
                if int(data[index - 1]) + 1 == int(year):
                    tmp_res.append('-%s' % str(year))
                else:
                    tmp_res.append(str(year))

        for index, year in enumerate(tmp_res):
            if index == 0:
                res += year
            elif index + 1 == len(tmp_res):
                res += ', %s' % year
            elif not year.startswith('-'):
                res += ', %s' % year
            elif not tmp_res[index + 1].startswith('-'):
                res += ', %s' % year
            elif year.startswith('-') and not tmp_res[index + 1].startswith(
                    '-'):
                res += ', %s' % year
            elif year.startswith('-') and tmp_res[index + 1].startswith('-'):
                pass
        return res.replace(', -', '-')


import itertools


class page(str):
    """
    class to represent a page of data for any of the types
    """
    @classmethod
    def fromPackets(self, packets):
        """
        given a BIRDpackets class create a list of pages
        """
        _seqnum = [p.seqnum for p in packets]
        _seqidx = [p.seqidx for p in packets]
        _pktnum = [p.pktnum for p in packets]
        _grtval = [p.grt for p in packets]
        """
        need tp look at _pktnum to look for missing packets in the page
        For example I have packet 1,2,4,5,6,7,8,9,a,b,c,d,e,f,10,11,12,13 (one page)
        (3 is missing)
        when pktnum skips a number between 1 and 13 hex inset a None into the page data
        then when decoding the page data when a None is encoutered the data up to the None
        is truncated (maybe recoverable) and then a sliding windew is needed asfter the
        None to get back on track with valid data.
        """
        # how many pages are in the file?
        # count through the seqidx and see if it repeats
        npages = 0
        pages = []
        pg = ''
        for ii, (sn, si, pn) in enumerate(itertools.izip( _seqnum, _seqidx, _pktnum)):
            """
            this need rework because it depends on getting packet 01 of the page
            look at each (sn, si, pn) to identify the start of a new page

            this all then needs to return a list of page class objects
            """
            if pn == '01' and pg: # start of a new page
                pages.append(pg)
                pg = ''
            elif pn == '01':
                pg = ''
            if pg:
                pg += ' '
            pg += ' '.join(packets[ii].data)
        pages.append(pg)
        return [page(p) for p in pages]


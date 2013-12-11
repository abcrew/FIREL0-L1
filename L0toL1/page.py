
import itertools


class page(str):
    """
    class to represent a page of data for any of the types
    """
    @classmethod
    def fromPackets(self, packets, fullreturn=False):
        """
        given a BIRDpackets class create a list of pages
        """
        _seqnum = [p.seqnum for p in packets]
        _seqidx = [p.seqidx for p in packets]
        _pktnum = [p.pktnum for p in packets]
        _grtval = [p.grt for p in packets]
        """
        need to look at _pktnum to look for missing packets in the page
        For example I have packet 1,2,4,5,6,7,8,9,a,b,c,d,e,f,10,11,12,13 (one page)
        (3 is missing)
        when pktnum skips a number between 1 and 13 hex inset a None into the page data
        then when decoding the page data when a None is encoutered the data up to the None
        is truncated (maybe recoverable) and then a sliding windew is needed asfter the
        None to get back on track with valid data.
        """
        pages = []
        outval = []
        pages_info = []
        curr_info  = []
        pn = packets[0].pktnum
        # the first packet in a L0 file is a new page
        #   if a page is downlinked across the day boundry maybe not
        #   but we will ignore that for now
        n_packets = 0
        n_pages = 0
        for ii, (p, si, pn) in enumerate(itertools.izip(packets, _seqidx, _pktnum)):
            if ii == 0:
                # this is the first on a file, put it into a page
                outval.extend(p.data)
                curr_info.extend([p.pktnum]*len(p.data))
                # and update the current seqindex and paketnumber
                si1 = si
                pn1 = pn
            elif si == si1 and pn > pn1:
                # add in None for each missing paketnumber
                #   Note that [None]*0 is an empty list
                #  TODO working here
                nNone = (int(pn, 16)-int(pn1, 16)-1)
                outval.extend([None]*nNone)
                curr_info.extend(p.pktnum)
                curr_info.extend([None]*nNone)
                if nNone:
                    print("Found a missing packet before, GRT:{3} num:{0}:{1}:{2}".format(p.seqnum,
                                                                                          p.seqidx,
                                                                                          p.pktnum,
                                                                                          p.grt.isoformat()))

                # now add the data from this packet into the working page
                outval.extend(p.data) # put this into page
                # and update the current seqindex and paketnumber
                si1 = si
                pn1 = pn
            elif (si == si1 and pn < pn1) or si != si1:
                # this means we asked for two 1-page downlinks in a row
                # so then we are done with the previous page
                pages.append(outval)
                outval = []
                nNone = (int(pn, 16)-1)
                outval.extend([None]*nNone)
                if nNone:
                    print("Found a missing packet before, GRT:{3} num:{0}:{1}:{2}".format(p.seqnum,
                                                                                          p.seqidx,
                                                                                          p.pktnum,
                                                                                          p.grt.isoformat()))
                # now add the data from this packet into the working page
                outval.extend(p.data) # put this into page
                # and update the current seqindex and paketnumber
                si1 = si
                pn1 = pn
            else:
                raise(RuntimeError("Should not have gotten here, page"))

        if outval:
            pages.append(outval)
        # return a list of data values with None separating
        #   each of the packets
        return pages


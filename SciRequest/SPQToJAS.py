#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SPQToJAS.py

Take a SPQ file and output a JAS script for the operator

"""

# standard library includes (alphabetical)
import datetime
from optparse import OptionParser
import os
import re


header = """PROC {file_name} (int Request_Index)

string operatorLogFileName, dateStr, response, command
string Data_Type_List[{num_requests}]
int    Request_Time_Duration_List[{num_requests}, 7]
int    Request_Index_Max
int    done

BEGIN
/* */
/* init operator log */
dateStr = REPLACE(SUBSTR(TOSTRING(NOW()), 0, 10), "/", "-")
operatorLogFileName = CONCAT("C:\\\\FIREBIRD\\\\FU_{flight_unit_num}\\\\Operator_Logs\\\\FU_{flight_unit_num}_", dateStr, ".log")
FILE_OPEN(operatorLogFileName, true)
FILE_WRITE(operatorLogFileName, "%s Starting of JAS Script: {file_name}.jpp", TOSTRING(NOW()))
FILE_WRITE(operatorLogFileName, "%s Request_Index = %d", TOSTRING(NOW()), Request_Index)
/* */

/* */
/* init vars */
done = FALSE
Request_Index_Max = {num_requests}
/* */

/* */
/* SPQ Data */
"""

spq_data = """
Data_Type_List[{idx}] = "{data_type}"
Request_Time_Duration_List[{idx}][0] = {year}
Request_Time_Duration_List[{idx}][1] = {month}
Request_Time_Duration_List[{idx}][2] = {day}
Request_Time_Duration_List[{idx}][3] = {hour}
Request_Time_Duration_List[{idx}][4] = {minute}
Request_Time_Duration_List[{idx}][5] = {second}
Request_Time_Duration_List[{idx}][6] = {duration}
"""
            
body = """

/* ready? */
response = PROMPT("Confirmation", "Send first command?")

WHILE ((NOT done) AND (Request_Index < Request_Index_Max))
    
    /* execute request */
    if(CONTAINS(Data_Type_List[Request_Index], "DATA_TIMES"))
        CMD "MFIB_GET_DATA_TIMES" ("IMMEDIATE", 0, 0, 0)
    ELSE
        command = CONCAT("MFIB_GET_", Data_Type_List[Request_Index], "_DATA_AT_TIME")
        CMD command ("IMMEDIATE", 0, 0, 0, Request_Time_Duration_List[Request_Index][0], Request_Time_Duration_List[Request_Index][1], Request_Time_Duration_List[Request_Index][2], Request_Time_Duration_List[Request_Index][3], Request_Time_Duration_List[Request_Index][4], Request_Time_Duration_List[Request_Index][5], Request_Time_Duration_List[Request_Index][6])
    ENDIF
    /* */

    /* what happenend? */
    response = PROMPT("PushButton", "What happened?", "Response_Decoded", "Response_Decoded", "Response_NOT_Decoded", "No_Response")
    /* */
    
    /* write response to AWE and operator log */
    SEND_AWE(AWE.Event_1, "%s %s %d-%d-%d %d:%d:%d, %d", response, Data_Type_List[Request_Index], 2000+Request_Time_Duration_List[Request_Index][0], Request_Time_Duration_List[Request_Index][1], Request_Time_Duration_List[Request_Index][2], Request_Time_Duration_List[Request_Index][3], Request_Time_Duration_List[Request_Index][4], Request_Time_Duration_List[Request_Index][5], Request_Time_Duration_List[Request_Index][6])
    FILE_WRITE(operatorLogFileName, "%s %s %s %d, %d, %d, %d, %d, %d, %d", TOSTRING(NOW()), response, Data_Type_List[Request_Index], Request_Time_Duration_List[Request_Index][0], Request_Time_Duration_List[Request_Index][1], Request_Time_Duration_List[Request_Index][2], Request_Time_Duration_List[Request_Index][3], Request_Time_Duration_List[Request_Index][4], Request_Time_Duration_List[Request_Index][5], Request_Time_Duration_List[Request_Index][6])
    /* */
    
    /* what do we want to do? */
    response = PROMPT("PushButton", "What Next?", "Execute_Next_Request", "Execute_Next_Request", "Rexecute_Last_Request", "End_Pass")
    SWITCH (response)
      CASE "End_Pass"
         done = TRUE
      ENDCASE      
      CASE "Execute_Next_Request"
          Request_Index = Request_Index + 1
        IF (Request_Index >= Request_Index_Max)
             SEND_AWE(AWE.Event_1, "No more Requests.")
            done = TRUE
        ENDIF
      ENDCASE      
      CASE "Rexecute_Last_Request"
        //Request_Index = Request_Index
      ENDCASE      
      CASE_DEFAULT
          SEND_AWE(AWE.Warning_1, "Error: Invalid prompt response!")
      ENDCASE
    
    ENDSWITCH
    
ENDWHILE
"""

footer = """
/* done with pass, close things out */
FILE_WRITE(operatorLogFileName, "%s Request_Index = %d", TOSTRING(NOW()), Request_Index)
FILE_WRITE(operatorLogFileName, "%s End of JAS Script", TOSTRING(NOW()))
FILE_WRITE(operatorLogFileName, "")
FILE_CLOSE(operatorLogFileName)

ENDPROC
"""


# SPQ format:
#  HIRES, 2013, 12, 6, 14, 31, 0, 60, FU_2_JAS_0043_20131209_0716.jpp
#  HIRES, 2013, 12, 6, 14, 31, 0, 60, None


# this is type, then seconds of data per block
typeDict = {'HIRES':None,
            'CONTEXT':None,
            'MICRO_BURST':None,
            'CONFIG':None,
            'DATA_TIMES':None} # This was a TBD and 2000 was made up

def toNone(inval):
    if inval in [0, 'NONE', 'None']:
        return None
    else:
        return inval

def NoneToStr(inval):
    if inval is None:
        return 'NONE'
    else:
        return inval
        
def NoneToZero(inval):
    if inval == '':
        return "0"
    else:
        return inval


class SPQline(object):
    
    def __init__(self, inline):
        """ take a line of a file and parse into this object  """
        p_line = inline.split(',')
        p_line = [v.strip() for v in p_line]
        if p_line == ['']: # empty line
            return
        self.data_type = p_line[0].upper()
        if self.data_type not in typeDict.keys():
            raise(ValueError("Did not understand data_type, {0}  must be {1}".format(self.data_type, ' '.join(typeDict.keys()))))
        self.year = p_line[1].replace("20", "")
        self.month = p_line[2]
        self.day = p_line[3]
        self.hour = p_line[4]
        self.minute = p_line[5]
        self.second = p_line[6]
        self.duration = p_line[7]
        self.JAS = toNone(p_line[8])
        if self.data_type != "DATA_TIMES":
            self.dt = datetime.datetime(int(self.year), int(self.month), int(self.day),
                                        int(self.hour), int(self.minute), int(self.second))
        else:
            self.dt = None
            
        self.idx = None
            
    def __str__(self):
        outstr = ', '.join([self.data_type, NoneToZero(self.year), NoneToZero(self.month), NoneToZero(self.day),
                            NoneToZero(self.hour), NoneToZero(self.minute), NoneToZero(self.second), NoneToStr(self.JAS)])
        return outstr
        
    def toJAS(self):
        """ 
        Creates a JAS block for defining the SPQ's info in JAS.
        """
        
        return spq_data.format(**self.__dict__)
    
    __repr__ = __str__


class SPQfile(list):
    def __init__(self):
        self.comments = []
        self.file_name = None
    
    def addLine(self, inobj):
        if not isinstance(inobj, SPQline):
            raise(ValueError("Invalid input data_type"))
        self.append(inobj)

    def addComment(self, inobj):
        self.comments.append(inobj)

    def __str__(self):
        outstr = '\n'.join(self.comments)
        outstr += '\n'.join(self)
        return outstr
    
    __repr__ = __str__

    def toFile(self, outname):
        with open(outname, 'w') as fp:
            for v in self.comments:
                fp.writelines(v + '\n')
            for v in self:
                fp.writelines(str(v) + '\n')
        print("Wrote: {0}".format(os.path.abspath(outname)))
        
    def toJAS(self):
        outValue = header.format(file_name= self.file_name.replace(".csv", ""), 
            num_requests= len(self), 
            flight_unit_num=self.FU_Num_From_SPQ())
        for i,f in enumerate(self):
            f.idx = i
            if f.data_type == "DATA_TIMES":
                f.year = "0"
                f.month = "0"
                f.day = "0"
                f.hour = "0"
                f.minute = "0"
                f.second = "0"
                f.duration = "0"
            outValue += f.toJAS()
        outValue += body
        outValue += footer
        
        return outValue
        
    def FU_Num_From_SPQ(self):
        """
        Extracts FU number from file name
        """
        temp = re.match(r".*FU\_([1234])\_SPQ\_20\d{6}\_v\d\d\.csv", self.file_name)
        if temp:
            return temp.groups()[0]
        else:
            return None

def parseFile(infile):
    with open(infile, 'r') as fp:
        lines = fp.readlines()
    spqf = SPQfile()
    for spql in lines:
        if spql[0] == '#':
            spqf.addComment(spql)
            continue
        tmp = SPQline(spql)
        if hasattr(tmp, 'data_type'): # else a blank line
            spqf.addLine(tmp)
    return spqf
    

if __name__ == '__main__':
    usage = "usage: %prog [options] infile"
    parser = OptionParser(usage=usage)

    parser.add_option("-f", "--force",
                  action="store_true", dest="force",
                  help="Force an overwrite, default=False", default=False)
    parser.add_option("-o", "--outfile",
                      dest="outfile",
                      help="Use a difference output filename", default=None)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments")

    if not os.path.isfile(args[0]):
        raise(OSError("Input file: {0} not found".format(args[0])))

    if options.outfile is None:
        options.outfile = args[0] + ".processed"
    
    if os.path.isfile(options.outfile) and not options.force:
        raise(RuntimeError("Outfile: {0} exists and will not overwrite, try --force".format(options.outfile)))

    spq = parseFile(args[0])
    spq.file_name = os.path.basename(options.outfile.replace(".processed", ""))
    
    
    if os.path.isfile(options.outfile):
        os.remove(options.outfile)

    """
    add JAS stuff here
    """
    JASString = spq.toJAS()
    
    outputFileName = os.path.basename(spq.file_name.replace(".csv", ".jpp").replace(".processed", ""))
    
    outPath = os.path.join("C:\\", "FIREBIRD", "FU_{0}".format(spq.FU_Num_From_SPQ()), "JAS_Files")    
    with open(os.path.join(outPath, os.path.basename(outputFileName)), "w") as fp:
        fp.write(JASString)
        print("Wrote: {0}".format(os.path.join(outPath, os.path.basename(outputFileName))))
		
		
	outPath = os.path.join("C:\\", 
	    "MSU", 
		"InControl-NG-Data", 
		"MSU-Data-5.8.14.1.37607", 
		"scopedData", 
		"Shared", 
		"FIREBIRD", 
		"procedures", 
		"FU_{0}".format(spq.FU_Num_From_SPQ()), 
		"FU_{0}_Scheduled".format(spq.FU_Num_From_SPQ()))
    with open(os.path.join(outPath, os.path.basename(outputFileName)), "w") as fp:
        fp.write(JASString)
        print("Wrote: {0}".format(os.path.join(outPath, os.path.basename(outputFileName))))


#########################################################
#
#  David Fetterer, Social And Scientrific Systems
#  Command line interface for define.xml
#
#########################################################



import argparse;
import define;
from sys import exit;



parser = argparse.ArgumentParser(description='Create A define.xml for SDTM')
parser.add_argument('ExcelFile', metavar='ExcelFile', type=str, nargs=1, help='Full Name of Excle file, see resource folder for example.  Follows cidsic end to end chptr 2')
parser.add_argument('XMLFile', metavar='XMLFile', type=str, nargs=1, help='Name of define.xml output file')
args = parser.parse_args()

try:
   with open(args.ExcelFile[0]):
       pass
except IOError:
   print 'File not found';
   exit(1);


A = define.define();
A.fromExcel(args.ExcelFile[0]);
A.validateXML();
print( A.isXMLValid );
A.writeXML(args.XMLFile[0]);




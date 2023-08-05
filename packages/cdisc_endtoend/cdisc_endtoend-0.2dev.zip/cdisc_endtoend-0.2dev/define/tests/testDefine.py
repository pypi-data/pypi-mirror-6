
import unittest;
import define;

class Test_define(unittest.TestCase):
      
    # test A checks that the fromExcel function works correctly
    def test_a(self):
        A = define.define();
        A.fromExcel('define\\resource\\sdtm_metadata.xlsx');
        self.assertEqual( A.readSuccess, 1);

    # test B checks that XML validation 
    # is successful for the example docs
    # provided by the CDISC standard
    def test_b(self):
        def runFile(filename):
            A = define.define();
            A.loadFromFile(filename);
            A.validateXML();
            self.assertEqual( A.isXMLValid, 1);
        runFile("define\\resource\\define_ex3.xml");
        runFile("define\\resource\\define_ex2.xml");
        runFile("define\\resource\\define_ex1.xml");

    # Now we test that a non sense xml will fail; 
    def test_c(self):
        def runFile(filename):
            A = define.define();
            A.loadFromFile(filename);
            A.validateXML();
            self.assertEqual( A.isXMLValid, 0);
        runFile("define\\resource\\books.xml");

    # A sort of manual test, Write back the results of converting
    # the cdisc end to end book example excel file to xml
    def test_d(self):
        A = define.define();
        A.fromExcel('define\\resource\\sdtm_metadata.xlsx');
        A.writeXML('define\\tests\\test_d.xml');
        A.validateXML();
        self.assertEqual( A.isXMLValid, 1);


if __name__ == '__main__':
    unittest.main();


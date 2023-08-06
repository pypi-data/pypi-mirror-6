import unittest
from test.mock import Mock, patch
import sys
from lizard import print_warnings, print_and_save_detail_information, FunctionInfo, FileInformation,\
    print_result, XMLFormatter, get_extensions

class StreamStdoutTestCase(unittest.TestCase):
    def setUp(self):
        self.savedStdout = sys.stdout 
        sys.stdout = self.StreamForTest()
    
    def tearDown(self):
        sys.stdout = self.savedStdout

    class StreamForTest:
        
        def __init__(self):
            self.stream = ""
            
        def write(self, x):
            self.stream += str(x)
            
        def __getattr__(self, attr):
            return getattr(self.stream, attr)    

class TestFunctionOutput(StreamStdoutTestCase):

    def setUp(self):
        StreamStdoutTestCase.setUp(self)
        self.options = Mock(warnings_only=False, extensions = get_extensions([]))

    def test_function_info_header_should_have_a_box(self):
        print_and_save_detail_information([], self.options)
        self.assertIn("=" * 20, sys.stdout.stream.splitlines()[0])

    def test_function_info_header_should_have_the_captions(self):
        print_and_save_detail_information([], self.options)
        self.assertEquals("  NLOC    CCN   token  PARAM  function@line@filename          ", sys.stdout.stream.splitlines()[1])

    def test_function_info_header_should_have_the_captions_of_external_extensions(self):
        external_extension = Mock(FUNCTION_CAPTION = "*external_extension*")
        self.options = Mock(warnings_only=False, extensions = get_extensions([external_extension]))
        print_and_save_detail_information([], self.options)
        self.assertEquals("  NLOC    CCN   token  PARAM *external_extension* function@line@filename          ", sys.stdout.stream.splitlines()[1])

    def test_print_fileinfo(self):
        fun = FunctionInfo("foo", 100)
        fun.end_line = 100
        fun.cyclomatic_complexity = 16
        fileStat = FileInformation("FILENAME", 1, [fun])
        print_and_save_detail_information([fileStat], self.options)
        self.assertEquals("       0     16      1      0 foo@100-100@FILENAME", sys.stdout.stream.splitlines()[3])

class TestWarningOutput(StreamStdoutTestCase):
        
    def test_should_have_header_when_warning_only_is_off(self):
        option = Mock(warnings_only=False, CCN=15, extensions = [])
        print_warnings(option, [])
        self.assertIn("Warnings (CCN > 15)", sys.stdout.stream)

    def test_should_say_no_warning_when_warning_only_is_off(self):
        option = Mock(warnings_only=False, CCN=15, extensions = [])
        print_warnings(option, [])
        self.assertIn("No warning found. Excellent!\n", sys.stdout.stream)

    def test_should_not_have_header_when_warning_only_is_on(self):
        option = Mock(warnings_only=True, CCN=15)
        print_warnings(option, [])
        self.assertNotIn("Warnings (CCN > 15)", sys.stdout.stream)

    def test_should_use_clang_format_for_warning(self):
        option = Mock(display_fn_end_line = False, extensions = get_extensions([]))
        print_warnings(option, [(FunctionInfo("foo", 100), "FILENAME")])
        self.assertIn("FILENAME:100: warning: foo has 1 CCN and 0 params (0 NLOC, 1 tokens)\n", sys.stdout.stream)

    def test_should_use_clang_format_with_function_end_line_number_for_warning(self):
        fun = FunctionInfo("foo", 100)
        fun.end_line = 100
        fun.cyclomatic_complexity = 16
        fileStat = FileInformation("FILENAME", 1, [fun])
        option = Mock(display_fn_end_line = True, extensions = get_extensions([])) 
        print_warnings(option, [(fun, "FILENAME")])
        self.assertIn("FILENAME:100-100: warning: foo has 16 CCN and 0 params (0 NLOC, 1 tokens)\n", sys.stdout.stream)

    @patch('lizard.print_function_info')
    def test_sort_warning(self, print_function_info):
        option = Mock(display_fn_end_line = False, extensions = get_extensions([]))
        option.sorting = ['cyclomatic_complexity']
        foo = FunctionInfo("foo", 100)
        foo.cyclomatic_complexity = 10
        bar = FunctionInfo("bar", 100)
        bar.cyclomatic_complexity = 15
        print_warnings(option, [(foo, "FILENAME"),(bar, "FILENAME")])
        self.assertEqual('bar', print_function_info.call_args_list[0][0][0].name)

    def test_sort_warning_with_generator(self):
        option = Mock(display_fn_end_line = False, extensions = get_extensions([]))
        option.sorting = ['cyclomatic_complexity']
        print_warnings(option, (x for x in []))


class TestFileOutput(StreamStdoutTestCase):
    
    def test_print_and_save_detail_information(self):
        fileSummary = FileInformation("FILENAME", 123, [])
        print_and_save_detail_information([fileSummary], Mock(warnings_only=False, extensions=[]))
        self.assertIn("    123      0      0         0         0     FILENAME", sys.stdout.stream)

    def test_print_file_summary_only_once(self):
        print_and_save_detail_information(
                            [FileInformation("FILENAME1", 123, []), 
                             FileInformation("FILENAME2", 123, [])], Mock(warnings_only=False, extensions=[]))
        self.assertEqual(1, sys.stdout.stream.count("FILENAME1"))

    
class TestAllOutput(StreamStdoutTestCase):
    def test_print_extension_results(self):

        file_infos = []
        extension = Mock()
        option = Mock(CCN=15, number = 0, extensions = [extension], whitelist='')
        print_result(file_infos, option)
        self.assertEqual(1, extension.print_result.call_count)

    def test_should_not_print_extension_results_when_not_implemented(self):
        file_infos = []
        option = Mock(CCN=15, number = 0, extensions = [object()], whitelist='')
        print_result(file_infos, option)

    @patch.object(sys, 'exit')
    def test_print_result(self, mock_exit):
        file_infos = [FileInformation('f1.c', 1, []), FileInformation('f2.c', 1, [])]
        option = Mock(CCN=15, number = 0, extensions=[], whitelist='')
        print_result(file_infos, option)
        self.assertEqual(0, mock_exit.call_count)

    @patch.object(sys, 'exit')
    def test_exit_with_non_zero_when_more_warning_than_ignored_number(self, mock_exit):
        fun = FunctionInfo("foo", 100)
        fun.cyclomatic_complexity = 16
        file_infos = [FileInformation('f1.c', 1, [fun])]
        option = Mock(CCN=15, number = 0, extensions=[], whitelist='')
        print_result(file_infos, option)
        mock_exit.assert_called_with(1)

    @patch.object(sys, 'exit')
    def test_whitelist(self, mock_exit):
        fun = FunctionInfo("foo", 100)
        fun.cyclomatic_complexity = 16
        file_infos = [FileInformation('f1.c', 1, [fun])]
        option = Mock(CCN=15, number = 0, extensions=[], whitelist='foo')
        print_result(file_infos, option)
        self.assertEqual(0, mock_exit.call_count)

    def test_null_result(self):
        file_infos = [FileInformation('f1.c', 1, []), None]
        option = Mock(CCN=15, number = 0, extensions=[], whitelist='')
        print_result(file_infos, option)



import xml.etree.ElementTree as ET
class TestXMLOutput(unittest.TestCase):
    
    fun = FunctionInfo("foo", 100)
    fun.cyclomatic_complexity = 16
    file_infos = [FileInformation('f1.c', 1, [fun])]
    option = Mock(CCN=15, number = 0, extensions=[])
    xml = XMLFormatter().xml_output(file_infos, option)
    
    def test_xml_output(self):
        root = ET.fromstring(self.xml)
        item = root.findall('''./measure[@type="Function"]/item[0]''')[0]
        self.assertEqual('''foo at f1.c:100''', item.get("name"))

    def test_xml_stylesheet(self):
        self.assertIn('''<?xml-stylesheet type="text/xsl" href="https://raw.github.com/terryyin/lizard/master/lizard.xsl"?>''', self.xml)
        
        

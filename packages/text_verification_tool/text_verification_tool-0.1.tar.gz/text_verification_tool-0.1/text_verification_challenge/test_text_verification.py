import unittest

import text_verification


class TestTextVerificationChallengeFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_convert_pdf_to_string(self):
        target = u'U.S. Patent No. 7,010,508 (\u201cthe \u2019508 Patent\u201d; Ex. 1007) issued March 7, 2006 and is \nassigned to Landmark Technologies LLC (\u201cLandmark\u201d). Each of claims 1-17 of the \u2019508 \nPatent is unpatentable for two independent reasons. First, the specification of the \u2019508 \nPatent fails to disclose a structure for many of the means-plus-function elements in the \nclaims. Second, every element of each of those claims was known in the prior art, \nincluding the use of so-called \u201cforwardchaining\u201d \u2013 the alleged inventive feature of the \n\u2019508 Patent.\n\n\x0c'
        content  =  text_verification.convert_pdf_to_string('S1-Source.pdf')
        self.assertEqual(content, target)


    def test_convert_xml_to_string(self):
        content = text_verification.convert_xml_to_string('S1-Target.xml')
        self.assertTrue('<?xml' not in content)
        self.assertTrue('</w:wordDocument>' not in content)

    def test_convert_html_to_string(self):
        target = u'\r\nU.S.\r\nPatent No. 7,010,508 (\u201cthe \u2019508 Patent\u201d; Ex. 1007)\r\nissued March 7, 2006 and is assigned to Landmark Technologies LLC\r\n(\u201cLandmark\u201d). Each of claims 1-17 of the \u2019508\r\nPatent is unpatentable for two independent reasons. First, the\r\nspecification of the \u2019508 Patent fails to disclose a structure\r\nfor many of the means-plus-function elements in the claims. Second,\r\nevery element of each of those claims was known in the prior art,\r\nincluding the use of so-called \u201cforwardchaining\u201d \u2013\r\nthe alleged inventive feature of the \u2019508 Patent.\r\n'
        content = text_verification.convert_html_to_string('S1-Source.html')
        self.assertEqual(content, target)

    def test_replace_line_breaks_with_space(self):
        text = u'\r\nU.S.\r\nPatent No. 7,010,508 (\u201cthe \u2019508 Patent\u201d; Ex. 1007)\r\nissued March 7, 2006 and is assigned to Landmark Technologies LLC\r\n(\u201cLandmark\u201d). Each of claims 1-17 of the \u2019508\r\nPatent is unpatentable for two independent reasons. First, the\r\nspecification of the \u2019508 Patent fails to disclose a structure\r\nfor many of the means-plus-function elements in the claims. Second,\r\nevery element of each of those claims was known in the prior art,\r\nincluding the use of so-called \u201cforwardchaining\u201d \u2013\r\nthe alleged inventive feature of the \u2019508 Patent.\r\n'
        processed_text = text_verification.replace_line_breaks_with_space(text)
        self.assertTrue('\n' not in processed_text and '\r\n' not in processed_text and '\r' not in processed_text)

    def test_replace_tabs_with_space(self):
        text = u'abc \t def \r\t ghi'
        processed_text = text_verification.replace_tabs_with_space(text)
        self.assertTrue('\t' not in processed_text and '\r\t' not in processed_text)


    def test_remove_extra_space_within_sentence(self):
        text = u' abc  def   ghi '
        processed_text = text_verification.remove_extra_space_within_sentence(text)
        self.assertEqual('abc def ghi', processed_text)

    def test_remove_all_space_within_sentence(self):
        text = u' abc  def   ghi '
        processed_text = text_verification.remove_all_space_within_sentence(text)
        self.assertEqual('abcdefghi', processed_text)

    def test_remove_extra_blank_lines(self):
        text = u'abc\n\ndef\n\nghi\n\n'
        processed_text = text_verification.remove_extra_blank_lines(text)
        self.assertEqual(u'abc\ndef\nghi',processed_text)

    def test_splitParagraphIntoSentences(self):
        text1 = u'abc,def'
        text1_ = u'abc\ndef'
        text2 = u'abc.def'
        text2_ = u'abc\ndef'
        text3 = u'abc?def'
        text3_ = u'abc\ndef'
        text4 = u'abc!def'
        text4_ = u'abc\ndef'
        self.assertEqual(text_verification.splitParagraphIntoSentences(text1),text1_)
        self.assertEqual(text_verification.splitParagraphIntoSentences(text2),text2_)
        self.assertEqual(text_verification.splitParagraphIntoSentences(text3),text3_)
        self.assertEqual(text_verification.splitParagraphIntoSentences(text4),text4_)


    def test_re_format_text(self):
        pass

    def test_write_string_to_file(self):
        pass

    def test_find_between(self):
        text = u'abc123def'
        target = u'c123d'
        target2 = u'c123def'
        self.assertEqual(text_verification.find_between(text,'c','d'), target)
        self.assertEqual(text_verification.find_between(text,'c'), target2 )

    def test_get_break_points(file):
        pass


if __name__ == '__main__':
    unittest.main()

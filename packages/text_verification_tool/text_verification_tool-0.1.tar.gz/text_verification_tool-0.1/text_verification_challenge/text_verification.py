# -*- coding: utf-8 -*-
#TODO - enable program to read form a from to get the start and end points for comparision.
#TODO - enable support for doc, docx, and RTF. These are not well suppporte by python. but can
#be added through third-party library
#FIXME: when reading pdf, it reads vertically, when reading html, it reads horitionally.
#this is causing a lot of trouble when there are tables in pdf/html
#i think the probelm is within pdfminer, it break the order. need to fix it.


ignored_ns =[
    '{urn:schemas-microsoft-com:office:office}Author',
    '{urn:schemas-microsoft-com:office:office}LastAuthor',
    '{urn:schemas-microsoft-com:office:office}Revision',
    '{urn:schemas-microsoft-com:office:office}TotalTime',
    '{urn:schemas-microsoft-com:office:office}Created',
    '{urn:schemas-microsoft-com:office:office}LastSaved',
    '{urn:schemas-microsoft-com:office:office}Pages',
    '{urn:schemas-microsoft-com:office:office}Words',
    '{urn:schemas-microsoft-com:office:office}Characters',
    '{urn:schemas-microsoft-com:office:office}Paragraphs',
    '{urn:schemas-microsoft-com:office:office}Editor',
    '{urn:schemas-microsoft-com:office:office}CustomDocumentProperties'
]


#TODO test
def convert_txt_to_string(txt_file):
    import codecs
    with codecs.open(txt_file, 'U',"utf-8") as f:
        content = f.readlines()
        return ''.join(content)

def convert_pdf_to_string(pdf_file):
    """
    input:pdf file
    output:string
    format:same as pdf file
    """
    import subprocess
    s=subprocess.Popen(['pdf2txt.py', pdf_file],stdout=subprocess.PIPE)
    out, err = s.communicate()
    try:
        unicode_out = out.decode('utf8')
        return unicode_out
    except:
        return out

def convert_xml_to_string(xml_file):
    """
    input:xml file
    output:string
    """
    from lxml import etree
    tree = etree.parse(xml_file)
    root = tree.getroot()
    all_content = root.xpath('//text()')
    body_content = []
    #filter out text content belong to certain name spaces.
    for item in all_content:
        if item.getparent().tag in ignored_ns:
            continue
        else:
            body_content.append(item)
    res = ''.join(body_content)
    return res


def convert_html_to_string(html_file):
    """
    input:html file
    output: string
    """
    from lxml.html import parse
    page=parse(html_file).getroot()
    res = page.body.text_content()
    return res

def replace_line_breaks_with_space(text):
    tmp  = text.replace("\n"," ").replace("\r"," ").replace("\r\n"," ")
    return tmp

def replace_tabs_with_space(text):
    tmp  = text.replace("\r\t"," ").replace("\t"," ")
    return tmp

def remove_extra_space_within_sentence(text):
    tmp  = ' '.join(text.split())
    return tmp

def remove_all_space_within_sentence(text):
    tmp  = ''.join(text.split())
    return tmp

def splitParagraphIntoSentences(paragraph):
    ''' break a paragraph into sentences
        and return a list

        after break, there should be no ,.!? sign
        in each sentence.

        note: this basically also means ,.!? are excluded
        from comparasion effectively. If the solution
        request strict comparasion of text including
        these signs, this program will not work
        '''
    import re
    sentenceEnders = re.compile('[,.!?]') #add comma
    sentenceList = sentenceEnders.split(paragraph)
    return '\n'.join(sentenceList)

def remove_extra_blank_lines(text):
    list = [line for line in text.split('\n') if line.strip() != '']
    return '\n'.join(list)


def find_between(s, first, last=None):
    try:
        start = s.index(first)
        if last is None:
            end = len(s)
        else:
            end = s.index(last,start) + len(last)
        return s[start:end]
    except ValueError:
        return""



def re_format_input_text(text):
    s1 = replace_line_breaks_with_space(text)
    s2 = replace_tabs_with_space(s1)
    s3 = remove_all_space_within_sentence(s2)
    return s3


def read_start_end_points(file):
    try:
        content = open(file, 'U').readlines()
        print content
    except:
        raise
    start_end_list = []
    for i in range(len(content)):
       start,end = content[i].split(":")
       start_end_list.append([re_format_input_text(start),re_format_input_text(end)])
    return start_end_list


def re_structure_text(file, config_file):
    content = generate_file_content(file)
    start_end_list = read_start_end_points(config_file)
    new_content = []
    for i in range(len(start_end_list)):
        new_content.append(find_between(content, start_end_list[i][0], start_end_list[i][1]))
    return '\n'.join(new_content)


def re_format_text(text):
    s1 = replace_line_breaks_with_space(text)
    s2 = replace_tabs_with_space(s1)
    s3 = remove_all_space_within_sentence(s2)
    s4 = splitParagraphIntoSentences(s3)
    s5 = remove_extra_blank_lines(s4)
    return s5

def write_string_to_file(string, filename):
    import codecs
    if not string:
        raise 'no string provided'
    if not filename:
        raise 'please input filename'
    with codecs.open(filename, 'w',"utf-8") as f:
        try:
            #f.write(string.encode('utf8'))
            f.write(string)
            #print 'Done'
        except:
            print 'cannot write to file'

#TODO test
def judge_file_format(file):
    import os
    file_name = os.path.basename(file)
    if file_name.lower().endswith('.txt'):
        return 'txt'
    elif file_name.lower().endswith('.pdf'):
        return 'pdf'
    elif file_name.lower().endswith('.xml'):
        return 'xml'
    elif file_name.lower().endswith('.html'):
        return 'html'
    else:
        return 'unsupported'


def generate_file_content(file):
    file_format = judge_file_format(file)
    #print file_format
    if file_format == 'txt':
        content = re_format_text(convert_txt_to_string(file))
    elif file_format == 'pdf':
        content = re_format_text(convert_pdf_to_string(file))
    elif file_format == 'xml':
        content = re_format_text(convert_xml_to_string(file))
    elif file_format == 'html':
        content = re_format_text(convert_html_to_string(file))
    elif file_format == 'unsupported':
        raise
    else:
        print 'not a file'
        raise
    return content



def generate_file_for_comparision(file, config_file=None):
    import os
    print 'got config file %s ' % config_file
    file_format = judge_file_format(file)
    #print file_format
    if file_format == 'txt':
        if not config_file:
            content = re_format_text(convert_txt_to_string(file))
        else:
            content = re_structure_text(file,config_file )
        write_string_to_file(content ,'COMPARE_txt_file_%s.txt' % os.path.basename(file))
        return 'COMPARE_txt_file_%s.txt' % os.path.basename(file)
    elif file_format == 'pdf':
        if not config_file:
            print 'no config file found'
            content = re_format_text(convert_pdf_to_string(file))
        else:
            content = re_structure_text(file,config_file )
        write_string_to_file(content,'COMPARE_pdf_file_%s.txt' %  os.path.basename(file))
        return 'COMPARE_pdf_file_%s.txt' % os.path.basename(file)
    elif file_format == 'xml':
        if not config_file:
            content = re_format_text(convert_xml_to_string(file))
        else:
            content = re_structure_text(file,config_file )
        write_string_to_file(content,'COMPARE_xml_file_%s.txt' % os.path.basename(file))
        return 'COMPARE_xml_file_%s.txt' % os.path.basename(file)
    elif file_format == 'html':
        if not config_file:
            content = re_format_text(convert_html_to_string(file))
        else:
            content = re_structure_text(file,config_file )
        write_string_to_file(content,'COMPARE_html_file_%s.txt' % os.path.basename(file))
        return 'COMPARE_html_file_%s.txt' % os.path.basename(file)
    elif file_format == 'unsupported':
        print 'unsupported file format'
        raise
    else:
        print 'not a file'


def generate_comparasion_report(fromfile, tofile):
    import sys
    import difflib
    lines = 5
    print 'got from file %r, to file %r' % (fromfile, tofile)
    fromlines = open(fromfile, 'U').readlines()
    tolines = open(tofile, 'U').readlines()
    diff = difflib.HtmlDiff().make_file(fromlines, tolines, fromfile,
                                        tofile, numlines = lines)
    sys.stdout.writelines(diff)





#TODO TEST
def perform_comparision(file1, file2, config_file=None):
    file1 = generate_file_for_comparision(file1, config_file)
    file2 = generate_file_for_comparision(file2, config_file)
    generate_comparasion_report(file1, file2)


if __name__ == '__main__':
    import sys, os
    if len(sys.argv) < 3:
        sys.exit(1)
    else:
        file1 = os.path.abspath(sys.argv[1])
        file2 = os.path.abspath(sys.argv[2])
        try:
            config_file = os.path.abspath(sys.argv[3])
        except:
            config_file = None
            #print 'no config file found'
        print sys.argv
        #print config_file
        perform_comparision(file1, file2, config_file=config_file )






"""
for manual comparasion and check

txt_s = re_format_text(convert_txt_to_string('background.txt'))
txt_t = re_format_text(convert_txt_to_string('background2.txt'))
pdf_s=re_format_text(convert_pdf_to_string('background.pdf'))
html_s=re_format_text(convert_html_to_string('S1-Source.html'))
html_t=re_format_text(convert_html_to_string('S1-Target.html'))
xml_t=re_format_text(convert_xml_to_string('S1-Target.xml'))
write_string_to_file(txt_s,'txt_s.txt')
write_string_to_file(txt_t,'txt_t.txt')
write_string_to_file(pdf_s,'pdf_s.txt')
write_string_to_file(html_s,'html_s.txt')
write_string_to_file(html_t,'html_t.txt')
write_string_to_file(xml_t,'xml_t.txt')


python diff.py txt_s.txt txt_t.txt -m > res_txt_txt_6.html
python diff.py txt_s.txt pdf_s.txt -m > res_txt_pdf_5.html
python diff.py pdf_s.txt html_t.txt -m > res_pdf_html_1.html
python diff.py pdf_s.txt xml_t.txt -m > res_pdf_xml_2.html
python diff.py html_s.txt xml_t.txt -m > res_html_xml_3.html
python diff.py html_s.txt html_t.txt -m > res_html_html_4.html


pdf_s=find_between(re_format_text(convert_pdf_to_string('S6-Source.pdf')),'DECREE')
html_s=find_between(re_format_text(convert_html_to_string('S6-Source.html')),'DECREE')
html_t=find_between(re_format_text(convert_html_to_string('S6-Target.html')),'DECREE')
xml_t=find_between(re_format_text(convert_xml_to_string('S6-Target.xml')),'DECREE')
write_string_to_file(pdf_s,'pdf_s.txt')
write_string_to_file(html_s,'html_s.txt')
write_string_to_file(html_t,'html_t.txt')
write_string_to_file(xml_t,'xml_t.txt')
"""

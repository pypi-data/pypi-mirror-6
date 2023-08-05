
import unittest
import os
import pymd

test_dir = os.path.abspath(os.path.dirname(__file__))

test_dir_input  = os.path.join(test_dir,'files_input')
test_dir_output  = os.path.join(test_dir,'files_output')

test_file_n1 = """File 1, h1
===========

Some text

File 1, h2
-----------

  * Some
  * nice
  * list

### File 1, h3

blablabla

File 1, back to h2
------------------

Dummy text"""

test_file_n2 = """File 2, h1
===========

Some text

File 2, h2
-----------

  * Some
  * nice
  * list

### File 2, h3

blablabla

File 2, back to h2
------------------

Dummy text"""

test_file_n3 = """File 3, h1
===========

Some text

File 3, h2
-----------

  * Some
  * nice
  * list

### File 3, h3

blablabla

File 3, back to h2
------------------

Dummy text"""

test_file_header = """Title: Testing projects
Comments: Hoping everything is ok

Let's show the toc

[TOC_HERE]

Now the content:
"""

test_file_index_custom = """Title: The index with wiki links too

  * [](file|file1.txt) 
  * [](file|file2.txt) 
  * [](file|file3.txt) 
  * [](file|INPUTPATH/file1.txt) 
  * [](file|INPUTPATH/file2.txt) 
  * [](file|INPUTPATH/file3.txt) 
  * [Custom title to file 1](file|file1.txt) 
  * [Custom title to file 2](file|file2.txt) 
  * [Custom title to file 3](file|file3.txt) 
  * [](file|notexistent.txt) 
  * [Custom title to not existent](file|notexistent.txt) 
  * [](file|notexistent2.html)
  * [Custom title to not existent html](file|notexistent2.html)
"""

test_file_index_custom = test_file_index_custom.replace("INPUTPATH/", os.path.join(test_dir_input,""))


class TestFileProperties(unittest.TestCase):
    """ file properties, special files (header, index - wiki) """
    
    def setUp(self):
        pymd.CONFIG['output'] = ""
        self.file_n1 = pymd.Parsing("")
        self.file_n1.mdParse(test_file_n1)

    def test_file_properties(self):
        """ Test file properties & one file convertion (no output) """

        self.assertEqual(self.file_n1.title, 'File 1, h1')
        self.assertEqual(self.file_n1.meta, '')
        self.assertEqual(self.file_n1.toc, u'<div class="toc">\n<ul>\n<li><a href="#file-1-h1">File 1, h1</a><ul>\n<li><a href="#file-1-h2">File 1, h2</a><ul>\n<li><a href="#file-1-h3">File 1, h3</a></li>\n</ul>\n</li>\n<li><a href="#file-1-back-to-h2">File 1, back to h2</a></li>\n</ul>\n</li>\n</ul>\n</div>\n')
        self.assertEqual(self.file_n1.html, u'<h1 id="file-1-h1">File 1, h1</h1>\n<p>Some text</p>\n<h2 id="file-1-h2">File 1, h2</h2>\n<ul>\n<li>Some</li>\n<li>nice</li>\n<li>list</li>\n</ul>\n<h3 id="file-1-h3">File 1, h3</h3>\n<p>blablabla</p>\n<h2 id="file-1-back-to-h2">File 1, back to h2</h2>\n<p>Dummy text</p>')
        self.assertEqual(self.file_n1.meta, '')

    def test_header(self):
        """Header file convertion and properties"""

        self.header = pymd.Parsing("")
        self.header.mdParse(test_file_header)

        self.assertEqual(self.header.title, 'Testing projects')
        self.assertEqual(self.header.meta, '<h1 class="title">Testing projects</h1>\n<dl>\n\t<dt>comments</dt>\n\t<dd>Hoping everything is ok</dd>\n</dl>\n')
        self.assertEqual(self.header.html, "<p>Let's show the toc</p>\n<p>[TOC_HERE]</p>\n<p>Now the content:</p>")

    def test_index_custom_wiki(self):
        """ Book index (custom) with wiki """

        self.maxDiff = None

        self.index = pymd.Parsing("")
        parsed = pymd.wikiLinks(test_file_index_custom.split("\n"))
        parsed = '\n'.join(n for n in parsed)

        self.index.mdParse(parsed)

        #if files existed
        #self.assertEqual(self.index.html, u'<ul>\n<li><a href="file1.html">file1.html</a> </li>\n<li><a href="file2.html">file2.html</a> </li>\n<li><a href="file3.html">file3.html</a> </li>\n<li><a href="file1.html">File 1, h1</a> </li>\n<li><a href="file2.html">File 2, h1</a> </li>\n<li><a href="file3.html">File 3, h1</a> </li>\n<li><a href="file1.txt">Custom title to file 1</a> </li>\n<li><a href="file2.txt">Custom title to file 2</a> </li>\n<li><a href="file3.txt">Custom title to file 3</a> </li>\n<li><a href="notexistent.html">notexistent.html</a> </li>\n<li><a href="notexistent.txt">Custom title to not existent</a> </li>\n<li><a href="notexistent2.html">notexistent2.html</a></li>\n<li><a href="notexistent2.html">Custom title to not existent html</a></li>\n</ul>')
        # But as doing in memory:
        self.assertEqual(self.index.html, u'<ul>\n<li><a href="file1.html">file1.html</a> </li>\n<li><a href="file2.html">file2.html</a> </li>\n<li><a href="file3.html">file3.html</a> </li>\n<li><a href="file1.html">file1.html</a> </li>\n<li><a href="file2.html">file2.html</a> </li>\n<li><a href="file3.html">file3.html</a> </li>\n<li><a href="file1.html">Custom title to file 1</a> </li>\n<li><a href="file2.html">Custom title to file 2</a> </li>\n<li><a href="file3.html">Custom title to file 3</a> </li>\n<li><a href="notexistent.html">notexistent.html</a> </li>\n<li><a href="notexistent.html">Custom title to not existent</a> </li>\n<li><a href="notexistent2.html">notexistent2.html</a></li>\n<li><a href="notexistent2.html">Custom title to not existent html</a></li>\n</ul>')



class TestConvertionsFile(unittest.TestCase):
    """ Convert file & output folder"""

    def setUp(self):
        pymd.CONFIG['flat'] = False

        self.file_n1 = pymd.Parsing("")
        self.file_n1.mdParse(test_file_n1)

    def test_file_output(self):
        """ One file output path """

        input_path  = os.path.join(test_dir_input,'file1.txt')
        output_path = os.path.join(test_dir_output,'file1.html')

        pymd.CONFIG['source'] = input_path
        pymd.CONFIG['output'] = test_dir_output

        self.file_n1.outputPath = pymd.path_output(input_path)

        self.assertEqual(self.file_n1.outputPath, output_path)


class TestConvertionsFiles(unittest.TestCase):
    """ Files like in folder or in .list """

    def setUp(self):
        pymd.CONFIG['flat'] = False
        pymd.CONFIG['source']   = test_dir_input
        pymd.CONFIG['output'] = test_dir_output

        self.thefiles = list()
        for i in range(1,4):
            x = pymd.Parsing("")

            # quick and dirty
            if i == 1: x.mdParse(test_file_n1)
            if i == 2: x.mdParse(test_file_n2)
            if i == 3: x.mdParse(test_file_n3)

            x.outputPath = pymd.path_output(os.path.join(test_dir_input,'file' + str(i) + '.txt'))

            self.thefiles.append(x)

    def test_merge(self):
        """ Test merging and lastDir"""

        lastDir = pymd.path_lastDir(pymd.path_get(self.thefiles[1].outputPath)) + ".html"

        projectWhole = ""

        for i in range(len(self.thefiles)):
            projectWhole += '\r\n <article>' + self.thefiles[i].meta + self.thefiles[i].html + "</article>\n\r"

        self.assertEqual(projectWhole, u'\r\n <article><h1 id="file-1-h1">File 1, h1</h1>\n<p>Some text</p>\n<h2 id="file-1-h2">File 1, h2</h2>\n<ul>\n<li>Some</li>\n<li>nice</li>\n<li>list</li>\n</ul>\n<h3 id="file-1-h3">File 1, h3</h3>\n<p>blablabla</p>\n<h2 id="file-1-back-to-h2">File 1, back to h2</h2>\n<p>Dummy text</p></article>\n\r\r\n <article><h1 id="file-2-h1">File 2, h1</h1>\n<p>Some text</p>\n<h2 id="file-2-h2">File 2, h2</h2>\n<ul>\n<li>Some</li>\n<li>nice</li>\n<li>list</li>\n</ul>\n<h3 id="file-2-h3">File 2, h3</h3>\n<p>blablabla</p>\n<h2 id="file-2-back-to-h2">File 2, back to h2</h2>\n<p>Dummy text</p></article>\n\r\r\n <article><h1 id="file-3-h1">File 3, h1</h1>\n<p>Some text</p>\n<h2 id="file-3-h2">File 3, h2</h2>\n<ul>\n<li>Some</li>\n<li>nice</li>\n<li>list</li>\n</ul>\n<h3 id="file-3-h3">File 3, h3</h3>\n<p>blablabla</p>\n<h2 id="file-3-back-to-h2">File 3, back to h2</h2>\n<p>Dummy text</p></article>\n\r')

        self.assertEqual(lastDir, "files_output.html")
        
    def test_merge_toc_untouched(self):
        """ Untouched toc """

        projectTocs = ""

        for i in range(len(self.thefiles)):
            projectTocs  += self.thefiles[i].toc

       # toc before merge
        self.assertEqual(projectTocs, u'<div class="toc">\n<ul>\n<li><a href="#file-1-h1">File 1, h1</a><ul>\n<li><a href="#file-1-h2">File 1, h2</a><ul>\n<li><a href="#file-1-h3">File 1, h3</a></li>\n</ul>\n</li>\n<li><a href="#file-1-back-to-h2">File 1, back to h2</a></li>\n</ul>\n</li>\n</ul>\n</div>\n<div class="toc">\n<ul>\n<li><a href="#file-2-h1">File 2, h1</a><ul>\n<li><a href="#file-2-h2">File 2, h2</a><ul>\n<li><a href="#file-2-h3">File 2, h3</a></li>\n</ul>\n</li>\n<li><a href="#file-2-back-to-h2">File 2, back to h2</a></li>\n</ul>\n</li>\n</ul>\n</div>\n<div class="toc">\n<ul>\n<li><a href="#file-3-h1">File 3, h1</a><ul>\n<li><a href="#file-3-h2">File 3, h2</a><ul>\n<li><a href="#file-3-h3">File 3, h3</a></li>\n</ul>\n</li>\n<li><a href="#file-3-back-to-h2">File 3, back to h2</a></li>\n</ul>\n</li>\n</ul>\n</div>\n')       
        
        # after merge
        tocmerged = pymd.tocMerge(projectTocs)
        self.assertEqual(tocmerged, u'<div class="toc"><ul><li><a href="#file-1-h1">File 1, h1</a><ul><li><a href="#file-1-h2">File 1, h2</a><ul></ul></li><li><a href="#file-1-back-to-h2">File 1, back to h2</a></li></ul></li><li><a href="#file-2-h1">File 2, h1</a><ul><li><a href="#file-2-h2">File 2, h2</a><ul></ul></li><li><a href="#file-2-back-to-h2">File 2, back to h2</a></li></ul></li><li><a href="#file-3-h1">File 3, h1</a><ul><li><a href="#file-3-h2">File 3, h2</a><ul></ul></li><li><a href="#file-3-back-to-h2">File 3, back to h2</a></li></ul></li></ul></div>')


    def test_merge_toc_filtered(self):
        """ Toc filtered to show upto 2nd level """

        pymd.CONFIG['toc'] = 2
        projectTocs = ""

        for i in range(len(self.thefiles)):
            projectTocs  += self.thefiles[i].toc

        tocmerged = pymd.tocMerge(projectTocs)
        self.assertEqual(tocmerged, u'<div class="toc"><ul><li><a href="#file-1-h1">File 1, h1</a><ul><li><a href="#file-1-h2">File 1, h2</a><ul></ul></li><li><a href="#file-1-back-to-h2">File 1, back to h2</a></li></ul></li><li><a href="#file-2-h1">File 2, h1</a><ul><li><a href="#file-2-h2">File 2, h2</a><ul></ul></li><li><a href="#file-2-back-to-h2">File 2, back to h2</a></li></ul></li><li><a href="#file-3-h1">File 3, h1</a><ul><li><a href="#file-3-h2">File 3, h2</a><ul></ul></li><li><a href="#file-3-back-to-h2">File 3, back to h2</a></li></ul></li></ul></div>')

    def test_book_index_default(self):
        """ Book index default (path_relative) """

        bookIndex  = "<ul>"

        for i in range(len(self.thefiles)):
            current_relative = pymd.path_relative_to(self.thefiles[i].outputPath, None, True)
            bookIndex += '<li><a href="' + current_relative + '">' + self.thefiles[i].title + '</a></li>'

        index = pymd.Parsing("")
        index.html = bookIndex + "</ul>"

        #for some reason, test parses \\ when original doesnt
        index.html = index.html.replace("\\", "")

        self.assertEqual(index.html, '<ul><li><a href="file1.html">File 1, h1</a></li><li><a href="file2.html">File 2, h1</a></li><li><a href="file3.html">File 3, h1</a></li></ul>')

    def test_book_nav_default(self):
        """ Book with normal nav """

        navigations = book_nav(self.thefiles)

        self.assertEqual(navigations[0], '<div class="nav"> <a href="index.html">index</a> <a href="file2.html">next &gt;</a></div>')
        self.assertEqual(navigations[1], '<div class="nav"><a href="file1.html">&lt; prev</a> <a href="index.html">index</a> <a href="file3.html">next &gt;</a></div>')
        self.assertEqual(navigations[2], '<div class="nav"><a href="file2.html">&lt; prev</a> <a href="index.html">index</a> </div>')

    def test_book_nav_titles(self):
        """ Book with titles nav """

        navigations = book_nav(self.thefiles, True)

        self.assertEqual(navigations[0], '<div class="nav"> <a href="index.html">index</a> <a href="file2.html">File 2, h1 &gt;</a></div>')
        self.assertEqual(navigations[1], '<div class="nav"><a href="file1.html">&lt; File 1, h1</a> <a href="index.html">index</a> <a href="file3.html">File 3, h1 &gt;</a></div>')
        self.assertEqual(navigations[2], '<div class="nav"><a href="file2.html">&lt; File 2, h1</a> <a href="index.html">index</a> </div>')

def book_nav(thefiles, nav=False):
    """ Creates the navigation. Returns a list of navigations """

    pymd.CONFIG['nav'] = nav

    data_prev = ""
    navigations = list()

    for i in range(len(thefiles)):
        if i == 0:
            data_prev = pymd.Parsing("")

        data_current = thefiles[i]
        
        if i+1 < len(thefiles):
            data_next = thefiles[i+1]
        else:
            data_next = pymd.Parsing("")

        navigation = pymd.html_bookNavigation(data_current.outputPath, data_prev.outputPath, 
                                        data_prev.title, data_next.outputPath, data_next.title)

        data_prev    = data_current
        data_current = data_next
        data_next    = pymd.Parsing("")

        #for some reason, test parses \\ when original doesnt
        navigation = navigation.replace("\\", "")

        navigations.append(navigation)

    return navigations


if __name__ == '__main__':
    unittest.main(verbosity=2) #so no command line -v

import codecs
import os
import re
import subprocess
import traceback

from util import makedirs


class BookBinder(object):
    def __init__(self, url, nr_range, name, res_dir=None, raw_dir="raw", output_dir="out", chunk_size=100):
        self.url = url
        self.nr_range = nr_range
        self.name = name
        self.raw_dir = os.path.abspath(raw_dir)
        self.output_dir = os.path.abspath(output_dir)
        self.chunk_size = chunk_size
        self.res_dir = os.path.abspath(res_dir) if res_dir else None

        self.pages_dir = os.path.join(raw_dir, os.path.dirname(re.sub("^.*://", "", url)))
        self.page_name = os.path.basename(url)
        self.extracted_dir = os.path.join(output_dir, "extracted")
        self.ebook_dir = os.path.abspath(os.path.join(output_dir, "ebooks"))

    def fetch_raw_pages(self):
        print "-- fetching raw pages from %s" % self.url
        makedirs(self.pages_dir)
        for nr in self.nr_range:
            if os.path.exists("%s/%s%s" % (self.pages_dir, self.page_name, str(nr))):
                print("---- nr %i cached\r" % nr)
                continue
            print "---- fetching comic nr %i" % nr
            print "------ %s%s" % (self.url, nr)
            return_code = subprocess.call(
                ["/usr/bin/wget", "-q", "-k", "-p", "-r", "-P", self.raw_dir, "--follow-tags=img", "%s%s" % (self.url, nr)]
            )
            if return_code:
                print "------ wget returns with exit code %i, assuming last comic" % return_code
                break

    def render_md_snippets(self, parse_fun):
        print "-- rendering markdown snippets"
        makedirs(self.extracted_dir)

        for filename in sorted(os.listdir(self.pages_dir)):
            if not filename.startswith(self.page_name):
                continue
            nr = int(re.sub(".*=", "", filename))
            out_file = os.path.join(self.extracted_dir, "%04i.md" % nr)
            if os.path.exists(out_file):
                print "---- snippet %i cached" % nr
                continue
            print "---- processing comic %s: %s -> %s" % (nr, filename, out_file)
            try:
                with codecs.open(out_file, 'w', 'utf-8') as output:
                    parse_fun(self.pages_dir, filename, nr, self.extracted_dir, output)
            except Exception, e:
                traceback.print_exc()
                print "------ problem encountered while parsing: %s" % str(e)
                print "------ removing generated file %s" % out_file
                os.unlink(out_file)

    def combine_md_snippets(self):
        print "-- combining markdown snippets to chunks of %s comics" % self.chunk_size
        nrs = []
        for md in os.listdir(self.extracted_dir):
            if not os.path.isfile(os.path.join(self.extracted_dir, md)):
                continue
            name, ext = os.path.splitext(md)
            if not name.isdigit():
                #print "---- skipping %s" % md
                continue
            nr = int(name)
            nrs.append(nr)
        nrs.sort()

        current = None
        for nr in nrs:
            last_nr = self.chunk_size * int((nr + self.chunk_size - 1) / self.chunk_size)
            if not current:
                current_name = "%s.%04i.md" % (self.name, last_nr)
                print "---- combining to %s" % current_name
                current = open(os.path.join(self.extracted_dir, current_name), "w")
            snippet_name = os.path.join(self.extracted_dir, "%04i.md" % nr)
            with open(snippet_name) as snippet_file:
                for line in snippet_file:
                    current.write(line)
            if nr % self.chunk_size == 0:
                current.close()
                current = None

    def render_ebook(self, polish_fun=None):
        print "-- generating ebooks"
        makedirs(self.ebook_dir)

        this_dir = os.getcwd()
        os.chdir(self.extracted_dir)
#        for t in range(0, 99):
#            first_nr = 100 * t + 1
#            last_nr = 100 * (t + 1)
#            md_name = "%s.%04i.md" % (self.name, last_nr)
#            if not os.path.exists(md_name):
#                break
        import glob
        for md_name in sorted(glob.glob("%s.*.md" % self.name)):
            last_nr = int(re.sub("%s." % self.name, "", os.path.splitext(md_name)[0]))
            first_nr = last_nr - self.chunk_size + 1
            print "---- processing markdown %s" % md_name
            epub_name = os.path.join(self.ebook_dir, "%s.%04i.epub" % (self.name, last_nr))
            makedirs(os.path.dirname(epub_name))
            cmd = ["pandoc", "-S", md_name,  "-o", epub_name, "--smart"]
            if self.res_dir:
                cmd.append("--epub-stylesheet=%s/epub.css" % self.res_dir)
            if polish_fun:
                context = locals()
                context.update(vars(self))
                cmd = polish_fun(context)
            print "------ rendering %s" % epub_name
            subprocess.check_call(cmd)
        os.chdir(this_dir)

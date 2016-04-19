def pdf_to_csv(filename):
    from cStringIO import StringIO
    from pdfminer.converter import LTChar, TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfparser import PDFDocument, PDFParser
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

    class CsvConverter(TextConverter):
        def __init__(self, *args, **kwargs):
            TextConverter.__init__(self, *args, **kwargs)

        def end_page(self, i):
            from collections import defaultdict
            lines = defaultdict(lambda : {})
            for child in self.cur_item._objs:                #<-- changed
                if isinstance(child, LTChar):
                    (_,_,x,y) = child.bbox
                    line = lines[int(-y)]
                    line[x] = child._text.encode(self.codec) #<-- changed

            for y in sorted(lines.keys()):
                line = lines[y]
                self.outfp.write(";".join(line[x] for x in sorted(line.keys())))
                self.outfp.write("\n")

    # ... the following part of the code is a remix of the
    # convert() function in the pdfminer/tools/pdf2text module
    rsrc = PDFResourceManager()
    outfp = StringIO()
    device = CsvConverter(rsrc, outfp, codec="utf-8", laparams=LAParams())
        # becuase my test documents are utf-8 (note: utf-8 is the default codec)

    doc = PDFDocument()
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')

    interpreter = PDFPageInterpreter(rsrc, device)

    for i, page in enumerate(doc.get_pages()):
        outfp.write("START PAGE %d\n" % i)
        if page is not None:
            interpreter.process_page(page)
        outfp.write("END PAGE %d\n" % i)

    device.close()
    fp.close()

    return outfp.getvalue()

import csv
import pdfrw

IN_FILE = "awards.csv"
TEMPLATE_FILE = "template.pdf"
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'
FIELDS = ["Certificate Category", "Certificate Rank"]
N = 1


# Updates single instance of template pdf, increment form field suffix
def modify_form(input_pdf_path, data_dict):
    global N
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    annotations = template_pdf.pages[0][ANNOT_KEY]
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                if key in data_dict.keys():
                    annotation.update(
                        pdfrw.PdfDict(T="{}".format(key + str(N)))
                    )
                    annotation.update(
                        pdfrw.PdfDict(V="{}".format(data_dict[key]))
                    )
                    annotation.update(pdfrw.PdfDict(Ff=1))
    N += 1
    return template_pdf


def build_datadict(in_file):
    o = []
    with open(in_file) as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            m = {}
            for f in FIELDS:
                if row[f] and not row[f].isspace() and not row[f] is None:
                    m[f] = row[f]
            if m:
                m['Date'] = "January 25th, 2020"
                o.append(m)
    return o


if __name__ == '__main__':
    data = build_datadict(IN_FILE)
    writer = pdfrw.PdfWriter()
    writer.trailer.Info = pdfrw.IndirectPdfDict(
        Title='Combined PDF'
    )
    # Iterate array of 'data_dict's
    for d in data:
        this_pages = modify_form(TEMPLATE_FILE, d)  # fill the form
        this_pages.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))  # maintain appearances
        writer.addpages(this_pages.pages)  # merge into single pdf
    writer.write(IN_FILE.split(".")[0] + ".pdf")

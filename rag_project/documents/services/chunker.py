from pypdf import PdfReader



class PDFProcessor:


    def extract_text(self,file_path):

        reader = PdfReader(file_path)


        text=""


        for page in reader.pages:

            text += page.extract_text()


        return text

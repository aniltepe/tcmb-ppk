from PyPDF2 import PdfReader

reader = PdfReader("ppk/özet/2024/DUY2024-03.pdf")
number_of_pages = len(reader.pages)
text = ""
for i in range(number_of_pages):
    page = reader.pages[i]
    text += page.extract_text()

print(text)
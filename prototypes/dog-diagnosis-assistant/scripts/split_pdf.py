import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf_by_pages(file_path, pages_per_chunk=20):
    file_base, file_ext = os.path.splitext(file_path)
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)

    for i in range(0, total_pages, pages_per_chunk):
        writer = PdfWriter()
        chunk_file_path = f"{file_base}_part{i // pages_per_chunk + 1}{file_ext}"
        
        for j in range(i, min(i + pages_per_chunk, total_pages)):
            writer.add_page(reader.pages[j])
        
        with open(chunk_file_path, 'wb') as output_pdf:
            writer.write(output_pdf)
        
        yield chunk_file_path

# Example usage
file_path = "./知识库/8.pdf"
pages_per_chunk = 20  # Split by 1 page per chunk
for part_file in split_pdf_by_pages(file_path, pages_per_chunk):
    print(f"Created part file: {part_file}")

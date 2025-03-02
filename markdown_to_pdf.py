#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert Markdown to PDF using fpdf and markdown.
"""

import os
import re
import markdown
from fpdf import FPDF

class MarkdownToPDF:
    """Class to convert Markdown to PDF."""
    
    def __init__(self, input_file, output_file):
        """Initialize with input and output files."""
        self.input_file = input_file
        self.output_file = output_file
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)
        
        # Set up fonts
        self.pdf.add_font('DejaVu', '', 'C:\\Windows\\Fonts\\arial.ttf', uni=True)
        self.pdf.add_font('DejaVuBold', '', 'C:\\Windows\\Fonts\\arialbd.ttf', uni=True)
        self.pdf.add_font('DejaVuItalic', '', 'C:\\Windows\\Fonts\\ariali.ttf', uni=True)
        
        # Set default font
        self.pdf.set_font('DejaVu', '', 12)
    
    def convert(self):
        """Convert Markdown to PDF."""
        print(f"Converting {self.input_file} to {self.output_file}...")
        
        try:
            # Read Markdown content
            with open(self.input_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert Markdown to HTML
            html_content = markdown.markdown(
                md_content,
                extensions=['extra', 'toc', 'tables', 'fenced_code']
            )
            
            # Process HTML content
            self._process_html(html_content)
            
            # Save PDF
            self.pdf.output(self.output_file)
            
            if os.path.exists(self.output_file):
                print(f"Successfully created PDF: {self.output_file}")
                
                # Try to open the PDF
                try:
                    os.startfile(self.output_file)
                    print(f"Opened {self.output_file}")
                except Exception as e:
                    print(f"Failed to open PDF: {e}")
            else:
                print(f"Failed to create PDF: {self.output_file}")
        
        except Exception as e:
            print(f"Error converting Markdown to PDF: {e}")
    
    def _process_html(self, html_content):
        """Process HTML content and add to PDF."""
        # Extract and process headings
        headings = re.findall(r'<h(\d)>(.*?)</h\1>', html_content)
        for level, text in headings:
            level = int(level)
            self._add_heading(text, level)
        
        # Extract and process paragraphs
        paragraphs = re.findall(r'<p>(.*?)</p>', html_content, re.DOTALL)
        for p in paragraphs:
            self._add_paragraph(p)
        
        # Extract and process lists
        lists = re.findall(r'<ul>(.*?)</ul>', html_content, re.DOTALL)
        for ul in lists:
            items = re.findall(r'<li>(.*?)</li>', ul, re.DOTALL)
            for item in items:
                self._add_list_item(item)
        
        # Extract and process code blocks
        code_blocks = re.findall(r'<pre><code>(.*?)</code></pre>', html_content, re.DOTALL)
        for code in code_blocks:
            self._add_code_block(code)
    
    def _add_heading(self, text, level):
        """Add a heading to the PDF."""
        # Clean text
        text = self._clean_text(text)
        
        # Set font size based on heading level
        sizes = {1: 24, 2: 20, 3: 16, 4: 14, 5: 12, 6: 12}
        size = sizes.get(level, 12)
        
        # Add some space before heading
        self.pdf.ln(10)
        
        # Add heading
        self.pdf.set_font('DejaVuBold', '', size)
        self.pdf.cell(0, 10, text, ln=True)
        
        # Reset font
        self.pdf.set_font('DejaVu', '', 12)
        
        # Add some space after heading
        self.pdf.ln(5)
    
    def _add_paragraph(self, text):
        """Add a paragraph to the PDF."""
        # Clean text
        text = self._clean_text(text)
        
        # Add paragraph
        self.pdf.set_font('DejaVu', '', 12)
        self.pdf.multi_cell(0, 10, text)
        
        # Add some space after paragraph
        self.pdf.ln(5)
    
    def _add_list_item(self, text):
        """Add a list item to the PDF."""
        # Clean text
        text = self._clean_text(text)
        
        # Add list item
        self.pdf.set_font('DejaVu', '', 12)
        self.pdf.cell(10, 10, '•', ln=0)
        self.pdf.multi_cell(0, 10, text)
    
    def _add_code_block(self, text):
        """Add a code block to the PDF."""
        # Clean text
        text = self._clean_text(text)
        
        # Add code block
        self.pdf.set_font('Courier', '', 10)
        self.pdf.multi_cell(0, 10, text)
        
        # Reset font
        self.pdf.set_font('DejaVu', '', 12)
        
        # Add some space after code block
        self.pdf.ln(5)
    
    def _clean_text(self, text):
        """Clean HTML text."""
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Replace HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        
        return text

def main():
    """Main function."""
    input_file = "dokumentasjon.md"
    output_file = "MedicalTextExtractor_Dokumentasjon.pdf"
    
    converter = MarkdownToPDF(input_file, output_file)
    converter.convert()

if __name__ == "__main__":
    main()

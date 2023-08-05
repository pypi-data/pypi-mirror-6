README for collective.pdfexport
==========================================

A simple product which provides a XHTML2PDF Exporter.

Enabling
----------

Implement collective.pdfexport.interfaces.IPDFExportCapable on the content
type and create xhtml2pdf_view for it. Loading download_pdf view on the content
will export xhtml2pdf_view as PDF.

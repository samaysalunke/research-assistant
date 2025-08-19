"""
PDF Processing Service
Handles PDF upload, text extraction, and processing
"""

import io
import tempfile
import os
from typing import Optional, Dict, Any
from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Service for processing PDF documents"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    async def process_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process a PDF file and extract text content
        
        Args:
            file_content: Raw PDF file bytes
            filename: Original filename
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            # Validate file extension
            if not any(filename.lower().endswith(ext) for ext in self.supported_extensions):
                raise ValueError(f"Unsupported file type. Supported: {self.supported_extensions}")
            
            # Create a temporary file to process
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text from PDF
                extracted_text = await self._extract_text_from_pdf(temp_file_path)
                
                # Extract metadata
                metadata = await self._extract_metadata(temp_file_path, filename)
                
                return {
                    'success': True,
                    'text': extracted_text,
                    'metadata': metadata,
                    'filename': filename,
                    'content_type': 'pdf'
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text content from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                text_content = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                        continue
                
                return '\n\n'.join(text_content)
                
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    async def _extract_metadata(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF file
        
        Args:
            file_path: Path to PDF file
            filename: Original filename
            
        Returns:
            PDF metadata
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                metadata = {
                    'filename': filename,
                    'page_count': len(pdf_reader.pages),
                    'file_size_bytes': os.path.getsize(file_path),
                    'pdf_version': pdf_reader.metadata.get('/PDFVersion', 'Unknown') if pdf_reader.metadata else 'Unknown'
                }
                
                # Extract document info if available
                if pdf_reader.metadata:
                    info = pdf_reader.metadata
                    metadata.update({
                        'title': info.get('/Title', ''),
                        'author': info.get('/Author', ''),
                        'subject': info.get('/Subject', ''),
                        'creator': info.get('/Creator', ''),
                        'producer': info.get('/Producer', ''),
                        'creation_date': info.get('/CreationDate', ''),
                        'modification_date': info.get('/ModDate', '')
                    })
                
                return metadata
                
        except Exception as e:
            logger.warning(f"Error extracting metadata from PDF: {str(e)}")
            return {
                'filename': filename,
                'page_count': 0,
                'file_size_bytes': 0,
                'error': str(e)
            }
    
    def validate_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate PDF file before processing
        
        Args:
            file_content: Raw PDF file bytes
            filename: Original filename
            
        Returns:
            Validation result
        """
        try:
            # Check file extension
            if not filename.lower().endswith('.pdf'):
                return {
                    'valid': False,
                    'error': 'File must be a PDF'
                }
            
            # Check file size (max 50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            if len(file_content) > max_size:
                return {
                    'valid': False,
                    'error': f'File size too large. Maximum allowed: 50MB'
                }
            
            # Try to read PDF header
            try:
                pdf_stream = io.BytesIO(file_content)
                pdf_reader = PdfReader(pdf_stream)
                
                if len(pdf_reader.pages) == 0:
                    return {
                        'valid': False,
                        'error': 'PDF appears to be empty or corrupted'
                    }
                
                return {
                    'valid': True,
                    'page_count': len(pdf_reader.pages),
                    'file_size': len(file_content)
                }
                
            except Exception as e:
                return {
                    'valid': False,
                    'error': f'Invalid PDF file: {str(e)}'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }

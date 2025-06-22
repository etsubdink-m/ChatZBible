"""
Document Processing Utilities
Handles conversion of raw data to LangChain documents
"""
from typing import List, Dict

from langchain_core.documents import Document


class DocumentProcessor:
    """Handles conversion of Bible data to LangChain documents"""
    
    @staticmethod
    def create_documents_from_bible_data(bible_data: List[Dict]) -> List[Document]:
        """
        Convert Bible data to LangChain Document objects
        
        Args:
            bible_data: List of bible verse dictionaries
            
        Returns:
            List of Document objects ready for indexing
        """
        documents = []
        
        for verse in bible_data:
            # Create individual verse document
            doc = Document(
                page_content=verse['text'],
                metadata={
                    'book': verse['book'],
                    'chapter': verse['chapter'],
                    'verse': verse['verse'],
                    'reference': f"{verse['book']} {verse['chapter']}:{verse['verse']}",
                    'translation': verse.get('translation', 'KJV'),
                    'testament': DocumentProcessor._get_testament(verse['book']),
                    'book_number': DocumentProcessor._get_book_number(verse['book']),
                    'chunk_type': 'verse'
                }
            )
            documents.append(doc)
        
        # Create passage-level documents for better context
        # passage_docs = DocumentProcessor._create_passage_documents(bible_data)
        documents.extend(documents)
        
        return documents
    
  
    @staticmethod
    def _get_testament(book: str) -> str:
        """Determine if book is Old or New Testament"""
        old_testament_books = {
            "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
            "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
            "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
            "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
            "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah",
            "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel",
            "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
            "Zephaniah", "Haggai", "Zechariah", "Malachi"
        }
        return "Old" if book in old_testament_books else "New"
    
    @staticmethod
    def _get_book_number(book: str) -> int:
        """Get biblical book number (1-66)"""
        book_numbers = {
            # Old Testament
            "Genesis": 1, "Exodus": 2, "Leviticus": 3, "Numbers": 4, "Deuteronomy": 5,
            "Joshua": 6, "Judges": 7, "Ruth": 8, "1 Samuel": 9, "2 Samuel": 10,
            "1 Kings": 11, "2 Kings": 12, "1 Chronicles": 13, "2 Chronicles": 14,
            "Ezra": 15, "Nehemiah": 16, "Esther": 17, "Job": 18, "Psalms": 19,
            "Proverbs": 20, "Ecclesiastes": 21, "Song of Solomon": 22, "Isaiah": 23,
            "Jeremiah": 24, "Lamentations": 25, "Ezekiel": 26, "Daniel": 27,
            "Hosea": 28, "Joel": 29, "Amos": 30, "Obadiah": 31, "Jonah": 32,
            "Micah": 33, "Nahum": 34, "Habakkuk": 35, "Zephaniah": 36,
            "Haggai": 37, "Zechariah": 38, "Malachi": 39,
            
            # New Testament
            "Matthew": 40, "Mark": 41, "Luke": 42, "John": 43, "Acts": 44,
            "Romans": 45, "1 Corinthians": 46, "2 Corinthians": 47, "Galatians": 48,
            "Ephesians": 49, "Philippians": 50, "Colossians": 51, "1 Thessalonians": 52,
            "2 Thessalonians": 53, "1 Timothy": 54, "2 Timothy": 55, "Titus": 56,
            "Philemon": 57, "Hebrews": 58, "James": 59, "1 Peter": 60, "2 Peter": 61,
            "1 John": 62, "2 John": 63, "3 John": 64, "Jude": 65, "Revelation": 66
        }
        return book_numbers.get(book, 0) 
"""
Bible Data Seeder
Handles loading, processing, and seeding biblical texts into the vector database
"""
import json
from typing import List, Dict, Optional
from pathlib import Path
import sys
# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import config

class BibleDataSeeder:
    """Handles loading and processing biblical data"""
    
    def __init__(self):
        self.data_path = Path(config.BIBLE_DATA_PATH)
    
    def create_sample_bible_data(self) -> Dict:
        """Create minimal sample Bible data as fallback only"""
        return {
            "translation": "KJV",
            "books": [
                {
                    "name": "Genesis",
                    "chapters": [
                        {
                            "chapter": 1,
                            "verses": [
                                {
                                    "verse": 1,
                                    "text": "In the beginning God created the heaven and the earth."
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    def load_kjv_data(self) -> List[Dict]:
        """
        Load the complete KJV Bible data from KJV.json
        
        Returns:
            List of verse dictionaries in flat format
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"KJV.json not found at {self.data_path}")
        
        print(f"Loading complete KJV Bible data from {self.data_path}...")
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            kjv_data = json.load(f)
        
        # Convert nested structure to flat list
        verses = []
        for book in kjv_data["books"]:
            book_name = book["name"]
            
            for chapter in book["chapters"]:
                chapter_num = chapter["chapter"]
                
                for verse in chapter["verses"]:
                    verse_num = verse["verse"]
                    verse_text = verse["text"]
                    
                    # Create verse dictionary in expected format
                    verse_dict = {
                        "book": book_name,
                        "chapter": chapter_num,
                        "verse": verse_num,
                        "text": verse_text,
                        "translation": "KJV"
                    }
                    verses.append(verse_dict)
        
        print(f"Successfully loaded {len(verses)} verses from complete KJV Bible")
        return verses

    def save_sample_data(self):
        """Save minimal sample data as fallback"""
        sample_data = self.create_sample_bible_data()
        
        # Ensure data directory exists
        self.data_path.parent.mkdir(exist_ok=True)
        
        # Save to a different file to avoid overwriting KJV.json
        sample_path = self.data_path.parent / "sample_bible.json"
        with open(sample_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved minimal sample data to {sample_path}")
        return sample_data
    
    def load_bible_data(self) -> List[Dict]:
        """
        Load complete KJV Bible data, with fallback to minimal sample
        
        Returns:
            List of verse dictionaries
        """
        try:
            # Always try to load complete KJV Bible first
            return self.load_kjv_data()
            
        except FileNotFoundError:
            print(f"⚠️  KJV.json not found at {self.data_path}")
            print("Creating minimal fallback data...")
            
            # Create and convert sample data
            sample_data = self.create_sample_bible_data()
            
            # Convert structure to flat format
            verses = []
            for book in sample_data["books"]:
                book_name = book["name"]
                
                for chapter in book["chapters"]:
                    chapter_num = chapter["chapter"]
                    
                    for verse in chapter["verses"]:
                        verse_num = verse["verse"]
                        verse_text = verse["text"]
                        
                        verse_dict = {
                            "book": book_name,
                            "chapter": chapter_num,
                            "verse": verse_num,
                            "text": verse_text,
                            "translation": "KJV"
                        }
                        verses.append(verse_dict)
            
            print(f"Using minimal fallback data: {len(verses)} verse(s)")
            print("💡 Please add KJV.json to data/ directory for complete Bible")
            return verses
    
    def get_bible_stats(self) -> Dict:
        """Get statistics about the KJV Bible data"""
        if not self.data_path.exists():
            return {"error": "KJV.json not found"}
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            kjv_data = json.load(f)
        
        stats = {
            "translation": kjv_data.get("translation", "Unknown"),
            "total_books": len(kjv_data["books"]),
            "total_chapters": 0,
            "total_verses": 0,
            "books": []
        }
        
        for book in kjv_data["books"]:
            book_chapters = len(book["chapters"])
            book_verses = sum(len(chapter["verses"]) for chapter in book["chapters"])
            
            stats["total_chapters"] += book_chapters
            stats["total_verses"] += book_verses
            stats["books"].append({
                "name": book["name"],
                "chapters": book_chapters,
                "verses": book_verses
            })
        
        return stats


if __name__ == "__main__":
    # Test the seeder
    seeder = BibleDataSeeder()
    
    print("=== Bible Data Seeder Test ===")
    
    # Show Bible stats if KJV.json exists
    stats = seeder.get_bible_stats()
    if "error" not in stats:
        print(f"Bible: {stats['translation']}")
        print(f"Books: {stats['total_books']}")
        print(f"Chapters: {stats['total_chapters']}")
        print(f"Verses: {stats['total_verses']}")
    
    # Test loading data
    data = seeder.load_bible_data()
    print(f"Successfully loaded {len(data)} verses")
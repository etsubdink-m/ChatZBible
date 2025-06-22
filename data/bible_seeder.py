"""
Bible Data Seeder
Handles loading, processing, and seeding biblical texts into the vector database
"""
import json
from typing import List, Dict
from pathlib import Path

# Note: We're avoiding langchain imports here to prevent circular dependencies
# The Document creation will be handled by the RAG engine

from config.settings import config


class BibleDataSeeder:
    """Handles loading and processing biblical data"""
    
    def __init__(self):
        self.data_path = Path(config.BIBLE_DATA_PATH)
    
    def create_sample_bible_data(self) -> List[Dict]:
        """Create sample Bible data for testing and initial setup"""
        return [
            # Genesis 1:1-5
            {
                "book": "Genesis",
                "chapter": 1,
                "verse": 1, 
                "text": "In the beginning God created the heaven and the earth.",
                "translation": "KJV"
            },
            {
                "book": "Genesis",
                "chapter": 1,
                "verse": 2,
                "text": "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.",
                "translation": "KJV"
            },
            {
                "book": "Genesis", 
                "chapter": 1,
                "verse": 3,
                "text": "And God said, Let there be light: and there was light.",
                "translation": "KJV"
            },
            
            # John 3:16-17
            {
                "book": "John",
                "chapter": 3,
                "verse": 16,
                "text": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                "translation": "KJV"
            },
            {
                "book": "John",
                "chapter": 3, 
                "verse": 17,
                "text": "For God sent not his Son into the world to condemn the world; but that the world through him might be saved.",
                "translation": "KJV"
            },
            
            # Psalm 23:1-3
            {
                "book": "Psalms",
                "chapter": 23,
                "verse": 1,
                "text": "The LORD is my shepherd; I shall not want.",
                "translation": "KJV"
            },
            {
                "book": "Psalms",
                "chapter": 23,
                "verse": 2,
                "text": "He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
                "translation": "KJV"
            },
            {
                "book": "Psalms",
                "chapter": 23,
                "verse": 3,
                "text": "He restoreth my soul: he leadeth me in the paths of righteousness for his name's sake.",
                "translation": "KJV"
            }
        ]
    
    def save_sample_data(self):
        """Save sample data to JSON file"""
        sample_data = self.create_sample_bible_data()
        
        # Ensure data directory exists
        self.data_path.parent.mkdir(exist_ok=True)
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(sample_data)} verses to {self.data_path}")
    
    def load_bible_data(self) -> List[Dict]:
        """Load Bible data from JSON file"""
        if not self.data_path.exists():
            print("Bible data file not found. Creating sample data...")
            self.save_sample_data()
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} verses from {self.data_path}")
        return data


if __name__ == "__main__":
    # Test the seeder
    seeder = BibleDataSeeder()
    data = seeder.load_bible_data()
    print(f"Loaded {len(data)} verses for processing") 
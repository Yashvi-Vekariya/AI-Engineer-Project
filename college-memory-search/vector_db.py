import chromadb
from chromadb.utils import embedding_functions
from config import COLLECTION_NAME, PERSIST_DIRECTORY

class VectorDatabase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
        # Use ChromaDB's default embedding function (no sentence-transformers needed!)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            return self.client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
        except:
            return self.client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"description": "College lecture memories"}
            )
    
    def add_lectures(self, lectures):
        """Add lectures to vector database"""
        documents = []
        metadatas = []
        ids = []
        
        for idx, lecture in enumerate(lectures):
            documents.append(lecture['content'])
            metadatas.append({
                'course': lecture['course'],
                'lecture_title': lecture['title'],
                'date': lecture.get('date', ''),
                'instructor': lecture.get('instructor', '')
            })
            ids.append(f"lecture_{idx}")
        
        # Add to collection (embeddings are generated automatically)
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(lectures)} lectures to the database")
    
    def search_similar(self, query, n_results=3):
        """Search for similar lectures"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        return results
    
    def get_collection_info(self):
        """Get count of documents in collection"""
        return self.collection.count()
    
    def clear_collection(self):
        """Clear all data from collection"""
        try:
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self._get_or_create_collection()
            print("✅ Collection cleared successfully")
        except Exception as e:
            print(f"❌ Error clearing collection: {e}")

# Singleton instance
vector_db = VectorDatabase()
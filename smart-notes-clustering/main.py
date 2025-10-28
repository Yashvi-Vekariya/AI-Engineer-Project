import json
import numpy as np
from embeddings import NoteEmbedder
from clustering import NoteClustering
from search import SemanticSearch
from visualization import Visualization
from config import client

def create_sample_notes():
    """Create sample notes for testing"""
    sample_notes = [
        {"id": 1, "content": "Machine learning is a subset of artificial intelligence"},
        {"id": 2, "content": "Deep learning uses neural networks with multiple layers"},
        {"id": 3, "content": "Python is a popular programming language for data science"},
        {"id": 4, "content": "JavaScript is used for web development and frontend"},
        {"id": 5, "content": "React is a JavaScript library for building user interfaces"},
        {"id": 6, "content": "Natural language processing helps computers understand text"},
        {"id": 7, "content": "Computer vision enables machines to interpret images"},
        {"id": 8, "content": "Data analysis involves cleaning and exploring datasets"},
        {"id": 9, "content": "Big data refers to extremely large datasets"},
        {"id": 10, "content": "Cloud computing provides remote servers and services"},
        {"id": 11, "content": "AWS and Azure are popular cloud platforms"},
        {"id": 12, "content": "Docker helps with containerization of applications"},
        {"id": 13, "content": "Kubernetes is used for container orchestration"},
        {"id": 14, "content": "Git is essential for version control in software development"},
        {"id": 15, "content": "Agile methodology focuses on iterative development"}
    ]
    
    with open('sample_notes.json', 'w') as f:
        json.dump(sample_notes, f, indent=2)
    
    return sample_notes

def main():
    print("=== Smart Notes Clustering ===")
    
    # Step 1: Create or load notes
    try:
        embedder = NoteEmbedder()
        notes_data = embedder.load_notes_from_file('sample_notes.json')
        print(f"Loaded {len(notes_data)} notes from file")
    except FileNotFoundError:
        print("Sample notes file not found. Creating sample notes...")
        notes_data = create_sample_notes()
        print(f"Created {len(notes_data)} sample notes")
    
    # Step 2: Prepare notes and generate embeddings
    texts, note_ids = embedder.prepare_notes(notes_data)
    print("Generating embeddings...")
    
    # Try Groq API first, fallback to local model
    try:
        embeddings = embedder.get_embeddings_groq(texts)
        print("Used Groq API for embeddings")
    except Exception as e:
        print(f"Groq API failed: {e}. Using local model...")
        embeddings = embedder.get_embeddings_local(texts)
        print("Used local model for embeddings")
    
    print(f"Embeddings shape: {embeddings.shape}")
    
    # Step 3: Cluster notes
    print("\nClustering notes...")
    clusterer = NoteClustering(method='kmeans', n_clusters=4)
    labels = clusterer.cluster_notes(embeddings)
    
    cluster_info = clusterer.get_cluster_info(embeddings)
    print(f"Created {clusterer.n_clusters} clusters")
    for cluster_id, info in cluster_info.items():
        print(f"Cluster {cluster_id}: {info['size']} notes")
    
    # Step 4: Initialize search
    searcher = SemanticSearch(embeddings, texts, note_ids)
    
    # Step 5: Visualize results
    viz = Visualization()
    print("\nReducing dimensions for visualization...")
    reduced_embeddings = viz.reduce_dimensions(embeddings, method='umap')
    
    # Matplotlib visualization
    print("Creating static visualization...")
    viz.plot_clusters_matplotlib(reduced_embeddings, labels, texts)
    
    # Plotly interactive visualization
    print("Creating interactive visualization...")
    viz.plot_clusters_plotly(reduced_embeddings, labels, texts, note_ids)
    
    # Cluster sizes
    viz.plot_cluster_sizes(cluster_info)
    
    # Step 6: Demonstrate semantic search
    print("\n=== Semantic Search Demo ===")
    
    # Search for similar notes
    query = "artificial intelligence and machine learning"
    print(f"Query: '{query}'")
    
    # Generate embedding for query
    query_embedding = embedder.get_embeddings_local([query])[0]
    
    # Find similar notes
    similar_notes = searcher.search_similar(query_embedding, top_k=3)
    
    print("Most similar notes:")
    for i, result in enumerate(similar_notes, 1):
        print(f"{i}. Note {result['note_id']} (Similarity: {result['similarity']:.3f}):")
        print(f"   {result['text']}")
        print()
    
    # Demonstrate cluster-based search
    print("=== Cluster-based Search ===")
    if clusterer.n_clusters > 0:
        target_cluster = 0  # Search in first cluster
        similar_in_cluster = searcher.find_similar_in_cluster(
            query_embedding, labels, target_cluster, top_k=2
        )
        
        print(f"Similar notes in cluster {target_cluster}:")
        for i, result in enumerate(similar_in_cluster, 1):
            print(f"{i}. Note {result['note_id']} (Similarity: {result['similarity']:.3f}):")
            print(f"   {result['text']}")
            print()

if __name__ == "__main__":
    main()
import json
from vector_db import vector_db
from memory_processor import MemoryProcessor
from config import GROQ_API_KEY

def load_sample_data():
    """Load sample lecture data"""
    try:
        with open('data/sample_lectures.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ Sample data file not found. Using default data.")
        return get_default_lectures()
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON format. Using default data.")
        return get_default_lectures()

def get_default_lectures():
    """Provide default lectures if file not found"""
    return [
        {
            "course": "Data Structures and Algorithms",
            "title": "Introduction to Stacks",
            "topics": ["stack", "LIFO", "push", "pop", "array implementation"],
            "content": "In this lecture, we covered stack data structure. Stack follows LIFO principle. We implemented stack using arrays with push and pop operations. Examples included browser back button and undo functionality in text editors.",
            "date": "2024-01-15",
            "instructor": "Dr. Smith"
        },
        {
            "course": "Data Structures and Algorithms",
            "title": "Queue Data Structure",
            "topics": ["queue", "FIFO", "enqueue", "dequeue", "circular queue"],
            "content": "This lecture introduced queue data structure following FIFO principle. We discussed enqueue and dequeue operations. Real-world examples included printer job scheduling and customer service lines.",
            "date": "2024-01-20",
            "instructor": "Dr. Smith"
        },
        {
            "course": "Database Systems",
            "title": "SQL Basics",
            "topics": ["SQL", "SELECT", "WHERE", "JOIN", "database queries"],
            "content": "Introduction to SQL with basic SELECT queries, WHERE clauses, and JOIN operations. Examples included student database queries and library management system.",
            "date": "2024-02-01",
            "instructor": "Dr. Johnson"
        },
        {
            "course": "Operating Systems",
            "title": "Process Scheduling",
            "topics": ["scheduling", "FCFS", "SJF", "priority", "round robin"],
            "content": "Covered various process scheduling algorithms including FCFS, SJF, Priority Scheduling, and Round Robin. Examples included CPU scheduling in multi-tasking systems.",
            "date": "2024-02-10",
            "instructor": "Dr. Williams"
        }
    ]

def initialize_database():
    """Initialize vector database with sample data"""
    print("\n🔧 Initializing College Memory Search Database...")
    
    # Load sample data
    lectures = load_sample_data()
    print(f"📚 Loaded {len(lectures)} lectures")
    
    # Process lectures with Groq for enhanced content (optional)
    print("🤖 Enhancing lecture content with Groq AI...")
    processor = MemoryProcessor()
    enhanced_lectures = []
    
    for i, lecture in enumerate(lectures, 1):
        print(f"  Processing {i}/{len(lectures)}: {lecture['title']}")
        try:
            enhanced_content = processor.generate_lecture_summary(lecture)
            enhanced_lecture = lecture.copy()
            enhanced_lecture['content'] = enhanced_content
            enhanced_lectures.append(enhanced_lecture)
        except Exception as e:
            print(f"  ⚠️ Error enhancing lecture, using original content: {e}")
            enhanced_lectures.append(lecture)
    
    # Add to vector database
    vector_db.add_lectures(enhanced_lectures)
    print("✅ Database initialized successfully!")

def search_interface():
    """Main search interface"""
    processor = MemoryProcessor()
    
    print("\n" + "="*50)
    print("🎓 COLLEGE MEMORY SEARCH ENGINE")
    print("="*50)
    
    while True:
        print("\n📋 Menu:")
        print("  1. 🔍 Search for specific topics")
        print("  2. 💬 Ask a question about lectures")
        print("  3. 📊 View database stats")
        print("  4. 🚪 Exit")
        
        choice = input("\n👉 Enter your choice (1-4): ").strip()
        
        if choice == '1':
            query = input("\n🔍 Enter search topic: ").strip()
            if query:
                try:
                    results = vector_db.search_similar(query, n_results=3)
                    
                    if results['documents'][0]:
                        print(f"\n✅ Found {len(results['documents'][0])} relevant lectures:")
                        print("-" * 50)
                        
                        for i, (doc, metadata, distance) in enumerate(zip(
                            results['documents'][0], 
                            results['metadatas'][0],
                            results['distances'][0]
                        ), 1):
                            print(f"\n{i}. 📖 {metadata['lecture_title']}")
                            print(f"   📚 Course: {metadata['course']}")
                            print(f"   👨‍🏫 Instructor: {metadata.get('instructor', 'N/A')}")
                            print(f"   📅 Date: {metadata.get('date', 'N/A')}")
                            print(f"   🎯 Relevance: {(1 - distance):.2%}")
                            print(f"   📝 Preview: {doc[:150]}...")
                    else:
                        print("❌ No relevant lectures found.")
                        
                except Exception as e:
                    print(f"❌ Search error: {e}")
        
        elif choice == '2':
            question = input("\n💬 Enter your question: ").strip()
            if question:
                try:
                    # Find relevant lectures
                    print("🔍 Searching relevant lectures...")
                    search_results = vector_db.search_similar(question, n_results=3)
                    
                    if not search_results['documents'][0]:
                        print("❌ No relevant information found in database.")
                        continue
                    
                    # Convert to document format for processor
                    context_docs = []
                    for doc, metadata in zip(
                        search_results['documents'][0], 
                        search_results['metadatas'][0]
                    ):
                        context_docs.append(type('Document', (object,), {
                            'page_content': doc,
                            'metadata': metadata
                        })())
                    
                    # Get answer using Groq
                    print("🤖 Generating answer with Groq AI...\n")
                    answer = processor.answer_question(question, context_docs)
                    
                    print("="*50)
                    print("📝 ANSWER:")
                    print("="*50)
                    print(answer)
                    print("="*50)
                    
                except Exception as e:
                    print(f"❌ Error processing question: {e}")
        
        elif choice == '3':
            try:
                count = vector_db.get_collection_info()
                print(f"\n📊 Database Statistics:")
                print(f"  📚 Total lectures: {count}")
                print(f"  💾 Storage location: {vector_db.client._settings.persist_directory}")
            except Exception as e:
                print(f"❌ Error fetching stats: {e}")
        
        elif choice == '4':
            print("\n👋 Thank you for using College Memory Search!")
            print("📚 Happy studying! 🎓")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    try:
        # Check API key
        if not GROQ_API_KEY:
            print("❌ Error: GROQ_API_KEY not found!")
            print("📝 Please create a .env file with your Groq API key:")
            print("   GROQ_API_KEY=your_key_here")
            exit(1)
            
        
        # Check if database is empty
        count = vector_db.get_collection_info()
        
        if count == 0:
            print("📦 No data found in database.")
            initialize_database()
        else:
            print(f"✅ Database loaded with {count} lectures")
        
        # Start search interface
        search_interface()
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
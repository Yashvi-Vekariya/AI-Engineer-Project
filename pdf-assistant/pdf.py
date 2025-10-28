import streamlit as st
import os
from groq import Groq
from pdf_processor import extract_text_from_pdf, chunk_text
from vector_store import VectorStoreManager
from config import GROQ_API_KEY, MODEL_NAME

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Initialize vector store manager
vector_manager = VectorStoreManager()

def initialize_session_state():
    """Initialize session state variables"""
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'processed_pdf' not in st.session_state:
        st.session_state.processed_pdf = False
    if 'question_input' not in st.session_state:
        st.session_state.question_input = ""

def process_pdf(uploaded_file):
    """Process uploaded PDF file"""
    try:
        with st.spinner("Processing PDF..."):
            # Extract text from PDF
            text = extract_text_from_pdf(uploaded_file)
            
            if not text.strip():
                st.error("No text could be extracted from the PDF. Please try a different file.")
                return False
            
            # Chunk the text
            chunks = chunk_text(text, metadata={"source": uploaded_file.name})
            
            # Create vector store
            vector_store = vector_manager.create_vector_store(chunks)
            st.session_state.vector_store = vector_store
            vector_manager.vector_store = vector_store
            st.session_state.processed_pdf = True
            
            st.success(f"✅ PDF processed successfully! Created {len(chunks)} chunks.")
            return True
            
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return False

def get_groq_response(query, context):
    """Get response from Groq LLM"""
    try:
        # Prepare prompt with context
        prompt = f"""Based on the following context from class notes, please answer the question.

Context:
{context}

Question: {query}

Please provide a clear, concise, and accurate answer based only on the provided context.
If the context doesn't contain relevant information, please state that.

Answer:"""
        
        # Call Groq API
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided class notes. Be precise and educational."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"Error getting response from Groq: {str(e)}"

def get_context_for_query(query):
    """Get relevant context for the query"""
    if st.session_state.vector_store:
        vector_manager.vector_store = st.session_state.vector_store
        similar_docs = vector_manager.similarity_search(query, k=3)
        context = "\n\n".join([doc.page_content for doc in similar_docs])
        return context
    return ""

def main():
    st.set_page_config(
        page_title="PDF Assistant for Class Notes",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 PDF Assistant for Class Notes")
    st.markdown("Upload your DBMS notes and ask questions like 'Explain 2NF quickly?'")
    
    initialize_session_state()
    
    # Sidebar for PDF upload
    with st.sidebar:
        st.header("Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose your class notes PDF",
            type="pdf",
            help="Upload your DBMS or other class notes PDF"
        )
        
        if uploaded_file is not None:
            if st.button("Process PDF"):
                process_pdf(uploaded_file)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Ask Questions")
        
        if not st.session_state.processed_pdf:
            st.info("👈 Please upload and process a PDF file first to start asking questions.")
        else:
            # Question input
            question = st.text_input(
                "Enter your question:",
                placeholder="e.g., Explain 2NF quickly?",
                value=st.session_state.question_input,
                key="question_input_field"
            )
            
            if st.button("Get Answer") and question:
                with st.spinner("Searching for answer..."):
                    # Get relevant context
                    context = get_context_for_query(question)
                    
                    if not context:
                        st.warning("No relevant context found in the PDF for this question.")
                    else:
                        # Get answer from Groq
                        answer = get_groq_response(question, context)
                        
                        # Display answer
                        st.subheader("Answer:")
                        st.write(answer)
                        
                        # Show context sources (optional)
                        with st.expander("View relevant context from PDF"):
                            st.write(context)
    
    with col2:
        st.header("How to Use")
        st.markdown("""
        1. **Upload PDF**: Use the sidebar to upload your class notes PDF
        2. **Process PDF**: Click 'Process PDF' to analyze the content
        3. **Ask Questions**: Type questions about your notes
        4. **Get Answers**: Receive AI-powered answers based on your PDF
        
        **Example Questions:**
        - "Explain 2NF quickly?"
        - "What is normalization?"
        - "Describe ACID properties"
        - "What are the types of joins?"
        """)
        
        if st.session_state.processed_pdf:
            st.success("✅ PDF is ready for questioning!")
            
            # Quick action buttons
            st.subheader("Quick Actions")
            if st.button("What is Normalization?"):
                st.session_state.question_input = "What is Normalization?"
                st.rerun()
            
            if st.button("Explain 2NF"):
                st.session_state.question_input = "Explain 2NF quickly?"
                st.rerun()

if __name__ == "__main__":
    main()
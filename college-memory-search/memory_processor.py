from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
import json

class MemoryProcessor:
    def __init__(self):
        """Initialize Groq client"""
        if not GROQ_API_KEY:
            raise ValueError("❌ GROQ_API_KEY is not set in config!")
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
    
    def generate_lecture_summary(self, lecture_data):
        """Generate enhanced lecture content using Groq"""
        try:
            # Use existing content if available, otherwise create from topics
            existing_content = lecture_data.get('content', '')
            
            prompt = f"""
            Create a detailed and comprehensive lecture summary based on the following information:
            
            Course: {lecture_data['course']}
            Title: {lecture_data['title']}
            Key Topics: {', '.join(lecture_data['topics'])}
            Original Content: {existing_content}
            
            Please provide a comprehensive summary that includes:
            1. Main concepts explained in detail
            2. Real-world examples and use cases
            3. Key takeaways students should remember
            4. Practical applications in industry or daily life
            5. Important formulas, algorithms, or patterns (if applicable)
            
            Make it detailed, educational, and easy to understand. Use clear language suitable for college students.
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational assistant that creates detailed, accurate lecture summaries for college students. Your summaries should be comprehensive, well-structured, and include practical examples."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            enhanced_content = response.choices[0].message.content
            print(f"  ✅ Enhanced: {lecture_data['title']}")
            return enhanced_content
            
        except Exception as e:
            print(f"  ⚠️ Error generating summary for '{lecture_data.get('title', 'Unknown')}': {e}")
            # Fallback to original content
            return lecture_data.get('content', f"Lecture about {', '.join(lecture_data.get('topics', []))}")
    
    def answer_question(self, question, context_documents):
        """Answer questions based on retrieved lecture context"""
        try:
            # Build context from documents
            context_parts = []
            for idx, doc in enumerate(context_documents, 1):
                lecture_title = doc.metadata.get('lecture_title', 'Unknown')
                course = doc.metadata.get('course', 'Unknown')
                content = doc.page_content
                
                context_parts.append(
                    f"[Lecture {idx}]\n"
                    f"Title: {lecture_title}\n"
                    f"Course: {course}\n"
                    f"Content: {content}\n"
                )
            
            context = "\n---\n".join(context_parts)
            
            prompt = f"""
            Based on the following lecture materials, answer the student's question accurately and helpfully.
            
            LECTURE MATERIALS:
            {context}
            
            STUDENT'S QUESTION: {question}
            
            Instructions:
            1. Provide a clear, direct answer to the question
            2. Cite which specific lecture(s) contained this information
            3. Include relevant examples or explanations from the lectures
            4. If the question asks for comparison, compare concepts clearly
            5. If information is not found in the materials, clearly state that
            
            Be conversational but accurate. Help the student understand the concept.
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful college teaching assistant that answers questions based on lecture materials. Be precise, cite specific lectures, and explain concepts clearly. If you don't know something from the provided materials, admit it rather than guessing."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=800,
                top_p=1,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = f"❌ Error processing question: {str(e)}"
            print(error_msg)
            return error_msg
    
    def generate_quiz_questions(self, lecture_data, num_questions=3):
        """Generate quiz questions from lecture content (bonus feature)"""
        try:
            prompt = f"""
            Based on this lecture, generate {num_questions} multiple-choice quiz questions to test student understanding:
            
            Course: {lecture_data['course']}
            Title: {lecture_data['title']}
            Topics: {', '.join(lecture_data['topics'])}
            Content: {lecture_data.get('content', '')}
            
            For each question:
            1. Write a clear question
            2. Provide 4 options (A, B, C, D)
            3. Indicate the correct answer
            4. Give a brief explanation
            
            Format as JSON.
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating educational quiz questions that test understanding, not just memorization."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.4,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating quiz: {e}"
    
    def explain_concept(self, concept, context=""):
        """Explain a specific concept in simple terms (bonus feature)"""
        try:
            prompt = f"""
            Explain the following concept in simple terms suitable for a college student:
            
            Concept: {concept}
            Additional Context: {context}
            
            Provide:
            1. A clear definition
            2. A simple analogy or example
            3. Why it's important
            4. Common misconceptions (if any)
            
            Keep it concise but thorough.
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a patient tutor who explains complex concepts in simple, relatable terms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=512
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error explaining concept: {e}"
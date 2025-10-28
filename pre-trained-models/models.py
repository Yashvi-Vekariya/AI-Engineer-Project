from dotenv import load_dotenv
load_dotenv()

import os
from groq import Groq
from datetime import datetime

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# System prompt that defines the Motivation Buddy's personality
SYSTEM_PROMPT = """You are a warm, empathetic Motivation Buddy. Your role is to:
- Provide genuine encouragement and support
- Normalize struggles and failures as part of growth
- Give practical perspective without being preachy
- Use a friendly, conversational tone
- Keep responses concise (2-4 paragraphs)
- Acknowledge feelings while redirecting to positive action

Remember: Everyone struggles. Progress > Perfection."""

def get_motivation(user_message):
    """
    Get a motivational response from the chatbot
    
    Args:
        user_message (str): The user's concern or question
    
    Returns:
        str: Motivational response from the AI
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and powerful
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=300
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Oops! Something went wrong: {str(e)}\nPlease check your API key and internet connection."

def daily_motivation():
    """Generate a random daily motivation message"""
    prompts = [
        "Give me a motivational message to start my day",
        "I need encouragement for today",
        "Tell me something inspiring for the morning"
    ]
    import random
    return get_motivation(random.choice(prompts))

def main():
    """Main function to run the Motivation Buddy chatbot"""
    print("=" * 60)
    print("💪 MOTIVATION BUDDY - Your Personal Cheerleader! 💪")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%B %d, %Y')}")
    print("⚡ Powered by Groq - SUPER FAST & FREE!")
    print("\nType 'quit' or 'exit' to close the chat")
    print("Type 'daily' for a random motivation boost")
    print("-" * 60)
    
    # Conversation history to maintain context
    conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    while True:
        user_input = input("\n🫵 You: ").strip()
        
        if not user_input:
            print("⚠️  Please enter a message!")
            continue
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\n💙 Remember: You're doing better than you think!")
            print("Keep going, champ! See you next time! 👋\n")
            break
        
        if user_input.lower() == 'daily':
            print("\n🤖 Motivation Buddy: ", end="")
            response = daily_motivation()
            print(response)
            continue
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})
        
        print("\n🤖 Motivation Buddy: ", end="")
        
        try:
            # Get response with conversation history
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=conversation_history,
                temperature=0.8,
                max_tokens=300
            )
            
            assistant_message = response.choices[0].message.content
            print(assistant_message)
            
            # Add assistant response to history
            conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Keep only last 10 messages to avoid token limits
            if len(conversation_history) > 11:
                conversation_history = [conversation_history[0]] + conversation_history[-10:]
        
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Please check your API key and try again.")

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("GROQ_API_KEY"):
        print("=" * 60)
        print("❌ ERROR: Groq API key not found!")
        print("=" * 60)
        print("\n🔑 Get your FREE API key (takes 1 minute):")
        print("   1. Go to: https://console.groq.com/keys")
        print("   2. Sign up (free, no credit card needed)")
        print("   3. Click 'Create API Key'")
        print("   4. Copy the key (starts with 'gsk_...')")
        print("\n💾 Add to your .env file:")
        print("   GROQ_API_KEY=gsk_your-api-key-here")
        print("\n⚡ Or set as environment variable:")
        print("   Windows (PowerShell): $env:GROQ_API_KEY='gsk_your-key-here'")
        print("   Mac/Linux: export GROQ_API_KEY=gsk_your-key-here")
        print("\n🚀 WHY GROQ?")
        print("   ✅ 100% FREE - No credit card required")
        print("   ✅ SUPER FAST - 10x faster than GPT-4")
        print("   ✅ NO LIMITS - 30 requests/minute (6000/day)")
        print("   ✅ POWERFUL - Uses Llama 3.3 70B model")
        print("=" * 60)
        input("\nPress Enter to exit...")
    else:
        main()
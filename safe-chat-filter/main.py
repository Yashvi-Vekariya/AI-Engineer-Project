import os
from moderator import ChatModerator

def main():
    # Initialize moderator
    moderator = ChatModerator()
    
    print("🔒 Safe Chat Filter - School Chat Moderation System")
    print("=" * 50)
    
    # Sample users for demonstration
    sample_users = ["student_001", "student_002", "student_003"]
    
    while True:
        print("\n--- New Message ---")
        
        # Get user input
        try:
            user_id = input("Enter User ID: ").strip()
            if not user_id:
                user_id = sample_users[0]  # Default user for demo
            
            message = input("Enter Message: ").strip()
            
            if message.lower() in ['exit', 'quit']:
                break
            
            if not message:
                print("Message cannot be empty!")
                continue
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        
        # Moderate the message
        result = moderator.check_message(user_id, message)
        
        # Display result
        print("\n" + "=" * 30)
        if result["allowed"]:
            print("✅ MESSAGE APPROVED")
            print(f"From: {user_id}")
            print(f"Message: {result['filtered_message']}")
        else:
            print("❌ MESSAGE BLOCKED")
            print(f"From: {user_id}")
            print(f"Reason: {result['reason']}")
            print(f"Display: {result['filtered_message']}")
        
        print("=" * 30)

if __name__ == "__main__":
    # Check for API key
    if not os.getenv('GROQ_API_KEY'):
        print("❌ ERROR: GROQ_API_KEY environment variable not set!")
        print("Please set it using: export GROQ_API_KEY='your-api-key'")
        exit(1)
    
    main()
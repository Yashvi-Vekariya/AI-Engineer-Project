from translator import translator
from model_loader import model_loader
import os

def main():
    print("🌍 Gujarati ↔ English Translator")
    print("=" * 50)
    
    # Show available models
    models = model_loader.get_available_models()
    print("\n📚 Available Translation Models:")
    for model in models:
        print(f"  • {model['name']} ({model['model_name']})")
    
    # Show supported languages
    languages = translator.get_supported_languages()
    print("\n🌐 Supported Languages:")
    for code, name in languages.items():
        print(f"  • {code}: {name}")
    
    print("\n🎯 Usage Options:")
    print("  1. Command Line Interface (CLI)")
    print("  2. Web Interface")
    print("  3. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                cli_interface()
            elif choice == '2':
                web_interface()
            elif choice == '3':
                print("Goodbye! 👋")
                break
            else:
                print("Please select 1, 2, or 3")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break

def cli_interface():
    """Command line translation interface"""
    print("\n🚀 Command Line Translator")
    print("Type 'back' to return to main menu")
    print("Type 'swap' to swap languages")
    
    # Default languages
    source_lang = 'en'
    target_lang = 'gu'
    
    while True:
        print(f"\n🔤 Translation: {translator.get_supported_languages()[source_lang]} → {translator.get_supported_languages()[target_lang]}")
        
        text = input("\nEnter text to translate: ").strip()
        
        if text.lower() == 'back':
            break
        elif text.lower() == 'swap':
            source_lang, target_lang = target_lang, source_lang
            print(f"🔄 Swapped to: {translator.get_supported_languages()[source_lang]} → {translator.get_supported_languages()[target_lang]}")
            continue
        elif not text:
            continue
        
        print("⏳ Translating...")
        
        # Perform translation
        result = translator.translate_text(text, source_lang, target_lang)
        
        if result['success']:
            print(f"\n✅ Translated Text:")
            print(f"   {result['translated_text']}")
            print(f"\n   📝 From {result['source_lang']} to {result['target_lang']}")
        else:
            print(f"\n❌ Error: {result['error']}")

def web_interface():
    """Start web interface"""
    print("\n🌐 Starting Web Interface...")
    print("   The translator will open in your web browser")
    print("   Press Ctrl+C to stop the server")
    
    try:
        # Import and run the web interface
        from web_interface import app
        import webbrowser
        import threading
        
        # Open browser after a short delay
        def open_browser():
            import time
            time.sleep(2)
            webbrowser.open(f'http://localhost:{app.config["PORT"]}')
        
        threading.Thread(target=open_browser).start()
        
        # Run the app
        app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
        
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        print("   Make sure you have Flask installed: pip install flask")

if __name__ == "__main__":
    main()
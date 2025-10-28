import streamlit as st
import base64
from PIL import Image
import io
import os
from dotenv import load_dotenv
from vision_analyzer import analyze_food_image
from speech_processor import text_to_speech, speech_to_text
from calorie_calculator import estimate_calories

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(
        page_title="Healthy Food Image Analyzer",
        page_icon="🍎",
        layout="wide"
    )
    
    st.title("🍎 Healthy Food Image Analyzer")
    st.markdown("Snap a food picture → Get approximate calories and nutrition info!")
    
    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose Input Method:", 
                               ["Image Upload", "Voice Description"])
    
    if app_mode == "Image Upload":
        image_analysis()
    else:
        voice_analysis()

def image_analysis():
    st.header("📸 Image Analysis")
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Choose a food image...", 
        type=['jpg', 'jpeg', 'png']
    )
    
    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Image", use_column_width=True)
        
        # Analyze button
        if st.button("Analyze Food Image"):
            with st.spinner("Analyzing your food image..."):
                try:
                    # Convert image to base64
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Analyze image
                    analysis_result = analyze_food_image(img_str)
                    st.session_state.result = analysis_result
                    
                except Exception as e:
                    st.error(f"Error analyzing image: {str(e)}")
    
    # Display results
    if st.session_state.result:
        display_results(st.session_state.result)

def voice_analysis():
    st.header("🎤 Voice Analysis")
    
    st.info("Describe your food verbally and get calorie estimation!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Recording"):
            with st.spinner("Listening..."):
                try:
                    # Capture speech
                    food_description = speech_to_text()
                    if food_description:
                        st.success(f"Detected: {food_description}")
                        
                        # Analyze description
                        with st.spinner("Analyzing your description..."):
                            analysis_result = estimate_calories(food_description)
                            st.session_state.result = analysis_result
                    else:
                        st.warning("No speech detected. Please try again.")
                        
                except Exception as e:
                    st.error(f"Error processing speech: {str(e)}")
    
    with col2:
        # Manual text input as fallback
        food_text = st.text_input("Or type food description:")
        if st.button("Analyze Text") and food_text:
            with st.spinner("Analyzing..."):
                analysis_result = estimate_calories(food_text)
                st.session_state.result = analysis_result
    
    # Display results
    if st.session_state.result:
        display_results(st.session_state.result)

def display_results(result):
    st.header("📊 Analysis Results")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Food Identified")
        st.write(f"**{result.get('food_name', 'Unknown')}**")
        
        st.subheader("Estimated Calories")
        st.metric(
            label="Calories", 
            value=f"{result.get('calories', 0)}",
            delta=None
        )
    
    with col2:
        st.subheader("Nutrition Information")
        nutrition = result.get('nutrition', {})
        
        if nutrition:
            st.write(f"**Protein:** {nutrition.get('protein', '0')}g")
            st.write(f"**Carbs:** {nutrition.get('carbs', '0')}g") 
            st.write(f"**Fat:** {nutrition.get('fat', '0')}g")
            st.write(f"**Fiber:** {nutrition.get('fiber', '0')}g")
        
        # Health score
        health_score = result.get('health_score', 0)
        st.subheader("Health Score")
        st.progress(health_score / 100)
        st.write(f"{health_score}/100")
    
    # Additional insights
    st.subheader("💡 Health Insights")
    insights = result.get('insights', [])
    for insight in insights:
        st.info(insight)
    
    # Text-to-speech option
    st.subheader("🔊 Audio Summary")
    if st.button("Listen to Results"):
        with st.spinner("Generating audio..."):
            try:
                summary = f"""
                The food appears to be {result.get('food_name', 'unknown')}. 
                Estimated calories: {result.get('calories', 0)}.
                {result.get('health_advice', 'Enjoy in moderation!')}
                """
                audio_file = text_to_speech(summary)
                st.session_state.audio_file = audio_file
                
                # Play audio
                st.audio(audio_file, format='audio/mp3')
                
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")

if __name__ == "__main__":
    main()
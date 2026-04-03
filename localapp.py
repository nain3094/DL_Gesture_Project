import cv2
import numpy as np
import streamlit as st
import pyautogui
import time
import operator
import os

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from speech_to_text import recognize_speech, transcribe_audio_file
from video_summarizer import video_summarizer_page
from gesture_notes_manager import GestureNotesManager

# Configure page
st.set_page_config(
    page_title="Hand Gesture & AI Features",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .streamlit-container {
        max-width: 1200px;
    }
    h1 {
        color: #f63366;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .feature-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #f63366;
        margin: 10px 0;
    }
    .info-badge {
        display: inline-block;
        background-color: #e7f3ff;
        color: #0066cc;
        padding: 8px 12px;
        border-radius: 5px;
        margin: 5px 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

loaded_model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(120,120,1)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Conv2D(128, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(256, activation='relu'),
    Dense(7, activation='softmax')
])

loaded_model.load_weights("gesture-model.h5")

categories = {
    0: 'palm',
    1: 'fist',
    2: 'thumbs-up',
    3: 'thumbs-down',
    4: 'index-right',
    5: 'index-left',
    6: 'no-gesture'
}

def main():
    # Header with styling
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>🎯 Hand Gesture Recognition & AI Suite</h1>
        <p style="font-size: 1.1rem; color: #666;">Smart control with hand gestures, speech recognition, and video analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("###  **Navigation**")
        pages = [
            '📋 About Web App',
            '👋 Gesture Control',
            '🎤 Speech to Text',
            '🎥 Video Summarizer'
        ]
        page = st.selectbox('Select a feature:', pages)

    # Main content based on selection
    if page == '📋 About Web App':
        with st.container():
            st.markdown("""
            <div class="feature-box">
                <h2>🎯 About This Application</h2>
                <p style="font-size: 1.1rem;">
                    This is an advanced AI suite combining hand gesture recognition, speech processing, 
                    and video analysis for smart control and learning.                     ~ By Naina, Nishtha & Rajsekhar
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Features overview
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="feature-box">
                    <h3>👋 Gesture Control</h3>
                    <p>Control your media player with natural hand gestures. No hardware needed!</p>
                    <ul>
                        <li>🎬 Play/Pause</li>
                        <li>🔊 Volume Control</li>
                        <li>⏭️ Skip Tracks</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="feature-box">
                    <h3>🎤 Speech to Text</h3>
                    <p>Convert speech directly to text or transcribe audio files.</p>
                    <ul>
                        <li>🎙️ Real-time Recording</li>
                        <li>📁 File Upload</li>
                        <li>💾 Multiple Export</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="feature-box">
                    <h3>🎥 Video Intelligence</h3>
                    <p>Analyze videos and generate educational notes automatically.</p>
                    <ul>
                        <li>🔍 Key Frame Extraction</li>
                        <li>📊 Content Analysis</li>
                        <li>📚 Study Notes</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Tech Stack
            st.markdown("### 💻 Technologies Used")
            tech_cols = st.columns(4)
            with tech_cols[0]:
                st.markdown("**<p style='text-align:center'>🤖 TensorFlow</p>**", unsafe_allow_html=True)
            with tech_cols[1]:
                st.markdown("**<p style='text-align:center'>📷 OpenCV</p>**", unsafe_allow_html=True)
            with tech_cols[2]:
                st.markdown("**<p style='text-align:center'>🌐 Streamlit</p>**", unsafe_allow_html=True)
            with tech_cols[3]:
                st.markdown("**<p style='text-align:center'>🎙️ SpeechRecognition</p>**", unsafe_allow_html=True)


    elif page == '👋 Gesture Control':
        # Initialize gesture notes
        GestureNotesManager.initialize()
        
        st.markdown("""
        <div class="feature-box">
            <h2>👋 Hand Gesture Control & Note Taking</h2>
            <p>Control your media player with hand gestures and automatically record actions as notes.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.markdown("### ⚙️ Controls")
            run = st.button('🔴 Start Camera', use_container_width=True, type="primary")
            
            st.markdown("### 📋 Gestures")
            st.write("""
            - 🖐️ **Palm** → Play/Pause
            - ✊ **Fist** → Mute
            - 👍 **Thumbs Up** → Volume +
            - 👎 **Thumbs Down** → Volume -
            - ☝️ **Index Right** → Next
            - ☝️ **Index Left** → Previous
            """)
            
            st.divider()
            
            # Note taking section in sidebar
            st.markdown("### 📝 Quick Notes")
            quick_note = st.text_input("Add a note:", placeholder="Type your observation...")
            if st.button("➕ Add Note", use_container_width=True):
                if quick_note:
                    GestureNotesManager.add_note('Manual', f'Note: {quick_note}')
                    st.success("✅ Note added!")

        with col1:
            FRAME_WINDOW1 = st.image([])
            FRAME_WINDOW2 = st.image([])

            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

            while run:
                ret, frame = camera.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)

                x1 = int(0.5 * frame.shape[1])
                y1 = 10
                x2 = frame.shape[1] - 10
                y2 = int(0.5 * frame.shape[1])

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                roi = frame[y1:y2, x1:x2]
                roi = cv2.resize(roi, (120,120))
                roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, test_image = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY)

                FRAME_WINDOW1.image(test_image)

                result = loaded_model.predict(test_image.reshape(1,120,120,1), verbose=0)

                prediction = {
                    'palm': result[0][0],
                    'fist': result[0][1],
                    'thumbs-up': result[0][2],
                    'thumbs-down': result[0][3],
                    'index-right': result[0][4],
                    'index-left': result[0][5],
                    'no-gesture': result[0][6]
                }

                prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
                label = prediction[0][0]
                action = "NO ACTION"

                if label == 'palm':
                    action = "PLAY/PAUSE"
                    GestureNotesManager.add_note(label, action)  # Record gesture
                    try:
                        pyautogui.press('playpause')
                    except:
                        pyautogui.hotkey('shift', 'space')  # Fallback
                    time.sleep(0.5)
                elif label == 'fist':
                    action = "MUTE"
                    GestureNotesManager.add_note(label, action)  # Record gesture
                    try:
                        pyautogui.press('volumemute')
                    except:
                        pyautogui.hotkey('ctrl', 'alt', 'm')  # Fallback
                    time.sleep(0.5)
                elif label == 'thumbs-up':
                    action = "VOLUME UP"
                    GestureNotesManager.add_note(label, action)  # Record gesture
                    try:
                        pyautogui.press('volumeup')
                    except:
                        for _ in range(3):
                            pyautogui.hotkey('ctrl', 'up')  # Fallback
                elif label == 'thumbs-down':
                    action = "VOLUME DOWN"
                    GestureNotesManager.add_note(label, action)  # Record gesture
                    try:
                        pyautogui.press('volumedown')
                    except:
                        for _ in range(3):
                            pyautogui.hotkey('ctrl', 'down')  # Fallback
                elif label == 'index-right':
                    action = "FORWARD"
                    GestureNotesManager.add_note(label, action)  # Record gesture
                    try:
                        pyautogui.press('nexttrack')
                    except:
                        pyautogui.hotkey('ctrl', 'right')  # Fallback
                elif label == 'index-left':
                    action = "REWIND"
                    GestureNotesManager.add_note(label, action)  # Record gesture
                    try:
                        pyautogui.press('prevtrack')
                    except:
                        pyautogui.hotkey('ctrl', 'left')  # Fallback

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                cv2.putText(frame, f"Gesture: {label}", (10,120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

                cv2.putText(frame, f"Action: {action}", (10,180),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

                FRAME_WINDOW2.image(frame)

            camera.release()
            cv2.destroyAllWindows()
        
        # Display collected notes and export options
        st.divider()
        st.markdown("### 📊 Session Notes")
        
        GestureNotesManager.display_notes()
        
        # Export options
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save as TXT", use_container_width=True):
                filename = GestureNotesManager.save_notes_as_file()
                if filename:
                    st.success(f"✅ Saved as {filename}")
                    with open(filename, 'r') as f:
                        st.download_button(
                            label="⬇️ Download TXT",
                            data=f.read(),
                            file_name=filename,
                            mime="text/plain"
                        )
        
        with col2:
            if st.button("📋 Save as JSON", use_container_width=True):
                filename = GestureNotesManager.save_notes_as_json()
                if filename:
                    st.success(f"✅ Saved as {filename}")
                    with open(filename, 'r') as f:
                        st.download_button(
                            label="⬇️ Download JSON",
                            data=f.read(),
                            file_name=filename,
                            mime="application/json"
                        )
        
        with col3:
            if st.button("🗑️ Clear Notes", use_container_width=True):
                GestureNotesManager.clear_notes()
                st.success("✅ All notes cleared!")

    elif page == '🎤 Speech to Text':
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; margin-bottom: 20px;">
            <h1 style="text-align: center; color: white; margin: 0;">🎤 Speech to Text Converter</h1>
            <p style="text-align: center; font-size: 1.1rem; margin: 10px 0; color: rgba(255,255,255,0.9);">Transform your voice into text with AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for different input methods
        tab1, tab2 = st.tabs(["🎙️ Live Recording", "📁 Upload Audio"])
        
        with tab1:
            st.markdown("""
            <div class="feature-box">
                <p><strong>Record directly from your microphone</strong></p>
                <p style="color: #666; font-size: 0.9rem;">Up to 30 seconds of recording time</p>
            </div>
            """, unsafe_allow_html=True)
            recognize_speech()
        
        with tab2:
            st.markdown("""
            <div class="feature-box">
                <p><strong>Upload an audio file for transcription</strong></p>
                <p style="color: #666; font-size: 0.9rem;">Supports: WAV, MP3, FLAC, OGG</p>
            </div>
            """, unsafe_allow_html=True)
            transcribe_audio_file()

    elif page == '🎥 Video Summarizer':
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 10px; color: white; margin-bottom: 20px;">
            <h1 style="text-align: center; color: white; margin: 0;">🎥 Video Summarizer & Notes Generator</h1>
            <p style="text-align: center; font-size: 1.1rem; margin: 10px 0; color: rgba(255,255,255,0.9);">AI-powered video analysis and educational notes</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**<p style='text-align:center'>📸 Key Frames</p>**", unsafe_allow_html=True)
        with col2:
            st.markdown("**<p style='text-align:center'>🎪 Scene Detection</p>**", unsafe_allow_html=True)
        with col3:
            st.markdown("**<p style='text-align:center'>📚 Study Notes</p>**", unsafe_allow_html=True)
        
        st.divider()
        
        video_summarizer_page()

if __name__ == "__main__":
    main()
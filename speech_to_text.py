import speech_recognition as sr
import streamlit as st
from datetime import datetime
import os

# Optional fallback capture path if pyaudio/Microphone has problems
def _record_with_sounddevice(duration=30, sample_rate=16000):
    import sounddevice as sd
    import numpy as np

    st.info("🎧 Falling back to sounddevice recording (no PyAudio needed)")
    st.info("⌛ Please speak clearly for up to 30 seconds...")

    audio_array = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()

    # Convert to bytes and create speech_recognition.AudioData
    audio_bytes = np.array(audio_array, dtype='int16').tobytes()
    return sr.AudioData(audio_bytes, sample_rate, 2)


def recognize_speech():
    """
    Captures audio from microphone and converts to text with improved listening time
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 4000
    
    st.write("🎤 **Click the button below and start speaking.**")
    st.info("⏱️ The app will listen for up to 30 seconds. Speak naturally and clearly.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        record_button = st.button(" Start Recording", key="record_audio", use_container_width=True)
    
    if record_button:
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            try:
                with sr.Microphone() as source:
                    # Adjust for ambient noise (longer duration for better calibration)
                    status_placeholder.info("🎵 Calibrating microphone... Please wait")
                    recognizer.adjust_for_ambient_noise(source, duration=2)
                    
                    status_placeholder.success(" Microphone ready! Speak now...")
                    progress_placeholder.write("⏳ **Listening...** (30 second limit)")
                    
                    # Listen for audio - increased timeout to 30 seconds
                    audio_data = recognizer.listen(
                        source, 
                        timeout=30,  # Increased from 10 to 30 seconds
                        phrase_time_limit=30  # Increased from 10 to 30 seconds
                    )

                progress_placeholder.success("✅ Audio captured successfully via PyAudio/Microphone!")
                status_placeholder.empty()
            except Exception as inner_e:
                #st.warning(f" {str(inner_e)}")
                #st.warning("Switching to sounddevice fallback recording—please speak clearly.")
                audio_data = _record_with_sounddevice(duration=30, sample_rate=16000)
                progress_placeholder.success("✅ Audio captured successfully via sounddevice fallback!")
                status_placeholder.empty()

            # Show processing message
            with st.spinner("🔄 Converting speech to text..."):
                # Try to recognize speech using Google Speech Recognition API
                text = recognizer.recognize_google(audio_data)
            
            st.success("✅ **Transcription Complete!**")
            
            # Display with better styling
            st.divider()
            st.write("### 📝 Recognized Text:")
            
            # Create a nice display box
            st.markdown(f"""
            <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 4px solid #1f77b4;">
                <p style="font-size: 16px; color: #333;">{text}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Display in a selectable text area
            st.text_area("📋 Copy text from here:", value=text, height=120, disabled=True, key="transcribed_text_microphone")
            
            # Better button layout
            st.write("### 💾 Export Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download button for text file
                st.download_button(
                    label="⬇️ Download as TXT",
                    data=text,
                    file_name=f"speech_to_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                # Save locally
                if st.button("💾 Save Locally", use_container_width=True, key="save_speech_local"):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"transcription_{timestamp}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(text)
                    st.balloons()
                    st.success(f"✅ Saved as **{filename}**")
            
            with col3:
                # Copy to clipboard button
                if st.button("📋 Copy to Clipboard", use_container_width=True, key="copy_speech"):
                    try:
                        # Try to use streamlit's built-in copy capability
                        st.session_state.copied_text = text
                        st.toast("✅ Text copied to clipboard!", icon="📋")
                    except:
                        st.info("💡 Click in the text area above and use Ctrl+C to copy")
            
            # Statistics
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Words", len(text.split()))
            with col2:
                st.metric("📝 Characters", len(text))
            with col3:
                st.metric("🎤 Duration", f"{len(text.split()) / 150:.1f} min")
            
            return text
                
        except sr.UnknownValueError:
            st.error("❌ **Could not understand the audio.** Please try again with clearer speech.")
            st.info("💡 Tips: Speak slower, louder, and reduce background noise")
        except sr.RequestError as e:
            st.error(f"❌ **Google Speech API Error:** {e}")
            st.info("⚠️ Make sure you have an active internet connection.")
        except Exception as e:
            st.error(f"❌ **Error:** {str(e)}")
            st.info("⚠️ Make sure your microphone is connected, enabled, and not in use by another app.")

def transcribe_audio_file():
    """
    Transcribe audio from uploaded file with improved UI
    """
    st.write("📁 **Upload an audio file to transcribe**")
    st.info("Supported formats: WAV, MP3, FLAC, OGG")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file", 
        type=['wav', 'mp3', 'flac', 'ogg'],
        help="Select an audio file for transcription"
    )
    
    if uploaded_file is not None:
        # Display audio player
        st.write("### 🎵 Preview")
        st.audio(uploaded_file, format='audio/wav')
        
        st.divider()
        
        if st.button("🎙️ Transcribe Audio File", use_container_width=True, type="primary"):
            try:
                recognizer = sr.Recognizer()
                recognizer.energy_threshold = 4000
                
                # Save uploaded file temporarily
                temp_file = "temp_audio_file.wav"
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                with st.spinner("🔄 Processing audio file..."):
                    with sr.AudioFile(temp_file) as source:
                        audio_data = recognizer.record(source)
                        text = recognizer.recognize_google(audio_data)
                    
                st.success("✅ **Transcription Complete!**")
                st.divider()
                
                st.write("### 📝 Recognized Text:")
                st.markdown(f"""
                <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 4px solid #1f77b4;">
                    <p style="font-size: 16px; color: #333;">{text}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.divider()
                
                # Display in selectable text area
                st.text_area("📋 Copy text from here:", value=text, height=120, disabled=True, key="transcribed_text_file")
                
                # Better button layout
                st.write("### 💾 Export Options")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Download button for text file
                    st.download_button(
                        label="⬇️ Download as TXT",
                        data=text,
                        file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col2:
                    # Save locally
                    if st.button("💾 Save Locally", use_container_width=True, key="save_audio_local"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"transcription_file_{timestamp}.txt"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(text)
                        st.balloons()
                        st.success(f"✅ Saved as **{filename}**")
                
                with col3:
                    # Copy to clipboard
                    if st.button("📋 Copy to Clipboard", use_container_width=True, key="copy_audio"):
                        st.session_state.copied_text = text
                        st.toast("✅ Text copied to clipboard!", icon="📋")
                
                # Statistics
                st.divider()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Words", len(text.split()))
                with col2:
                    st.metric("📝 Characters", len(text))
                with col3:
                    st.metric("⏱️ Duration", f"{len(text.split()) / 150:.1f} min")
                    
            except sr.UnknownValueError:
                st.error("❌ **Could not understand the audio in the file.**")
                st.info("💡 Make sure the audio quality is good and speech is clear.")
            except sr.RequestError as e:
                st.error(f"❌ **Google Speech API Error:** {e}")
            except Exception as e:
                st.error(f"❌ **Error:** {str(e)}")
                st.info("💡 Try converting the audio file to WAV format first.")
                
            finally:
                # Cleanup
                if os.path.exists("temp_audio_file.wav"):
                    os.remove("temp_audio_file.wav")

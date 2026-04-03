import cv2
import numpy as np
import streamlit as st
import os
from datetime import timedelta
import json
from datetime import datetime
from video_notes_generator import save_notes_as_text, save_notes_as_pdf

def analyze_frame_content(frame):
    """
    Analyze a single frame to detect content type
    Returns description of frame content
    """
    # Convert to HSV for color analysis
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Detect dominant colors and features
    height, width = frame.shape[:2]
    
    # Calculate color distribution
    blue_channel = frame[:,:,0].mean()
    green_channel = frame[:,:,1].mean()
    red_channel = frame[:,:,2].mean()
    
    # Detect edges for motion/activity
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges) / (height * width * 255)
    
    # Detect brightness
    brightness = gray.mean()
    
    description = ""
    
    # Brightness-based description
    if brightness < 50:
        description += "Dark scene. "
    elif brightness > 200:
        description += "Bright/Well-lit scene. "
    else:
        description += "Moderately lit scene. "
    
    # Activity level based on edges
    if edge_density > 0.15:
        description += "High activity/Motion detected. "
    elif edge_density > 0.08:
        description += "Moderate activity. "
    else:
        description += "Low activity/Stable shot. "
    
    # Color dominance
    if red_channel > green_channel and red_channel > blue_channel:
        description += "Red/Warm tones present. "
    elif green_channel > red_channel and green_channel > blue_channel:
        description += "Green/Natural tones present. "
    elif blue_channel > red_channel and blue_channel > green_channel:
        description += "Blue/Cool tones present. "
    
    return description.strip()

def generate_ai_summary(video_path, stats, key_frames, scene_changes):
    """
    Generate AI-powered summary of video content using already-extracted key frames
    Creates meaningful text describing what the video is about
    """
    try:
        duration = stats.get('duration', 0)
        fps = stats.get('fps', 0)
        
        # Analyze the key frames that were already extracted
        frame_descriptions = []
        if key_frames:
            for frame in key_frames:
                try:
                    frame_desc = analyze_frame_content(frame)
                    frame_descriptions.append(frame_desc)
                except Exception as e:
                    frame_descriptions.append(f"Unable to analyze frame: {str(e)[:30]}")
        
        # Generate summary based on analysis
        summary = f"""
🎬 VIDEO CONTENT ANALYSIS & SUMMARY
═══════════════════════════════════════════════════════════════

📊 Video Characteristics:
• Duration: {int(duration)} seconds ({int(duration // 60)} minutes, {int(duration % 60)} seconds)
• Video Quality: {stats.get('resolution', 'Unknown')} at {fps:.1f} FPS
• Scene Complexity: {len(scene_changes)} major scene changes detected
• Key Frames Analyzed: {len(key_frames)}

🎯 Content Overview:
Based on analysis of {len(key_frames)} key frames extracted throughout the video:

"""
        
        # Add frame analysis summaries
        if frame_descriptions:
            summary += "📹 Frame-by-Frame Analysis:\n"
            for i, desc in enumerate(frame_descriptions, 1):
                summary += f"  • Key Frame {i}: {desc}\n"
        
        # Determine video type based on characteristics
        summary += "\n📋 Video Type Assessment:\n"
        
        if len(scene_changes) > 10:
            summary += "• MULTI-SCENE CONTENT: This video contains many scene transitions, suggesting edited/compiled content with multiple segments.\n"
        elif len(scene_changes) > 5:
            summary += "• NARRATIVE/FORMATTED: This video has several distinct sections, suggesting well-structured content with clear transitions.\n"
        else:
            summary += "• CONTINUOUS CONTENT: This video is primarily continuous with minimal scene changes, suggesting a focused, single-topic presentation.\n"
        
        # Motion characteristics based on frame analysis
        if frame_descriptions:
            motion_count = sum(1 for desc in frame_descriptions if "High activity" in desc)
            bright_count = sum(1 for desc in frame_descriptions if "Bright" in desc)
            
            if motion_count > len(frame_descriptions) * 0.6:
                summary += "• HIGHLY DYNAMIC: Content with significant movement and activity throughout.\n"
            elif motion_count > len(frame_descriptions) * 0.3:
                summary += "• MIXED PACING: Content with both dynamic and static sections.\n"
            else:
                summary += "• STATIC/STRUCTURED: Content with minimal movement, likely presentation, lecture, or documentary style.\n"
            
            if bright_count > len(frame_descriptions) * 0.7:
                summary += "• WELL-LIT: Professional production with good lighting throughout.\n"
            elif bright_count < len(frame_descriptions) * 0.3:
                summary += "• LOW-LIGHT: Video content with darker scenes or mood-based lighting.\n"
        
        summary += f"\n💡 Key Insights:\n"
        summary += f"• Total Scene Changes Detected: {len(scene_changes)} transitions\n"
        summary += f"• Key Frames for Review: {len(key_frames)} representative moments captured\n"
        summary += f"• Estimated Duration: {int(duration // 60)} minutes {int(duration % 60)} seconds\n"
        summary += f"• Recommended Use: Educational review, content cataloging, and study materials\n"
        
        summary += "\n✨ How to Use This Analysis:\n"
        summary += "• Review the extracted key frames above to understand the content flow\n"
        summary += "• Use 'Generate Text Notes' to create comprehensive study materials\n"
        summary += "• Use 'Generate PDF Notes' for formatted, shareable documentation\n"
        summary += "• Check the scene changes to identify topic transitions\n"
        
        return summary
    
    except Exception as e:
        return f"""
❌ Error Generating AI Summary
═══════════════════════════════════════════════════════════════

Video Analysis encountered an issue: {str(e)}

However, the basic video information is available:
• Duration: {int(stats.get('duration', 0))} seconds
• Resolution: {stats.get('resolution', 'Unknown')}
• FPS: {stats.get('fps', 0):.1f}
• Scene Changes: {len(scene_changes)}
• Key Frames: {len(key_frames)}

✅ Workaround: You can still generate Text and PDF notes using the extracted key frames.
"""


def extract_key_frames(video_path, num_frames=5):
    """
    Extract key frames from a video file
    Returns list of frames and their timestamps
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return None, None
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if total_frames == 0:
        return None, None
    
    # Calculate frame indices to extract
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    
    key_frames = []
    timestamps = []
    
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        
        if ret:
            # Resize frame for display
            frame = cv2.resize(frame, (400, 300))
            key_frames.append(frame)
            
            # Calculate timestamp
            seconds = idx / fps
            timestamp = timedelta(seconds=seconds)
            timestamps.append(str(timestamp).split('.')[0])
    
    cap.release()
    return key_frames, timestamps

def get_video_stats(video_path):
    """
    Extract video statistics like duration, fps, resolution
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return None
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if fps > 0:
        duration = total_frames / fps
    else:
        duration = 0
    
    cap.release()
    
    # Get file size if available
    file_size = "Unknown"
    file_format = "Unknown"
    try:
        if os.path.exists(video_path):
            file_size = f"{os.path.getsize(video_path) / (1024*1024):.2f} MB"
            file_format = os.path.splitext(video_path)[1].upper().strip('.')
    except:
        pass
    
    return {
        'total_frames': total_frames,
        'fps': fps,
        'duration': duration,
        'resolution': f"{width}x{height}",
        'width': width,
        'height': height,
        'file_size': file_size,
        'file_format': file_format
    }

def detect_scene_changes(video_path, threshold=25.0):
    """
    Detect scene changes in video using histogram comparison
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return []
    
    prev_frame = None
    scene_changes = []
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.resize(frame, (320, 240))
        
        if prev_frame is not None:
            # Compare histograms
            hist_curr = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8],
                                    [0, 256, 0, 256, 0, 256])
            hist_prev = cv2.calcHist([prev_frame], [0, 1, 2], None, [8, 8, 8],
                                    [0, 256, 0, 256, 0, 256])
            
            # Normalize histograms
            cv2.normalize(hist_curr, hist_curr)
            cv2.normalize(hist_prev, hist_prev)
            
            # Compare using correlation
            diff = cv2.compareHist(hist_curr, hist_prev, cv2.HISTCMP_BHATTACHARYYA)
            
            if diff > threshold:
                scene_changes.append(frame_count)
        
        prev_frame = frame.copy()
        frame_count += 1
    
    cap.release()
    return scene_changes

def summarize_video(video_path, num_key_frames=5):
    """
    Create a video summary
    """
    key_frames, timestamps = extract_key_frames(video_path, num_key_frames)
    stats = get_video_stats(video_path)
    scene_changes = detect_scene_changes(video_path)
    
    return key_frames, timestamps, stats, scene_changes

def display_video_summary(video_path):
    """
    Display video summary in Streamlit with AI analysis
    """
    st.write("### 🎬 Video Summary")
    
    # Get video stats
    stats = get_video_stats(video_path)
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Duration", f"{int(stats['duration'])}s")
        with col2:
            st.metric("FPS", f"{stats['fps']:.1f}")
        with col3:
            st.metric("Resolution", stats['resolution'])
        with col4:
            st.metric("Total Frames", stats['total_frames'])
    
    st.divider()
    
    # Extract and display key frames
    st.write("### 📸 Key Frames from Video:")
    
    num_frames = st.slider("Number of key frames to extract:", 3, 15, 5)
    
    if st.button("Extract & Analyze Video"):
        with st.spinner("🔍 Analyzing video content..."):
            key_frames, timestamps, _, scene_changes = summarize_video(video_path, num_frames)
            
            if key_frames:
                st.success(f"✅ Extracted {len(key_frames)} key frames")
                
                # Display key frames
                cols = st.columns(3)
                for idx, (frame, timestamp) in enumerate(zip(key_frames, timestamps)):
                    col = cols[idx % 3]
                    with col:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        st.image(frame_rgb, caption=f"Frame at {timestamp}")
                
                st.divider()
                
                # AI-powered content analysis
                st.write("### 🤖 AI-Powered Content Analysis")
                ai_summary = generate_ai_summary(None, stats, key_frames, scene_changes)
                st.text_area("Content Summary:", value=ai_summary, height=400, disabled=True)
                
                st.divider()
                
                # Scene change analysis
                if scene_changes:
                    st.write(f"### 🎪 Scene Changes Detected: {len(scene_changes)}")
                    st.info(f"Scene changes were detected at {len(scene_changes)} points in the video.")
                    
                    if len(scene_changes) <= 20:
                        st.write("**Detected at frame numbers:**")
                        st.write(str(scene_changes[:20]))
                
                # Save summary option
                if st.button("💾 Save AI Analysis Summary"):
                    import json
                    from datetime import datetime
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    summary_data = {
                        'timestamp': timestamp,
                        'duration': stats['duration'],
                        'fps': stats['fps'],
                        'resolution': stats['resolution'],
                        'total_frames': stats['total_frames'],
                        'scene_changes': len(scene_changes),
                        'key_frames_count': len(key_frames),
                        'ai_analysis': ai_summary,
                    }
                    
                    filename = f"video_analysis_{timestamp}.json"
                    with open(filename, 'w') as f:
                        json.dump(summary_data, f, indent=2)
                    
                    st.success(f"✅ Analysis saved as {filename}")
            else:
                st.error("❌ Could not extract frames from video")

def video_summarizer_page():
    """
    Main video summarizer page with direct (non-background) analysis
    """
    # Initialize session state keys safely
    if 'progress' not in st.session_state:
        st.session_state.progress = {'analysis_complete': False}

    # Initialize placeholders for status updates
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    st.write("### 🎥 Video Summarizer & Study Notes Generator")
    st.write("Upload a video to analyze it and generate study notes")
    
    uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'])
    
    if uploaded_file is not None:
        # Save uploaded file
        video_path = f"temp_video_{uploaded_file.name}"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.divider()
        
        # Analysis settings
        st.write("### ⚙️ Analysis Settings")
        num_frames = st.slider("Number of key frames to extract:", 3, 15, 5)
        
        # Analyze button
        if st.button("🚀 Analyze Video", type="primary", use_container_width=True):
            with st.spinner("🔍 Analyzing video... This may take a moment"):
                try:
                    # Perform analysis
                    key_frames, timestamps, stats, scene_changes = summarize_video(video_path, num_frames)
                    
                    if key_frames and stats:
                        st.session_state.video_analysis = {
                            'key_frames': key_frames,
                            'timestamps': timestamps,
                            'stats': stats,
                            'scene_changes': scene_changes,
                            'video_path': video_path,
                            'video_name': uploaded_file.name.split('.')[0]
                        }
                        st.success("✅ Video analysis complete!")
                    else:
                        st.error("❌ Could not analyze video. Please try a different file.")
                        
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
        
        st.divider()
        
        # Display results if analysis was successful
        if 'video_analysis' in st.session_state:
            analysis = st.session_state.video_analysis
            key_frames = analysis['key_frames']
            timestamps = analysis['timestamps']
            stats = analysis['stats']
            scene_changes = analysis['scene_changes']
            
            # Display video
            st.write("### 📹 Video Player")
            st.video(uploaded_file)
            
            st.divider()
            
            # Video statistics
            st.write("### 📈 Video Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Duration", f"{int(stats['duration'])}s ({int(stats['duration']//60)}m)")
            with col2:
                st.metric("FPS", f"{stats['fps']:.1f}")
            with col3:
                st.metric("Resolution", stats['resolution'])
            with col4:
                st.metric("Total Frames", f"{stats['total_frames']:,}")
            
            st.divider()
            
            # Key frames
            st.write("### 📸 Extracted Key Frames")
            cols = st.columns(3)
            for idx, (frame, timestamp) in enumerate(zip(key_frames, timestamps)):
                col = cols[idx % 3]
                with col:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.image(frame_rgb, caption=f"Frame at {timestamp}", use_column_width=True)
            
            st.divider()
            
            # Scene changes
            st.write("### 🎪 Scene Changes Analysis")
            st.info(f"📍 {len(scene_changes)} scene changes detected in this video")
            if scene_changes and len(scene_changes) <= 50:
                st.write("**Detected at frame numbers:**")
                st.code(str(scene_changes[:50]))
            
            st.divider()
            
            # AI Content Summary
            st.write("### 🤖 AI-Powered Content Summary")
            ai_summary = generate_ai_summary(None, stats, key_frames, scene_changes)
            st.text_area("Video Content Analysis:", value=ai_summary, height=350, disabled=True)
            
            st.divider()
            
            # Notes Generation Section
            st.write("### 📚 Generate Study Notes")
            st.info("💡 Create and save educational notes from this video analysis")
            
            col1, col2 = st.columns(2)
            
            # Text Notes
            with col1:
                st.write("#### 📄 Text Notes")
                if st.button("📝 Generate Text Notes (.txt)", use_container_width=True, key="gen_txt"):
                    try:
                        text_file = save_notes_as_text(
                            analysis['video_name'],
                            stats,
                            len(key_frames),
                            len(scene_changes)
                        )
                        
                        with open(text_file, 'r', encoding='utf-8') as f:
                            notes_content = f.read()
                        
                        st.success(f"✅ Text notes created: {text_file}")
                        
                        # Show preview
                        st.text_area("Preview:", value=notes_content[:1500] + "\n\n... (full file saved)", height=300, disabled=True)
                        
                        # Download button
                        st.download_button(
                            label="⬇️ Download Text File",
                            data=notes_content,
                            file_name=text_file,
                            mime="text/plain",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            # PDF Notes
            with col2:
                st.write("#### 📕 PDF Notes")
                if st.button("📕 Generate PDF Notes (.pdf)", use_container_width=True, key="gen_pdf"):
                    try:
                        pdf_file = save_notes_as_pdf(
                            analysis['video_name'],
                            stats,
                            len(key_frames),
                            len(scene_changes)
                        )
                        
                        with open(pdf_file, 'rb') as f:
                            pdf_data = f.read()
                        
                        st.success(f"✅ PDF notes created: {pdf_file}")
                        
                        # Download button
                        st.download_button(
                            label="⬇️ Download PDF File",
                            data=pdf_data,
                            file_name=pdf_file,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            st.divider()
            
            # Additional options
            st.write("### 💾 Save Analysis Summary")
            if st.button("Save as JSON", use_container_width=True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                summary_data = {
                    'timestamp': timestamp,
                    'video_name': analysis['video_name'],
                    'duration': stats['duration'],
                    'fps': stats['fps'],
                    'resolution': stats['resolution'],
                    'total_frames': stats['total_frames'],
                    'scene_changes_count': len(scene_changes),
                    'key_frames_extracted': len(key_frames),
                }
                
                filename = f"video_analysis_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(summary_data, f, indent=2)
                
                st.success(f"✅ Analysis saved as {filename}")
                
                import time
                time.sleep(2)  # Poll every 2 seconds instead of continuous rerun
                max_wait += 2
            
            # If analysis completed, trigger a single rerun to show results
            progress_state = st.session_state.get('progress', {})
            if progress_state.get('analysis_complete'):
                if 'progress_placeholder' in locals():
                    progress_placeholder.empty()
                if 'status_placeholder' in locals():
                    status_placeholder.empty()
                st.rerun()
        
        else:
            st.info("💡 Click 'Start Background Analysis' button to begin analysis while video plays!")
        
        # Cleanup
        try:
            os.remove(video_path)
        except:
            pass

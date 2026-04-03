import streamlit as st
from datetime import datetime
import json
import os

class GestureNotesManager:
    """
    Manage notes created through gesture commands during video/gesture control
    """
    
    SESSION_KEY = "gesture_notes"
    
    @staticmethod
    def initialize():
        """Initialize notes session state"""
        if GestureNotesManager.SESSION_KEY not in st.session_state:
            st.session_state[GestureNotesManager.SESSION_KEY] = {
                'notes': [],
                'current_note': "",
                'is_recording': False,
                'start_time': None
            }
    
    @staticmethod
    def add_note(gesture_label, action, timestamp=None):
        """Add a note triggered by a gesture"""
        GestureNotesManager.initialize()
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        note_entry = {
            'timestamp': timestamp,
            'gesture': gesture_label,
            'action': action,
            'created_at': datetime.now().isoformat()
        }
        
        st.session_state[GestureNotesManager.SESSION_KEY]['notes'].append(note_entry)
        return note_entry
    
    @staticmethod
    def start_recording_note(gesture_label):
        """Start recording notes for a specific gesture"""
        GestureNotesManager.initialize()
        st.session_state[GestureNotesManager.SESSION_KEY]['is_recording'] = True
        st.session_state[GestureNotesManager.SESSION_KEY]['current_gesture'] = gesture_label
        st.session_state[GestureNotesManager.SESSION_KEY]['start_time'] = datetime.now()
    
    @staticmethod
    def stop_recording_note(note_text):
        """Stop recording and save the note"""
        GestureNotesManager.initialize()
        
        if st.session_state[GestureNotesManager.SESSION_KEY]['is_recording']:
            timestamp = datetime.now().strftime("%H:%M:%S")
            gesture = st.session_state[GestureNotesManager.SESSION_KEY].get('current_gesture', 'Unknown')
            
            note_entry = {
                'timestamp': timestamp,
                'gesture': gesture,
                'note_text': note_text,
                'created_at': datetime.now().isoformat()
            }
            
            st.session_state[GestureNotesManager.SESSION_KEY]['notes'].append(note_entry)
            st.session_state[GestureNotesManager.SESSION_KEY]['is_recording'] = False
            st.session_state[GestureNotesManager.SESSION_KEY]['current_note'] = ""
            
            return note_entry
        
        return None
    
    @staticmethod
    def get_all_notes():
        """Get all notes collected"""
        GestureNotesManager.initialize()
        return st.session_state[GestureNotesManager.SESSION_KEY]['notes']
    
    @staticmethod
    def get_notes_text():
        """Get formatted text of all notes"""
        GestureNotesManager.initialize()
        notes = st.session_state[GestureNotesManager.SESSION_KEY]['notes']
        
        if not notes:
            return ""
        
        text = "GESTURE CONTROL SESSION NOTES\n"
        text += "=" * 50 + "\n"
        text += f"Session Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += "=" * 50 + "\n\n"
        
        for i, note in enumerate(notes, 1):
            text += f"{i}. [{note.get('timestamp', 'N/A')}] "
            text += f"Gesture: {note.get('gesture', 'Unknown')}\n"
            
            if 'note_text' in note:
                text += f"   Note: {note['note_text']}\n"
            else:
                text += f"   Action: {note.get('action', 'Unknown')}\n"
            
            text += "\n"
        
        return text
    
    @staticmethod
    def save_notes_as_file(filename=None):
        """Save all notes to a file"""
        GestureNotesManager.initialize()
        
        if filename is None:
            filename = f"gesture_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        notes_text = GestureNotesManager.get_notes_text()
        
        if notes_text:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(notes_text)
            
            return filename
        
        return None
    
    @staticmethod
    def save_notes_as_json(filename=None):
        """Save all notes as JSON"""
        GestureNotesManager.initialize()
        
        if filename is None:
            filename = f"gesture_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        notes = st.session_state[GestureNotesManager.SESSION_KEY]['notes']
        
        if notes:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(notes, f, indent=2, ensure_ascii=False)
            
            return filename
        
        return None
    
    @staticmethod
    def clear_notes():
        """Clear all notes"""
        GestureNotesManager.initialize()
        st.session_state[GestureNotesManager.SESSION_KEY] = {
            'notes': [],
            'current_note': "",
            'is_recording': False,
            'start_time': None
        }
    
    @staticmethod
    def display_notes():
        """Display collected notes in UI"""
        GestureNotesManager.initialize()
        notes = GestureNotesManager.get_all_notes()
        
        if not notes:
            st.info("No notes recorded yet. Use gestures or the note panel to add notes.")
            return
        
        st.write(f"### 📝 Notes ({len(notes)} entries)")
        
        # Display notes in expandable sections
        for i, note in enumerate(notes, 1):
            with st.expander(f"Note {i} - {note.get('timestamp', 'N/A')} - {note.get('gesture', 'Unknown')}"):
                st.write(f"**Gesture**: {note.get('gesture', 'Unknown')}")
                st.write(f"**Time**: {note.get('timestamp', 'N/A')}")
                
                if 'note_text' in note:
                    st.write(f"**Content**: {note['note_text']}")
                else:
                    st.write(f"**Action**: {note.get('action', 'Unknown')}")

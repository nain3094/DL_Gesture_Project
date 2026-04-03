import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

class VideoNotesGenerator:
    """
    Generate educational notes from video analysis data
    """
    
    def __init__(self, video_name, stats, key_frames_count, scene_changes_count):
        self.video_name = video_name
        self.stats = stats
        self.key_frames_count = key_frames_count
        self.scene_changes_count = scene_changes_count
        self.timestamp = datetime.now()
    
    def generate_text_notes(self):
        """
        Generate plain text notes from video data
        """
        notes = f"""
═══════════════════════════════════════════════════════════════
                    VIDEO SUMMARY NOTES
═══════════════════════════════════════════════════════════════

Video: {self.video_name}
Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
───────────────────────────────────────────────────────────────

📹 VIDEO INFORMATION
═══════════════════════════════════════════════════════════════
Duration:           {int(self.stats.get('duration', 0))} seconds ({int(self.stats.get('duration', 0) // 60)} min {int(self.stats.get('duration', 0) % 60)} sec)
Frame Rate (FPS):   {self.stats.get('fps', 0):.1f} fps
Resolution:         {self.stats.get('resolution', 'Unknown')}
Total Frames:       {self.stats.get('total_frames', 0)}
File Size:          {self.stats.get('file_size', 'Unknown')}

───────────────────────────────────────────────────────────────

📊 CONTENT ANALYSIS
═══════════════════════════════════════════════════════════════
Key Frames Extracted:  {self.key_frames_count}
Scene Changes:         {self.scene_changes_count}

───────────────────────────────────────────────────────────────

🎓 KEY OBSERVATIONS
═══════════════════════════════════════════════════════════════

1. Video Duration & Pace:
   This video is {int(self.stats.get('duration', 0))} seconds long, which is suitable for 
   {self._get_duration_category(self.stats.get('duration', 0))} learning sessions.
   
   Frame rate of {self.stats.get('fps', 0):.1f} fps provides 
   {"smooth" if self.stats.get('fps', 0) >= 24 else "standard"} playback quality.

2. Visual Content Structure:
   {self.scene_changes_count} scene changes detected indicates 
   {self._get_scene_change_description(self.scene_changes_count)}.
   
   Extracted {self.key_frames_count} key frames representing the most important visual moments.

3. Content Characteristics:
   - Resolution: {self.stats.get('resolution', 'Unknown')} pixels
   - Total frames: {self.stats.get('total_frames', 0)}
   - Average scene length: {self._calculate_avg_scene_length()} seconds

───────────────────────────────────────────────────────────────

📝 STUDY NOTES TEMPLATE
═══════════════════════════════════════════════════════════════

Topic/Subject: ___________________________________________________

Main Concepts Covered:
□ Concept 1: _____________________________________________________
□ Concept 2: _____________________________________________________
□ Concept 3: _____________________________________________________

Key Points:
1. ________________________________________________________________
2. ________________________________________________________________
3. ________________________________________________________________
4. ________________________________________________________________
5. ________________________________________________________________

Important Definitions:
- Term 1: _________________________________________________________
- Term 2: _________________________________________________________
- Term 3: _________________________________________________________

Questions to Answer:
Q1: What is the main idea of this video?
A: _________________________________________________________________

Q2: What are the key takeaways?
A: _________________________________________________________________

Q3: How can this be applied in practice?
A: _________________________________________________________________

───────────────────────────────────────────────────────────────

✅ LEARNING CHECKLIST
═══════════════════════════════════════════════════════════════

After watching this video, you should be able to:
☐ Understand the main concepts
☐ Explain key ideas to someone else
☐ Apply the knowledge to real-world situations
☐ Recall at least 3 main points
☐ Complete related exercises or assignments

───────────────────────────────────────────────────────────────

📋 SUMMARY
═══════════════════════════════════════════════════════════════

This video provides {self._get_content_type()} content that is approximately
{int(self.stats.get('duration', 0))} seconds ({int(self.stats.get('duration', 0) // 60)} minutes) in length.
With {self.scene_changes_count} scene transitions and {self.key_frames_count} key visual moments,
it presents information in a segmented, potentially easy-to-follow format.

Recommended viewing: Watch in focused intervals with note-taking.
Review: Return to key frames for reinforcement learning.

───────────────────────────────────────────────────────────────
Generated: {self.timestamp.strftime('%Y-%m-%d at %H:%M:%S')}
═══════════════════════════════════════════════════════════════
"""
        return notes
    
    def generate_pdf_notes(self, output_filename=None):
        """
        Generate PDF notes from video data
        """
        if output_filename is None:
            output_filename = f"video_notes_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(output_filename, pagesize=letter,
                               rightMargin=0.5*inch, leftMargin=0.5*inch,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        )
        
        # Title
        elements.append(Paragraph("📹 VIDEO SUMMARY NOTES", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Metadata
        metadata_text = f"""
        <b>Video:</b> {self.video_name}<br/>
        <b>Generated:</b> {self.timestamp.strftime('%B %d, %Y at %H:%M:%S')}
        """
        elements.append(Paragraph(metadata_text, body_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Video Information Section
        elements.append(Paragraph("📹 VIDEO INFORMATION", heading_style))
        
        video_data = [
            ['Metric', 'Value'],
            ['Duration', f"{int(self.stats.get('duration', 0))} seconds ({int(self.stats.get('duration', 0) // 60)} min {int(self.stats.get('duration', 0) % 60)} sec)"],
            ['Frame Rate (FPS)', f"{self.stats.get('fps', 0):.1f} fps"],
            ['Resolution', self.stats.get('resolution', 'Unknown')],
            ['Total Frames', str(self.stats.get('total_frames', 0))],
        ]
        
        video_table = Table(video_data, colWidths=[2*inch, 3*inch])
        video_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(video_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Content Analysis
        elements.append(Paragraph("📊 CONTENT ANALYSIS", heading_style))
        analysis_text = f"""
        <b>Key Frames Extracted:</b> {self.key_frames_count}<br/>
        <b>Scene Changes Detected:</b> {self.scene_changes_count}<br/>
        <b>Average Scene Length:</b> {self._calculate_avg_scene_length()} seconds
        """
        elements.append(Paragraph(analysis_text, body_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key Observations
        elements.append(Paragraph("🎓 KEY OBSERVATIONS", heading_style))
        
        observations = f"""
        <b>1. Video Duration & Pace:</b><br/>
        This {int(self.stats.get('duration', 0))}-second video is suitable for 
        {self._get_duration_category(self.stats.get('duration', 0))} learning sessions. 
        The {self.stats.get('fps', 0):.1f} fps frame rate provides smooth playback quality.
        <br/><br/>
        
        <b>2. Visual Content Structure:</b><br/>
        The {self.scene_changes_count} detected scene changes indicate 
        {self._get_scene_change_description(self.scene_changes_count)}.
        {self.key_frames_count} key frames were extracted as the most visually significant moments.
        <br/><br/>
        
        <b>3. Content Characteristics:</b><br/>
        • Resolution: {self.stats.get('resolution', 'Unknown')}<br/>
        • Total Frames: {self.stats.get('total_frames', 0)}<br/>
        • File Format: {self.stats.get('file_format', 'Unknown')}<br/>
        """
        elements.append(Paragraph(observations, body_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Study Template Section
        elements.append(PageBreak())
        elements.append(Paragraph("📝 STUDY NOTES TEMPLATE", heading_style))
        
        template_text = """
        <b>Topic/Subject:</b> _____________________________________________<br/><br/>
        
        <b>Main Concepts Covered:</b><br/>
        ☐ Concept 1: ____________________________________________________<br/>
        ☐ Concept 2: ____________________________________________________<br/>
        ☐ Concept 3: ____________________________________________________<br/><br/>
        
        <b>Key Points:</b><br/>
        1. ________________________________________________________________<br/>
        2. ________________________________________________________________<br/>
        3. ________________________________________________________________<br/><br/>
        
        <b>Important Definitions:</b><br/>
        Term 1: __________________________________________________________<br/>
        Term 2: __________________________________________________________<br/>
        """
        elements.append(Paragraph(template_text, body_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Learning Checklist
        elements.append(Paragraph("✅ LEARNING CHECKLIST", heading_style))
        checklist_text = """
        After watching this video, you should be able to:<br/>
        ☐ Understand the main concepts<br/>
        ☐ Explain key ideas to someone else<br/>
        ☐ Apply the knowledge to real-world situations<br/>
        ☐ Recall at least 3 main points<br/>
        ☐ Complete related exercises or assignments<br/>
        """
        elements.append(Paragraph(checklist_text, body_style))
        
        # Build PDF
        doc.build(elements)
        return output_filename
    
    def _get_duration_category(self, duration):
        """Categorize video by duration"""
        if duration < 60:
            return "quick reference"
        elif duration < 300:  # 5 minutes
            return "short focused"
        elif duration < 600:  # 10 minutes
            return "medium-length"
        else:
            return "comprehensive"
    
    def _get_scene_change_description(self, count):
        """Describe scene changes"""
        if count == 0:
            return "a continuous narrative with minimal transitions"
        elif count < 5:
            return "a simple structure with a few key transitions"
        elif count < 15:
            return "a moderately segmented content with multiple topics"
        else:
            return "a highly segmented content with many scene transitions"
    
    def _calculate_avg_scene_length(self):
        """Calculate average scene length"""
        if self.scene_changes_count == 0:
            return int(self.stats.get('duration', 0))
        return int(self.stats.get('duration', 0) / (self.scene_changes_count + 1))
    
    def _get_content_type(self):
        """Determine content type based on statistics"""
        fps = self.stats.get('fps', 0)
        duration = self.stats.get('duration', 0)
        
        if self.scene_changes_count > duration / 10:
            return "fast-paced, segmented educational"
        elif self.scene_changes_count > duration / 30:
            return "medium-paced educational"
        else:
            return "continuous narrative"


def save_notes_as_text(video_name, stats, key_frames_count, scene_changes_count, output_filename=None):
    """
    Helper function to save notes as text file
    """
    generator = VideoNotesGenerator(video_name, stats, key_frames_count, scene_changes_count)
    notes = generator.generate_text_notes()
    
    if output_filename is None:
        output_filename = f"video_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(notes)
    
    return output_filename


def save_notes_as_pdf(video_name, stats, key_frames_count, scene_changes_count, output_filename=None):
    """
    Helper function to save notes as PDF file
    """
    generator = VideoNotesGenerator(video_name, stats, key_frames_count, scene_changes_count)
    return generator.generate_pdf_notes(output_filename)

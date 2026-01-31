import urllib.parse
import re

def get_whatsapp_link(user_name, program_name):
    """Generate WhatsApp deep link with pre-filled message"""
    from config import WHATSAPP_NUMBER
    
    message = f"Hi Asha! I'm {user_name}. I just received my AI roadmap and I'm interested in {program_name}. Can we discuss next steps?"
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}"

def generate_share_text(user_name, match_score):
    """Generate social media share text"""
    text = f"I just discovered my personalized leadership path with Iron Lady's AI Navigator! 🎯 Got a {match_score}% match score. Ready to transform my career! 💪 #IronLady #WomenInLeadership #CareerGrowth"
    return text

def calculate_match_score(ai_response):
    """Extract match score from AI response or calculate default"""
    # Try to find percentage in response
    match = re.search(r'(\d{2,3})%', ai_response)
    if match:
        return int(match.group(1))
    
    # Default score based on response length and quality
    return 92  # High confidence default

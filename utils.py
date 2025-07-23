import streamlit as st
import hashlib
import uuid
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import base64
from io import BytesIO
from PIL import Image
import requests

def load_css():
    """Load custom CSS for the application"""
    css = """
    <style>
    /* Global Styles */
    .main-header {
        background: linear-gradient(135deg, #1A73E8, #34A853);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    
    /* News Card Styles */
    .news-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #1A73E8;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .news-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .news-card-title {
        font-size: 18px;
        font-weight: 600;
        color: #202124;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    
    .news-card-summary {
        color: #5f6368;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 16px;
    }
    
    .news-card-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: #80868b;
    }
    
    .news-card-source {
        font-weight: 500;
    }
    
    .news-card-time {
        font-style: italic;
    }
    
    /* Color Psychology Classes */
    .breaking { border-left-color: #EA4335 !important; }
    .politics { border-left-color: #FF9800 !important; }
    .business { border-left-color: #1A73E8 !important; }
    .technology { border-left-color: #34A853 !important; }
    .sports { border-left-color: #FBBC04 !important; }
    .entertainment { border-left-color: #FF6D01 !important; }
    .health { border-left-color: #9C27B0 !important; }
    .science { border-left-color: #00BCD4 !important; }
    .positive { border-left-color: #4CAF50 !important; }
    .neutral { border-left-color: #757575 !important; }
    
    /* Urgency Animations */
    .urgency-high {
        animation: pulse 2s infinite;
        border-left-color: #FF0000 !important;
    }
    
    .urgency-medium {
        animation: glow 3s ease-in-out infinite;
        border-left-color: #FF6600 !important;
    }
    
    @keyframes pulse {
        0% { border-left-color: #FF0000; }
        50% { border-left-color: #FF4444; }
        100% { border-left-color: #FF0000; }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(255, 102, 0, 0.5); }
        50% { box-shadow: 0 0 20px rgba(255, 102, 0, 0.8); }
    }
    
    /* Dashboard Styles */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #1A73E8;
        margin-bottom: 8px;
    }
    
    .metric-label {
        font-size: 14px;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Navigation Styles */
    .nav-button {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px 20px;
        margin: 4px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .nav-button:hover {
        background: #e8f0fe;
        border-color: #1A73E8;
    }
    
    .nav-button.active {
        background: #1A73E8;
        color: white;
        border-color: #1A73E8;
    }
    
    /* Form Styles */
    .form-container {
        background: white;
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Status Indicators */
    .status-active { color: #34A853; }
    .status-pending { color: #FBBC04; }
    .status-inactive { color: #EA4335; }
    .status-warning { color: #FF9800; }
    
    /* Profile Styles */
    .profile-header {
        background: linear-gradient(135deg, #1A73E8, #34A853);
        color: white;
        padding: 32px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 24px;
    }
    
    .profile-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 4px solid white;
        margin-bottom: 16px;
    }
    
    /* Advertisement Styles */
    .advertisement-container {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        background: #f8f9fa;
        position: relative;
    }
    
    .ad-label {
        position: absolute;
        top: 4px;
        right: 4px;
        font-size: 10px;
        color: #666;
        background: #fff;
        padding: 2px 4px;
        border-radius: 2px;
    }
    
    /* Theme Selector Styles */
    .theme-preview {
        border: 2px solid transparent;
        border-radius: 8px;
        padding: 16px;
        margin: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .theme-preview:hover {
        border-color: #1A73E8;
    }
    
    .theme-preview.selected {
        border-color: #1A73E8;
        background: #e8f0fe;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .news-card {
            margin: 12px 0;
            padding: 16px;
        }
        
        .news-card-title {
            font-size: 16px;
        }
        
        .metric-card {
            padding: 16px;
        }
        
        .metric-value {
            font-size: 24px;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def generate_session_id() -> str:
    """Generate unique session ID"""
    return str(uuid.uuid4())

def hash_string(text: str) -> str:
    """Generate SHA-256 hash of string"""
    return hashlib.sha256(text.encode()).hexdigest()

def safe_execute(func, *args, **kwargs) -> Any:
    """Safely execute function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"Error executing function {func.__name__}: {str(e)}")
        return None

def format_number(num: float, decimals: int = 2) -> str:
    """Format number with proper comma separators"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.{decimals}f}M"
    elif num >= 1_000:
        return f"{num/1_000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_date(date_obj: datetime, format_type: str = "short") -> str:
    """Format datetime object to string"""
    if not date_obj:
        return "N/A"
    
    if format_type == "short":
        return date_obj.strftime("%m/%d/%Y")
    elif format_type == "long":
        return date_obj.strftime("%B %d, %Y at %I:%M %p")
    elif format_type == "time_ago":
        return get_time_ago(date_obj)
    else:
        return date_obj.strftime(format_type)

def get_time_ago(date_obj: datetime) -> str:
    """Get human-readable time ago string"""
    if not date_obj:
        return "Unknown"
    
    now = datetime.now()
    if date_obj.tzinfo:
        now = now.replace(tzinfo=date_obj.tzinfo)
    
    diff = now - date_obj
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return re.match(pattern, url) is not None

def sanitize_html(text: str) -> str:
    """Remove HTML tags from text"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction - remove stop words and get most frequent
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'shall', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]

def generate_color_palette(base_color: str) -> Dict[str, str]:
    """Generate color palette from base color"""
    # Simple color palette generation
    return {
        "primary": base_color,
        "secondary": lighten_color(base_color, 0.3),
        "accent": darken_color(base_color, 0.2),
        "background": lighten_color(base_color, 0.9),
        "text": "#333333",
        "border": lighten_color(base_color, 0.7)
    }

def lighten_color(hex_color: str, factor: float = 0.3) -> str:
    """Lighten a hex color"""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def darken_color(hex_color: str, factor: float = 0.3) -> str:
    """Darken a hex color"""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def create_download_link(data: str, filename: str, link_text: str) -> str:
    """Create download link for data"""
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def compress_image(image: Image.Image, quality: int = 85) -> bytes:
    """Compress PIL Image to bytes"""
    output = BytesIO()
    image.save(output, format='JPEG', quality=quality, optimize=True)
    return output.getvalue()

def resize_image(image: Image.Image, max_size: tuple = (800, 600)) -> Image.Image:
    """Resize image maintaining aspect ratio"""
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image

def generate_avatar(name: str, size: int = 80) -> str:
    """Generate avatar URL from name"""
    # Use a service like DiceBear or similar
    initial = name[0].upper() if name else "?"
    color = hash_string(name)[:6]  # Use hash for consistent color
    
    # Simple SVG avatar
    svg = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
        <circle cx="{size//2}" cy="{size//2}" r="{size//2}" fill="#{color}"/>
        <text x="{size//2}" y="{size//2 + 8}" text-anchor="middle" fill="white" font-size="{size//3}" font-family="Arial, sans-serif">{initial}</text>
    </svg>
    """
    
    return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes"""
    word_count = len(text.split())
    reading_time = max(1, round(word_count / words_per_minute))
    return reading_time

def generate_excerpt(text: str, sentence_count: int = 2) -> str:
    """Generate excerpt from text"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= sentence_count:
        return text
    
    return '. '.join(sentences[:sentence_count]) + '.'

def parse_json_safely(json_string: str) -> Optional[Dict]:
    """Safely parse JSON string"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None

def merge_dictionaries(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def remove_duplicates(lst: List, key_func=None) -> List:
    """Remove duplicates from list"""
    if key_func:
        seen = set()
        result = []
        for item in lst:
            key = key_func(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result
    else:
        return list(dict.fromkeys(lst))

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''

def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'}
    return get_file_extension(filename) in image_extensions

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def create_breadcrumb(path_parts: List[str], separator: str = " > ") -> str:
    """Create breadcrumb navigation string"""
    return separator.join(path_parts)

def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Simple phone validation - accepts various formats
    cleaned = re.sub(r'[^\d+]', '', phone)
    return len(cleaned) >= 10 and len(cleaned) <= 15

def format_phone(phone: str) -> str:
    """Format phone number for display"""
    # Simple US phone formatting
    cleaned = re.sub(r'[^\d]', '', phone)
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    elif len(cleaned) == 11 and cleaned[0] == '1':
        return f"+1 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
    else:
        return phone

def get_client_ip() -> str:
    """Get client IP address (for analytics)"""
    # In a real deployment, this would get the actual client IP
    # For now, return a placeholder
    return "127.0.0.1"

def create_pagination(total_items: int, items_per_page: int, current_page: int) -> Dict:
    """Create pagination information"""
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    return {
        "current_page": current_page,
        "total_pages": total_pages,
        "items_per_page": items_per_page,
        "total_items": total_items,
        "start_item": (current_page - 1) * items_per_page + 1,
        "end_item": min(current_page * items_per_page, total_items),
        "has_previous": current_page > 1,
        "has_next": current_page < total_pages,
        "previous_page": current_page - 1 if current_page > 1 else None,
        "next_page": current_page + 1 if current_page < total_pages else None
    }

def render_pagination(pagination_info: Dict) -> None:
    """Render pagination controls in Streamlit"""
    if pagination_info["total_pages"] <= 1:
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if pagination_info["has_previous"]:
            if st.button("◀ Previous"):
                st.session_state.current_page = pagination_info["previous_page"]
                st.rerun()
    
    with col2:
        st.write(f"Page {pagination_info['current_page']}")
    
    with col3:
        st.write(f"of {pagination_info['total_pages']}")
    
    with col4:
        page_input = st.number_input("Go to page", 
                                   min_value=1, 
                                   max_value=pagination_info["total_pages"],
                                   value=pagination_info["current_page"],
                                   key="page_input")
        if page_input != pagination_info["current_page"]:
            st.session_state.current_page = page_input
            st.rerun()
    
    with col5:
        if pagination_info["has_next"]:
            if st.button("Next ▶"):
                st.session_state.current_page = pagination_info["next_page"]
                st.rerun()

def create_progress_bar(current: int, total: int, prefix: str = "", suffix: str = "") -> str:
    """Create ASCII progress bar"""
    percent = current / total if total > 0 else 0
    bar_length = 20
    filled_length = int(bar_length * percent)
    
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    return f"{prefix} |{bar}| {percent:.1%} {suffix}"

def debounce_function(wait_time: float):
    """Decorator to debounce function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Simple debouncing using session state
            key = f"debounce_{func.__name__}"
            current_time = datetime.now()
            
            if key in st.session_state:
                last_call = st.session_state[key]
                if (current_time - last_call).total_seconds() < wait_time:
                    return None
            
            st.session_state[key] = current_time
            return func(*args, **kwargs)
        return wrapper
    return decorator

def cache_with_expiry(expiry_minutes: int = 60):
    """Simple caching decorator with expiry"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"cache_{func.__name__}_{hash(str(args) + str(kwargs))}"
            current_time = datetime.now()
            
            # Check if cached result exists and is not expired
            if cache_key in st.session_state:
                cached_data, cached_time = st.session_state[cache_key]
                if (current_time - cached_time).total_seconds() < expiry_minutes * 60:
                    return cached_data
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            st.session_state[cache_key] = (result, current_time)
            return result
        return wrapper
    return decorator

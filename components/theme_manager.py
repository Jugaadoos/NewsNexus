import streamlit as st
import json
from typing import Dict, Optional
import colorsys

from ai_services import generate_theme
from database import update_user_preferences, get_user_preferences
from auth import get_current_user
from utils import lighten_color, darken_color, generate_color_palette

class ThemeManager:
    def __init__(self):
        self.predefined_themes = {
            "Default": {
                "primary_color": "#1A73E8",
                "secondary_color": "#34A853", 
                "background_color": "#F8F9FA",
                "text_color": "#202124",
                "accent_color": "#EA4335",
                "card_background": "#FFFFFF",
                "border_color": "#E0E0E0",
                "theme_name": "Default",
                "description": "Clean and modern default theme"
            },
            "Dark Mode": {
                "primary_color": "#BB86FC",
                "secondary_color": "#03DAC6",
                "background_color": "#121212",
                "text_color": "#FFFFFF",
                "accent_color": "#CF6679",
                "card_background": "#1E1E1E",
                "border_color": "#333333",
                "theme_name": "Dark Mode",
                "description": "Dark theme for comfortable night reading"
            },
            "Ocean Blue": {
                "primary_color": "#0277BD",
                "secondary_color": "#00ACC1",
                "background_color": "#E0F2F1",
                "text_color": "#004D40",
                "accent_color": "#00BCD4",
                "card_background": "#FFFFFF",
                "border_color": "#B2DFDB",
                "theme_name": "Ocean Blue",
                "description": "Calming ocean-inspired blue theme"
            },
            "Forest Green": {
                "primary_color": "#2E7D32",
                "secondary_color": "#66BB6A",
                "background_color": "#E8F5E9",
                "text_color": "#1B5E20",
                "accent_color": "#4CAF50",
                "card_background": "#FFFFFF",
                "border_color": "#C8E6C9",
                "theme_name": "Forest Green",
                "description": "Natural forest-inspired green theme"
            },
            "Sunset Orange": {
                "primary_color": "#F57C00",
                "secondary_color": "#FF9800",
                "background_color": "#FFF8E1",
                "text_color": "#E65100",
                "accent_color": "#FF5722",
                "card_background": "#FFFFFF",
                "border_color": "#FFCC02",
                "theme_name": "Sunset Orange",
                "description": "Warm sunset-inspired orange theme"
            },
            "Royal Purple": {
                "primary_color": "#6A1B9A",
                "secondary_color": "#AB47BC",
                "background_color": "#F3E5F5",
                "text_color": "#4A148C",
                "accent_color": "#E91E63",
                "card_background": "#FFFFFF",
                "border_color": "#CE93D8",
                "theme_name": "Royal Purple",
                "description": "Elegant royal purple theme"
            },
            "Minimalist": {
                "primary_color": "#424242",
                "secondary_color": "#757575",
                "background_color": "#FAFAFA",
                "text_color": "#212121",
                "accent_color": "#FF6F00",
                "card_background": "#FFFFFF",
                "border_color": "#E0E0E0",
                "theme_name": "Minimalist",
                "description": "Clean minimalist gray theme"
            }
        }
    
    def get_current_theme(self, user_id: int) -> Dict:
        """Get current theme for user"""
        preferences = get_user_preferences(user_id)
        theme_data = preferences.get('theme_data')
        
        if theme_data and isinstance(theme_data, dict):
            return theme_data
        
        # Return default theme if no custom theme
        return self.predefined_themes["Default"]
    
    def apply_theme(self, user_id: int, theme_data: Dict) -> bool:
        """Apply theme to user preferences"""
        try:
            preferences = get_user_preferences(user_id)
            preferences['theme_data'] = theme_data
            preferences['theme_name'] = theme_data.get('theme_name', 'Custom')
            
            return update_user_preferences(user_id, preferences)
        except Exception as e:
            st.error(f"Error applying theme: {e}")
            return False
    
    def generate_css(self, theme_data: Dict) -> str:
        """Generate CSS from theme data"""
        css = f"""
        <style>
        :root {{
            --primary-color: {theme_data.get('primary_color', '#1A73E8')};
            --secondary-color: {theme_data.get('secondary_color', '#34A853')};
            --background-color: {theme_data.get('background_color', '#F8F9FA')};
            --text-color: {theme_data.get('text_color', '#202124')};
            --accent-color: {theme_data.get('accent_color', '#EA4335')};
            --card-background: {theme_data.get('card_background', '#FFFFFF')};
            --border-color: {theme_data.get('border_color', '#E0E0E0')};
        }}
        
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
        }}
        
        .news-card {{
            background: var(--card-background);
            border-left-color: var(--primary-color);
            color: var(--text-color);
        }}
        
        .news-card-title {{
            color: var(--text-color);
        }}
        
        .metric-card {{
            background: var(--card-background);
            border-color: var(--border-color);
        }}
        
        .stButton > button {{
            background-color: var(--primary-color);
            color: white;
            border: none;
        }}
        
        .stButton > button:hover {{
            background-color: var(--accent-color);
        }}
        
        .stSelectbox > div > div {{
            background-color: var(--card-background);
            border-color: var(--border-color);
        }}
        
        .stTextInput > div > div > input {{
            background-color: var(--card-background);
            border-color: var(--border-color);
            color: var(--text-color);
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            background-color: var(--card-background);
            border-bottom: 2px solid var(--border-color);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: var(--text-color);
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: var(--primary-color);
            color: white;
        }}
        </style>
        """
        return css

def render_theme_selector():
    """Render theme selection interface"""
    st.markdown("### 🎨 Theme Selector")
    
    user = get_current_user()
    if not user:
        st.warning("Please login to customize themes")
        return
    
    theme_manager = ThemeManager()
    current_theme = theme_manager.get_current_theme(user['id'])
    
    # Theme tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Predefined", "🤖 AI Generated", "📁 Upload", "🎨 Custom"])
    
    with tab1:
        render_predefined_themes(theme_manager, user['id'], current_theme)
    
    with tab2:
        render_ai_theme_generator(theme_manager, user['id'])
    
    with tab3:
        render_theme_upload(theme_manager, user['id'])
    
    with tab4:
        render_custom_theme_creator(theme_manager, user['id'], current_theme)

def render_predefined_themes(theme_manager: ThemeManager, user_id: int, current_theme: Dict):
    """Render predefined theme selection"""
    st.markdown("#### Choose from Predefined Themes")
    
    # Display themes in a grid
    cols = st.columns(3)
    
    for idx, (theme_name, theme_data) in enumerate(theme_manager.predefined_themes.items()):
        with cols[idx % 3]:
            # Theme preview card
            render_theme_preview(theme_name, theme_data)
            
            # Apply button
            is_current = current_theme.get('theme_name') == theme_name
            button_text = "✓ Current" if is_current else "Apply Theme"
            
            if st.button(button_text, key=f"apply_{theme_name}", disabled=is_current):
                if theme_manager.apply_theme(user_id, theme_data):
                    st.success(f"{theme_name} theme applied!")
                    st.rerun()
                else:
                    st.error("Failed to apply theme")

def render_theme_preview(theme_name: str, theme_data: Dict):
    """Render a preview of the theme"""
    preview_html = f"""
    <div style="
        background: {theme_data['background_color']};
        border: 2px solid {theme_data['border_color']};
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        height: 180px;
        position: relative;
    ">
        <div style="
            background: {theme_data['primary_color']};
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            margin-bottom: 12px;
            font-weight: bold;
            font-size: 14px;
        ">
            {theme_name}
        </div>
        
        <div style="
            background: {theme_data['card_background']};
            border-left: 4px solid {theme_data['primary_color']};
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 8px;
        ">
            <h4 style="
                color: {theme_data['text_color']};
                margin: 0 0 6px 0;
                font-size: 14px;
            ">
                Sample News Title
            </h4>
            <p style="
                color: #666;
                margin: 0;
                font-size: 12px;
                line-height: 1.3;
            ">
                This is how articles will look with this theme...
            </p>
        </div>
        
        <div style="
            background: {theme_data['secondary_color']};
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 11px;
            display: inline-block;
        ">
            Sample Button
        </div>
        
        <div style="
            position: absolute;
            bottom: 8px;
            right: 8px;
            color: #888;
            font-size: 10px;
        ">
            {theme_data.get('description', '')}
        </div>
    </div>
    """
    
    st.markdown(preview_html, unsafe_allow_html=True)

def render_ai_theme_generator(theme_manager: ThemeManager, user_id: int):
    """Render AI theme generation interface"""
    st.markdown("#### 🤖 AI Theme Generator")
    
    with st.form("ai_theme_form"):
        st.markdown("Describe your ideal theme and let AI create it for you!")
        
        # Theme description input
        theme_prompt = st.text_area(
            "Describe your theme",
            placeholder="e.g., 'A calming theme with soft blues and greens for reading at night' or 'A vibrant theme with warm colors for energy and focus'",
            height=100
        )
        
        # Style preferences
        col1, col2 = st.columns(2)
        
        with col1:
            contrast_level = st.selectbox(
                "Contrast Level",
                ["Low", "Medium", "High"],
                index=1
            )
            
            color_temperature = st.selectbox(
                "Color Temperature", 
                ["Cool (Blues/Greens)", "Neutral", "Warm (Reds/Oranges)"],
                index=1
            )
        
        with col2:
            brightness = st.selectbox(
                "Brightness",
                ["Dark", "Medium", "Light"],
                index=2
            )
            
            mood = st.selectbox(
                "Mood",
                ["Professional", "Casual", "Playful", "Serious", "Creative"],
                index=0
            )
        
        if st.form_submit_button("🎨 Generate AI Theme"):
            if theme_prompt.strip():
                with st.spinner("AI is creating your custom theme..."):
                    # Enhanced prompt with user preferences
                    enhanced_prompt = f"""
                    Create a theme based on: {theme_prompt}
                    
                    Additional preferences:
                    - Contrast: {contrast_level}
                    - Temperature: {color_temperature}
                    - Brightness: {brightness}
                    - Mood: {mood}
                    
                    The theme should be suitable for a news application with good readability.
                    """
                    
                    try:
                        ai_theme = generate_theme(enhanced_prompt)
                        
                        if ai_theme:
                            st.success("AI theme generated successfully!")
                            
                            # Display AI theme preview
                            st.markdown("#### Preview")
                            render_theme_preview(
                                ai_theme.get('theme_name', 'AI Generated Theme'),
                                ai_theme
                            )
                            
                            # Apply AI theme
                            if st.button("✨ Apply AI Theme"):
                                if theme_manager.apply_theme(user_id, ai_theme):
                                    st.success("AI theme applied!")
                                    st.rerun()
                                else:
                                    st.error("Failed to apply AI theme")
                        else:
                            st.error("Failed to generate AI theme. Please try again.")
                    
                    except Exception as e:
                        st.error(f"Error generating AI theme: {e}")
            else:
                st.error("Please describe your desired theme")

def render_theme_upload(theme_manager: ThemeManager, user_id: int):
    """Render theme upload interface"""
    st.markdown("#### 📁 Upload Theme")
    
    st.info("Upload a theme JSON file created by yourself or downloaded from the community.")
    
    uploaded_file = st.file_uploader(
        "Choose theme file",
        type=['json'],
        help="Upload a JSON file containing theme configuration"
    )
    
    if uploaded_file:
        try:
            theme_data = json.load(uploaded_file)
            
            # Validate theme structure
            required_keys = [
                'primary_color', 'secondary_color', 'background_color', 
                'text_color', 'accent_color', 'card_background', 'border_color'
            ]
            
            missing_keys = [key for key in required_keys if key not in theme_data]
            
            if missing_keys:
                st.error(f"Invalid theme file. Missing keys: {', '.join(missing_keys)}")
            else:
                # Display uploaded theme preview
                st.success("Theme file loaded successfully!")
                
                theme_name = theme_data.get('theme_name', 'Uploaded Theme')
                render_theme_preview(theme_name, theme_data)
                
                # Apply uploaded theme
                if st.button("📁 Apply Uploaded Theme"):
                    if theme_manager.apply_theme(user_id, theme_data):
                        st.success("Uploaded theme applied!")
                        st.rerun()
                    else:
                        st.error("Failed to apply uploaded theme")
        
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid theme file.")
        except Exception as e:
            st.error(f"Error loading theme file: {e}")
    
    # Download current theme
    st.markdown("#### 💾 Download Current Theme")
    
    current_theme = theme_manager.get_current_theme(user_id)
    
    if st.button("💾 Download Current Theme"):
        theme_json = json.dumps(current_theme, indent=2)
        st.download_button(
            label="📥 Download Theme JSON",
            data=theme_json,
            file_name=f"{current_theme.get('theme_name', 'theme')}.json",
            mime="application/json"
        )

def render_custom_theme_creator(theme_manager: ThemeManager, user_id: int, current_theme: Dict):
    """Render custom theme creation interface"""
    st.markdown("#### 🎨 Custom Theme Creator")
    
    with st.form("custom_theme_form"):
        # Theme metadata
        theme_name = st.text_input(
            "Theme Name", 
            value=current_theme.get('theme_name', 'My Custom Theme')
        )
        
        theme_description = st.text_area(
            "Theme Description",
            value=current_theme.get('description', ''),
            placeholder="Describe your custom theme..."
        )
        
        # Color selection
        st.markdown("##### Color Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            primary_color = st.color_picker(
                "Primary Color",
                value=current_theme.get('primary_color', '#1A73E8'),
                help="Main brand color used for buttons and highlights"
            )
            
            secondary_color = st.color_picker(
                "Secondary Color", 
                value=current_theme.get('secondary_color', '#34A853'),
                help="Secondary accent color"
            )
            
            accent_color = st.color_picker(
                "Accent Color",
                value=current_theme.get('accent_color', '#EA4335'),
                help="Color for important highlights and alerts"
            )
        
        with col2:
            background_color = st.color_picker(
                "Background Color",
                value=current_theme.get('background_color', '#F8F9FA'),
                help="Main page background color"
            )
            
            card_background = st.color_picker(
                "Card Background",
                value=current_theme.get('card_background', '#FFFFFF'),
                help="Background color for cards and panels"
            )
            
            border_color = st.color_picker(
                "Border Color",
                value=current_theme.get('border_color', '#E0E0E0'),
                help="Color for borders and dividers"
            )
        
        with col3:
            text_color = st.color_picker(
                "Text Color",
                value=current_theme.get('text_color', '#202124'),
                help="Main text color"
            )
            
            # Auto-generate complementary colors
            if st.button("🎨 Generate Palette", help="Auto-generate complementary colors"):
                palette = generate_color_palette(primary_color)
                st.session_state.generated_palette = palette
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            # Typography settings
            font_family = st.selectbox(
                "Font Family",
                ["Default", "Roboto", "Inter", "Arial", "Helvetica", "Georgia"],
                index=0
            )
            
            # Spacing and sizing
            border_radius = st.slider("Border Radius (px)", 0, 20, 8)
            card_shadow = st.selectbox(
                "Card Shadow",
                ["None", "Light", "Medium", "Heavy"],
                index=1
            )
            
            # Animation preferences
            enable_animations = st.checkbox("Enable Animations", value=True)
            animation_speed = st.selectbox(
                "Animation Speed",
                ["Slow", "Normal", "Fast"],
                index=1
            )
        
        # Preview section
        st.markdown("##### Preview")
        
        # Create preview theme data
        preview_theme = {
            'theme_name': theme_name,
            'description': theme_description,
            'primary_color': primary_color,
            'secondary_color': secondary_color,
            'background_color': background_color,
            'text_color': text_color,
            'accent_color': accent_color,
            'card_background': card_background,
            'border_color': border_color,
            'font_family': font_family,
            'border_radius': border_radius,
            'card_shadow': card_shadow,
            'enable_animations': enable_animations,
            'animation_speed': animation_speed
        }
        
        render_theme_preview(theme_name, preview_theme)
        
        # Form submission
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Custom Theme"):
                if theme_name.strip():
                    if theme_manager.apply_theme(user_id, preview_theme):
                        st.success("Custom theme saved and applied!")
                        st.rerun()
                    else:
                        st.error("Failed to save custom theme")
                else:
                    st.error("Please enter a theme name")
        
        with col2:
            if st.form_submit_button("🔄 Reset to Default"):
                default_theme = theme_manager.predefined_themes["Default"]
                if theme_manager.apply_theme(user_id, default_theme):
                    st.success("Theme reset to default!")
                    st.rerun()
                else:
                    st.error("Failed to reset theme")

def render_theme_marketplace():
    """Render theme marketplace for sharing themes"""
    st.markdown("### 🏪 Theme Marketplace")
    
    st.info("Theme marketplace coming soon! Share and discover themes created by the community.")
    
    # Mock marketplace themes
    marketplace_themes = [
        {
            "name": "Newspaper Classic",
            "author": "ThemeCreator",
            "downloads": 1250,
            "rating": 4.8,
            "description": "Classic newspaper-inspired theme"
        },
        {
            "name": "Neon Cyberpunk",
            "author": "FutureDesigner", 
            "downloads": 890,
            "rating": 4.6,
            "description": "Futuristic neon cyberpunk theme"
        },
        {
            "name": "Pastel Dreams",
            "author": "SoftColors",
            "downloads": 2100,
            "rating": 4.9,
            "description": "Soft pastel colors for gentle reading"
        }
    ]
    
    cols = st.columns(3)
    
    for idx, theme in enumerate(marketplace_themes):
        with cols[idx]:
            with st.container():
                st.markdown(f"**{theme['name']}**")
                st.write(f"By {theme['author']}")
                st.write(theme['description'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"⭐ {theme['rating']}")
                with col2:
                    st.write(f"📥 {theme['downloads']}")
                
                if st.button(f"Download", key=f"download_{idx}"):
                    st.info("Marketplace download coming soon!")

def apply_theme_css(theme_data: Dict):
    """Apply theme CSS to the current page"""
    theme_manager = ThemeManager()
    css = theme_manager.generate_css(theme_data)
    st.markdown(css, unsafe_allow_html=True)

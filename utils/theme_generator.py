import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import colorsys
import random

class ThemeGenerator:
    def __init__(self):
        # Base theme templates
        self.base_themes = {
            'modern': {
                'primary_hue': 220,
                'secondary_hue': 200,
                'saturation': 0.7,
                'lightness': 0.5,
                'style': 'clean, minimalist, professional'
            },
            'vibrant': {
                'primary_hue': 340,
                'secondary_hue': 280,
                'saturation': 0.9,
                'lightness': 0.6,
                'style': 'energetic, bold, attention-grabbing'
            },
            'calm': {
                'primary_hue': 200,
                'secondary_hue': 160,
                'saturation': 0.4,
                'lightness': 0.7,
                'style': 'peaceful, serene, easy on eyes'
            },
            'professional': {
                'primary_hue': 210,
                'secondary_hue': 30,
                'saturation': 0.6,
                'lightness': 0.4,
                'style': 'business-like, trustworthy, sophisticated'
            },
            'warm': {
                'primary_hue': 30,
                'secondary_hue': 60,
                'saturation': 0.8,
                'lightness': 0.6,
                'style': 'welcoming, cozy, inviting'
            },
            'cool': {
                'primary_hue': 180,
                'secondary_hue': 240,
                'saturation': 0.6,
                'lightness': 0.5,
                'style': 'fresh, modern, tech-oriented'
            }
        }
        
        # Typography options
        self.font_combinations = {
            'modern': {
                'primary': 'Inter, system-ui, sans-serif',
                'secondary': 'Roboto, Arial, sans-serif',
                'accent': 'Poppins, sans-serif'
            },
            'classic': {
                'primary': 'Georgia, serif',
                'secondary': 'Arial, sans-serif',
                'accent': 'Playfair Display, serif'
            },
            'tech': {
                'primary': 'Fira Code, monospace',
                'secondary': 'Source Sans Pro, sans-serif',
                'accent': 'JetBrains Mono, monospace'
            },
            'elegant': {
                'primary': 'Crimson Text, serif',
                'secondary': 'Lato, sans-serif',
                'accent': 'Libre Baskerville, serif'
            }
        }
        
        # Spacing systems
        self.spacing_systems = {
            'compact': {'base': '8px', 'scale': 1.2},
            'standard': {'base': '16px', 'scale': 1.5},
            'generous': {'base': '24px', 'scale': 1.618}
        }
    
    def generate_theme_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate a theme based on a text prompt"""
        try:
            # Parse prompt for theme characteristics
            theme_characteristics = self._parse_prompt(prompt)
            
            # Select base theme
            base_theme_name = self._select_base_theme(theme_characteristics)
            base_theme = self.base_themes[base_theme_name]
            
            # Generate color palette
            color_palette = self._generate_color_palette(base_theme, theme_characteristics)
            
            # Select typography
            typography = self._select_typography(theme_characteristics)
            
            # Select spacing system
            spacing = self._select_spacing(theme_characteristics)
            
            # Generate component styles
            component_styles = self._generate_component_styles(color_palette, typography, spacing)
            
            # Create complete theme
            theme = {
                'name': self._generate_theme_name(theme_characteristics),
                'description': f"Generated theme based on: {prompt}",
                'base_theme': base_theme_name,
                'colors': color_palette,
                'typography': typography,
                'spacing': spacing,
                'components': component_styles,
                'created_at': datetime.now().isoformat(),
                'prompt': prompt
            }
            
            return theme
            
        except Exception as e:
            logging.error(f"Error generating theme from prompt: {str(e)}")
            return self._get_default_theme()
    
    def _parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parse prompt to extract theme characteristics"""
        try:
            prompt_lower = prompt.lower()
            
            characteristics = {
                'mood': 'neutral',
                'style': 'modern',
                'colors': [],
                'energy': 'medium',
                'formality': 'medium',
                'contrast': 'medium'
            }
            
            # Mood detection
            if any(word in prompt_lower for word in ['calm', 'peaceful', 'serene', 'quiet']):
                characteristics['mood'] = 'calm'
            elif any(word in prompt_lower for word in ['energetic', 'vibrant', 'bold', 'dynamic']):
                characteristics['mood'] = 'energetic'
            elif any(word in prompt_lower for word in ['warm', 'cozy', 'welcoming', 'friendly']):
                characteristics['mood'] = 'warm'
            elif any(word in prompt_lower for word in ['cool', 'fresh', 'clean', 'minimal']):
                characteristics['mood'] = 'cool'
            
            # Style detection
            if any(word in prompt_lower for word in ['professional', 'business', 'corporate']):
                characteristics['style'] = 'professional'
            elif any(word in prompt_lower for word in ['modern', 'contemporary', 'sleek']):
                characteristics['style'] = 'modern'
            elif any(word in prompt_lower for word in ['classic', 'traditional', 'timeless']):
                characteristics['style'] = 'classic'
            elif any(word in prompt_lower for word in ['tech', 'digital', 'futuristic']):
                characteristics['style'] = 'tech'
            
            # Color detection
            color_keywords = {
                'blue': ['blue', 'navy', 'azure', 'cyan'],
                'green': ['green', 'emerald', 'forest', 'mint'],
                'red': ['red', 'crimson', 'ruby', 'coral'],
                'purple': ['purple', 'violet', 'lavender', 'magenta'],
                'orange': ['orange', 'amber', 'peach', 'tangerine'],
                'yellow': ['yellow', 'gold', 'sunshine', 'lemon'],
                'pink': ['pink', 'rose', 'blush', 'salmon'],
                'brown': ['brown', 'tan', 'beige', 'chocolate']
            }
            
            for color, keywords in color_keywords.items():
                if any(keyword in prompt_lower for keyword in keywords):
                    characteristics['colors'].append(color)
            
            # Energy level
            if any(word in prompt_lower for word in ['high', 'intense', 'strong', 'powerful']):
                characteristics['energy'] = 'high'
            elif any(word in prompt_lower for word in ['low', 'subtle', 'gentle', 'soft']):
                characteristics['energy'] = 'low'
            
            # Formality level
            if any(word in prompt_lower for word in ['formal', 'serious', 'official']):
                characteristics['formality'] = 'high'
            elif any(word in prompt_lower for word in ['casual', 'informal', 'relaxed']):
                characteristics['formality'] = 'low'
            
            # Contrast level
            if any(word in prompt_lower for word in ['high contrast', 'bold', 'stark']):
                characteristics['contrast'] = 'high'
            elif any(word in prompt_lower for word in ['low contrast', 'subtle', 'muted']):
                characteristics['contrast'] = 'low'
            
            return characteristics
            
        except Exception as e:
            logging.error(f"Error parsing prompt: {str(e)}")
            return {'mood': 'neutral', 'style': 'modern', 'colors': [], 'energy': 'medium'}
    
    def _select_base_theme(self, characteristics: Dict[str, Any]) -> str:
        """Select base theme based on characteristics"""
        try:
            mood = characteristics.get('mood', 'neutral')
            style = characteristics.get('style', 'modern')
            
            # Map characteristics to base themes
            if mood == 'calm':
                return 'calm'
            elif mood == 'energetic':
                return 'vibrant'
            elif mood == 'warm':
                return 'warm'
            elif mood == 'cool':
                return 'cool'
            elif style == 'professional':
                return 'professional'
            else:
                return 'modern'
                
        except Exception as e:
            logging.error(f"Error selecting base theme: {str(e)}")
            return 'modern'
    
    def _generate_color_palette(self, base_theme: Dict[str, Any], 
                               characteristics: Dict[str, Any]) -> Dict[str, str]:
        """Generate color palette"""
        try:
            # Start with base theme colors
            primary_hue = base_theme['primary_hue']
            secondary_hue = base_theme['secondary_hue']
            saturation = base_theme['saturation']
            lightness = base_theme['lightness']
            
            # Adjust based on characteristics
            energy = characteristics.get('energy', 'medium')
            if energy == 'high':
                saturation = min(1.0, saturation + 0.2)
            elif energy == 'low':
                saturation = max(0.1, saturation - 0.2)
            
            # Generate primary colors
            primary_color = self._hsl_to_hex(primary_hue, saturation, lightness)
            secondary_color = self._hsl_to_hex(secondary_hue, saturation * 0.8, lightness + 0.1)
            
            # Generate supporting colors
            accent_color = self._hsl_to_hex((primary_hue + 120) % 360, saturation, lightness)
            
            # Generate neutral colors
            background_color = self._hsl_to_hex(primary_hue, saturation * 0.1, 0.98)
            text_color = self._hsl_to_hex(primary_hue, saturation * 0.2, 0.15)
            
            # Generate semantic colors
            success_color = self._hsl_to_hex(120, 0.6, 0.4)
            warning_color = self._hsl_to_hex(45, 0.8, 0.5)
            error_color = self._hsl_to_hex(0, 0.7, 0.5)
            info_color = self._hsl_to_hex(200, 0.7, 0.5)
            
            palette = {
                'primary': primary_color,
                'secondary': secondary_color,
                'accent': accent_color,
                'background': background_color,
                'surface': self._hsl_to_hex(primary_hue, saturation * 0.05, 0.95),
                'text': text_color,
                'text_secondary': self._hsl_to_hex(primary_hue, saturation * 0.15, 0.4),
                'border': self._hsl_to_hex(primary_hue, saturation * 0.1, 0.8),
                'success': success_color,
                'warning': warning_color,
                'error': error_color,
                'info': info_color
            }
            
            return palette
            
        except Exception as e:
            logging.error(f"Error generating color palette: {str(e)}")
            return {
                'primary': '#1A73E8',
                'secondary': '#34A853',
                'accent': '#EA4335',
                'background': '#F8F9FA',
                'text': '#202124'
            }
    
    def _select_typography(self, characteristics: Dict[str, Any]) -> Dict[str, str]:
        """Select typography based on characteristics"""
        try:
            style = characteristics.get('style', 'modern')
            formality = characteristics.get('formality', 'medium')
            
            if style == 'tech':
                return self.font_combinations['tech']
            elif style == 'classic' or formality == 'high':
                return self.font_combinations['classic']
            elif formality == 'low':
                return self.font_combinations['modern']
            else:
                return self.font_combinations['elegant']
                
        except Exception as e:
            logging.error(f"Error selecting typography: {str(e)}")
            return self.font_combinations['modern']
    
    def _select_spacing(self, characteristics: Dict[str, Any]) -> Dict[str, str]:
        """Select spacing system based on characteristics"""
        try:
            energy = characteristics.get('energy', 'medium')
            
            if energy == 'high':
                return self.spacing_systems['generous']
            elif energy == 'low':
                return self.spacing_systems['compact']
            else:
                return self.spacing_systems['standard']
                
        except Exception as e:
            logging.error(f"Error selecting spacing: {str(e)}")
            return self.spacing_systems['standard']
    
    def _generate_component_styles(self, colors: Dict[str, str], 
                                  typography: Dict[str, str], 
                                  spacing: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Generate component-specific styles"""
        try:
            components = {
                'button': {
                    'background': colors['primary'],
                    'color': '#FFFFFF',
                    'font_family': typography['primary'],
                    'padding': f"{spacing['base']} {self._multiply_spacing(spacing['base'], 2)}",
                    'border_radius': self._multiply_spacing(spacing['base'], 0.5),
                    'border': 'none',
                    'font_weight': '600'
                },
                'card': {
                    'background': colors['surface'],
                    'color': colors['text'],
                    'font_family': typography['primary'],
                    'padding': spacing['base'],
                    'border_radius': self._multiply_spacing(spacing['base'], 0.5),
                    'border': f"1px solid {colors['border']}",
                    'box_shadow': '0 2px 4px rgba(0,0,0,0.1)'
                },
                'input': {
                    'background': colors['background'],
                    'color': colors['text'],
                    'font_family': typography['primary'],
                    'padding': self._multiply_spacing(spacing['base'], 0.75),
                    'border_radius': self._multiply_spacing(spacing['base'], 0.25),
                    'border': f"1px solid {colors['border']}",
                    'font_size': '16px'
                },
                'heading': {
                    'color': colors['text'],
                    'font_family': typography['accent'],
                    'font_weight': '700',
                    'line_height': '1.2',
                    'margin_bottom': spacing['base']
                },
                'paragraph': {
                    'color': colors['text_secondary'],
                    'font_family': typography['primary'],
                    'font_size': '16px',
                    'line_height': '1.6',
                    'margin_bottom': spacing['base']
                }
            }
            
            return components
            
        except Exception as e:
            logging.error(f"Error generating component styles: {str(e)}")
            return {}
    
    def _hsl_to_hex(self, hue: float, saturation: float, lightness: float) -> str:
        """Convert HSL to hex color"""
        try:
            # Normalize values
            h = hue / 360
            s = saturation
            l = lightness
            
            # Convert to RGB
            rgb = colorsys.hls_to_rgb(h, l, s)
            
            # Convert to hex
            hex_color = '#%02x%02x%02x' % (
                int(rgb[0] * 255),
                int(rgb[1] * 255),
                int(rgb[2] * 255)
            )
            
            return hex_color.upper()
            
        except Exception as e:
            logging.error(f"Error converting HSL to hex: {str(e)}")
            return '#000000'
    
    def _multiply_spacing(self, base_spacing: str, multiplier: float) -> str:
        """Multiply spacing value"""
        try:
            # Extract numeric value
            numeric_value = float(base_spacing.replace('px', ''))
            
            # Multiply and format
            new_value = numeric_value * multiplier
            return f"{int(new_value)}px"
            
        except Exception as e:
            logging.error(f"Error multiplying spacing: {str(e)}")
            return base_spacing
    
    def _generate_theme_name(self, characteristics: Dict[str, Any]) -> str:
        """Generate a name for the theme"""
        try:
            mood = characteristics.get('mood', 'neutral')
            style = characteristics.get('style', 'modern')
            
            adjectives = {
                'calm': ['Serene', 'Peaceful', 'Tranquil'],
                'energetic': ['Dynamic', 'Vibrant', 'Bold'],
                'warm': ['Cozy', 'Welcoming', 'Friendly'],
                'cool': ['Fresh', 'Clean', 'Crisp'],
                'neutral': ['Balanced', 'Classic', 'Timeless']
            }
            
            nouns = {
                'modern': ['Edge', 'Flow', 'Pulse'],
                'professional': ['Suite', 'Pro', 'Executive'],
                'classic': ['Heritage', 'Vintage', 'Tradition'],
                'tech': ['Code', 'Digital', 'Matrix']
            }
            
            adjective = random.choice(adjectives.get(mood, ['Custom']))
            noun = random.choice(nouns.get(style, ['Theme']))
            
            return f"{adjective} {noun}"
            
        except Exception as e:
            logging.error(f"Error generating theme name: {str(e)}")
            return "Custom Theme"
    
    def generate_css(self, theme: Dict[str, Any]) -> str:
        """Generate CSS from theme data"""
        try:
            colors = theme.get('colors', {})
            typography = theme.get('typography', {})
            spacing = theme.get('spacing', {})
            components = theme.get('components', {})
            
            css = f"""
            /* {theme.get('name', 'Custom Theme')} */
            /* Generated on {theme.get('created_at', datetime.now().isoformat())} */
            
            :root {{
                /* Colors */
                --primary: {colors.get('primary', '#1A73E8')};
                --secondary: {colors.get('secondary', '#34A853')};
                --accent: {colors.get('accent', '#EA4335')};
                --background: {colors.get('background', '#F8F9FA')};
                --surface: {colors.get('surface', '#FFFFFF')};
                --text: {colors.get('text', '#202124')};
                --text-secondary: {colors.get('text_secondary', '#5F6368')};
                --border: {colors.get('border', '#DADCE0')};
                --success: {colors.get('success', '#34A853')};
                --warning: {colors.get('warning', '#FBBC04')};
                --error: {colors.get('error', '#EA4335')};
                --info: {colors.get('info', '#1A73E8')};
                
                /* Typography */
                --font-primary: {typography.get('primary', 'Inter, sans-serif')};
                --font-secondary: {typography.get('secondary', 'Roboto, sans-serif')};
                --font-accent: {typography.get('accent', 'Poppins, sans-serif')};
                
                /* Spacing */
                --spacing-base: {spacing.get('base', '16px')};
                --spacing-scale: {spacing.get('scale', '1.5')};
            }}
            
            /* Global Styles */
            body {{
                font-family: var(--font-primary);
                color: var(--text);
                background-color: var(--background);
                line-height: 1.6;
            }}
            
            /* Component Styles */
            """
            
            # Add component styles
            for component, styles in components.items():
                css += f"\n.{component} {{\n"
                for property, value in styles.items():
                    css_property = property.replace('_', '-')
                    css += f"    {css_property}: {value};\n"
                css += "}\n"
            
            return css
            
        except Exception as e:
            logging.error(f"Error generating CSS: {str(e)}")
            return ""
    
    def save_theme(self, theme: Dict[str, Any], filename: str) -> bool:
        """Save theme to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(theme, f, indent=2)
            return True
            
        except Exception as e:
            logging.error(f"Error saving theme: {str(e)}")
            return False
    
    def load_theme(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load theme from file"""
        try:
            with open(filename, 'r') as f:
                theme = json.load(f)
            return theme
            
        except Exception as e:
            logging.error(f"Error loading theme: {str(e)}")
            return None
    
    def _get_default_theme(self) -> Dict[str, Any]:
        """Get default theme"""
        return {
            'name': 'Default Theme',
            'description': 'Default application theme',
            'colors': {
                'primary': '#1A73E8',
                'secondary': '#34A853',
                'accent': '#EA4335',
                'background': '#F8F9FA',
                'text': '#202124'
            },
            'typography': {
                'primary': 'Inter, sans-serif',
                'secondary': 'Roboto, sans-serif',
                'accent': 'Poppins, sans-serif'
            },
            'spacing': {
                'base': '16px',
                'scale': '1.5'
            },
            'components': {},
            'created_at': datetime.now().isoformat()
        }

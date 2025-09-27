import json
import os
from tkinter import messagebox

class DataManager:
    """Manages color palette and user settings data"""
    
    def __init__(self):
        self.color_palette = self._load_color_palette()
        self.user_settings = self._load_user_settings()
        
        # Analysis state
        self.canvas_region = self.user_settings.get('preferences', {}).get('last_canvas_region')
        self.palette_region = self.user_settings.get('preferences', {}).get('last_palette_region')
        self.pixel_map = None
        self.color_position_map = None
        self.pixel_size = None
    
    def _load_color_palette(self):
        """Load color palette from JSON file, excluding ignored colors"""
        try:
            with open('colors.json', 'r') as f:
                data = json.load(f)
                filtered_palette = [
                    color for color in data['color_palette'] 
                    if not color.get('ignore', False)
                ]
                print(f"Loaded {len(filtered_palette)} colors (filtered out ignored colors)")
                return filtered_palette
        except FileNotFoundError:
            messagebox.showerror("Error", "colors.json not found!")
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load colors.json: {e}")
            return []

    def _load_user_settings(self):
        """Load user settings from JSON file"""
        default_settings = {
            "color_profiles": {
                "Default": {"colors": {}}
            },
            "active_color_profile": "Default",
            "preferences": {
                "color_tolerance": 5,
                "click_delay": 20,
                "pixel_limit": 50,
                "auto_save_regions": True
            }
        }
        
        try:
            if os.path.exists('user_settings.json'):
                with open('user_settings.json', 'r') as f:
                    settings = json.load(f)
                    
                    # Migrate old format if needed
                    if 'bought_colors' in settings or 'enabled_colors' in settings or 'colors' in settings:
                        settings = self._migrate_old_format(settings)
                    
                    # Merge with defaults
                    for key in default_settings:
                        if key not in settings:
                            settings[key] = default_settings[key]
                    return settings
            else:
                return default_settings
        except Exception as e:
            print(f"Failed to load user settings: {e}")
            return default_settings

    def _migrate_old_format(self, old_settings):
        """Convert old settings format to new profile-based format"""
        new_settings = {
            "color_profiles": {
                "Default": {"colors": {}}
            },
            "active_color_profile": "Default",
            "preferences": old_settings.get('preferences', {})
        }
        
        # Migrate from old 'colors' format or older formats
        colors_data = {}
        if 'colors' in old_settings:
            colors_data = old_settings['colors']
        else:
            # Handle very old format with separate bought_colors/enabled_colors
            all_color_ids = set()
            if 'bought_colors' in old_settings:
                all_color_ids.update(old_settings['bought_colors'].keys())
            if 'enabled_colors' in old_settings:
                all_color_ids.update(old_settings['enabled_colors'].keys())
            
            for color_id in all_color_ids:
                color_data = {}
                if color_id in old_settings.get('enabled_colors', {}):
                    color_data['enabled'] = old_settings['enabled_colors'][color_id]
                if color_id in old_settings.get('bought_colors', {}):
                    color_data['bought'] = old_settings['bought_colors'][color_id]
                colors_data[color_id] = color_data
        
        new_settings['color_profiles']['Default']['colors'] = colors_data
        return new_settings

    def save_user_settings(self):
        """Save user settings to JSON file"""
        try:
            # Save current regions
            if self.canvas_region:
                self.user_settings['preferences']['last_canvas_region'] = self.canvas_region
            if self.palette_region:
                self.user_settings['preferences']['last_palette_region'] = self.palette_region
            
            with open('user_settings.json', 'w') as f:
                json.dump(self.user_settings, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save user settings: {e}")
    
    def update_preference(self, key, value):
        """Update a preference setting"""
        self.user_settings['preferences'][key] = value
        self.save_user_settings()
    
    def get_preference(self, key, default=None):
        """Get a preference setting"""
        return self.user_settings['preferences'].get(key, default)
    
    def set_canvas_region(self, region):
        """Set canvas region"""
        self.canvas_region = region
        self.save_user_settings()
    
    def set_palette_region(self, region):
        """Set palette region"""
        self.palette_region = region
        self.save_user_settings()
    
    def get_color_setting(self, color_id, key, default=None):
        """Get a color-specific setting from active profile"""
        active_profile = self.user_settings['active_color_profile']
        profile_colors = self.user_settings['color_profiles'].get(active_profile, {}).get('colors', {})
        return profile_colors.get(str(color_id), {}).get(key, default)
    
    def set_color_setting(self, color_id, key, value):
        """Set a color-specific setting in active profile"""
        color_id = str(color_id)
        active_profile = self.user_settings['active_color_profile']
        
        if active_profile not in self.user_settings['color_profiles']:
            self.user_settings['color_profiles'][active_profile] = {'colors': {}}
        
        profile_colors = self.user_settings['color_profiles'][active_profile]['colors']
        if color_id not in profile_colors:
            profile_colors[color_id] = {}
        
        profile_colors[color_id][key] = value
        self.save_user_settings()
    
    def get_active_profile(self):
        """Get active color profile name"""
        return self.user_settings['active_color_profile']
    
    def get_profile_names(self):
        """Get list of all profile names"""
        return list(self.user_settings['color_profiles'].keys())
    
    def create_profile(self, name):
        """Create new color profile"""
        if name not in self.user_settings['color_profiles']:
            self.user_settings['color_profiles'][name] = {'colors': {}}
            self.save_user_settings()
            return True
        return False
    
    def switch_profile(self, name):
        """Switch to different color profile"""
        if name in self.user_settings['color_profiles']:
            self.user_settings['active_color_profile'] = name
            self.save_user_settings()
            return True
        return False
    
    def rename_profile(self, old_name, new_name):
        """Rename a color profile"""
        if old_name in self.user_settings['color_profiles'] and new_name not in self.user_settings['color_profiles']:
            self.user_settings['color_profiles'][new_name] = self.user_settings['color_profiles'].pop(old_name)
            if self.user_settings['active_color_profile'] == old_name:
                self.user_settings['active_color_profile'] = new_name
            self.save_user_settings()
            return True
        return False
    
    def delete_profile(self, name):
        """Delete a color profile (cannot delete Default)"""
        if name != 'Default' and name in self.user_settings['color_profiles']:
            del self.user_settings['color_profiles'][name]
            if self.user_settings['active_color_profile'] == name:
                self.user_settings['active_color_profile'] = 'Default'
            self.save_user_settings()
            return True
        return False
    
    def copy_profile(self, source_name, new_name):
        """Copy a profile to a new profile"""
        if source_name in self.user_settings['color_profiles'] and new_name not in self.user_settings['color_profiles']:
            import copy
            self.user_settings['color_profiles'][new_name] = copy.deepcopy(self.user_settings['color_profiles'][source_name])
            self.save_user_settings()
            return True
        return False
    
    def get_enabled_colors(self):
        """Get list of enabled colors"""
        enabled_colors = []
        for color in self.color_palette:
            color_id = str(color['id'])
            is_enabled = self.get_color_setting(color_id, 'enabled', True)
            if is_enabled:
                enabled_colors.append(color)
        return enabled_colors
    
    def set_analysis_results(self, pixel_size, pixel_map, color_position_map):
        """Store analysis results"""
        self.pixel_size = pixel_size
        self.pixel_map = pixel_map
        self.color_position_map = color_position_map
    
    def has_analysis_data(self):
        """Check if analysis data is available"""
        return self.pixel_map is not None and self.color_position_map is not None
    
    def has_regions(self):
        """Check if both regions are selected"""
        return self.canvas_region is not None and self.palette_region is not None
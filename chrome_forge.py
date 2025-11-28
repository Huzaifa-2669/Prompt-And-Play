"""
ChromeForge - Chrome Extension Generator
Generates Chrome extensions from natural language descriptions
"""

import json
import os
import re
from manifest_builder import generate_manifest
from code_generator import CodeGenerator


class PromptAnalyzer:
    """Part A - Analyzes user prompts to determine extension requirements"""
    
    def __init__(self, user_prompt):
        self.prompt = user_prompt.lower()
        self.requirements = {
            'needs_popup': False,
            'needs_content_script': False,
            'needs_background': False,
            'needs_css': False,
            'permissions': set(),
            'features': []
        }
    
    def analyze(self):
        """Analyze the prompt and determine all requirements"""
        self._detect_popup()
        self._detect_content_script()
        self._detect_background()
        self._detect_permissions()
        self._detect_css()
        
        # Store original prompt for description
        self.requirements['original_prompt'] = self.prompt
        
        return self.requirements
    
    def _detect_popup(self):
        """Detect if a popup UI is needed"""
        popup_keywords = [
            'popup', 'button in', 'menu', 'click a button', 'interface', 'ui',
            'show a popup', 'display', 'panel', 'window', 'input', 'form',
            'today\'s date', 'calculator', 'converter', 'list'
        ]
        
        # Keywords that suggest user interaction via popup
        for keyword in popup_keywords:
            if keyword in self.prompt:
                self.requirements['needs_popup'] = True
                self.requirements['features'].append('popup_ui')
                break
        
        # Special cases that need popup for display
        if 'extract' in self.prompt and 'display' in self.prompt:
            self.requirements['needs_popup'] = True
            if 'popup_ui' not in self.requirements['features']:
                self.requirements['features'].append('popup_ui')
        
        # Special case: if it's a timer/notification tool, needs popup for controls
        if ('timer' in self.prompt or 'pomodoro' in self.prompt) and not self.requirements['needs_popup']:
            self.requirements['needs_popup'] = True
            self.requirements['features'].append('popup_ui')
    
    def _detect_content_script(self):
        """Detect if content script is needed (webpage modification)"""
        content_keywords = [
            'highlight', 'webpage', 'website', 'page', 'dom', 'text',
            'change', 'modify', 'replace', 'extract', 'find', 'search',
            'color', 'style', 'hide', 'remove', 'add', 'insert',
            'phone number', 'email', 'link', 'image', 'element',
            'all websites', 'any website', 'every page'
        ]
        
        for keyword in content_keywords:
            if keyword in self.prompt:
                self.requirements['needs_content_script'] = True
                self.requirements['features'].append('content_modification')
                break
    
    def _detect_background(self):
        """Detect if background script is needed"""
        background_keywords = [
            'block', 'blocking', 'automation', 'automatic', 'alarm',
            'timer', 'schedule', 'filter', 'url', 'monitor', 'track',
            'every time', 'on startup', 'browser opens', 'redirect',
            'intercept', 'request', 'api call', 'fetch', 'listener'
        ]
        
        for keyword in background_keywords:
            if keyword in self.prompt:
                self.requirements['needs_background'] = True
                self.requirements['features'].append('background_logic')
                break
    
    def _detect_permissions(self):
        """Detect required permissions based on features"""
        permissions = self.requirements['permissions']
        
        # Content script permissions
        if self.requirements['needs_content_script']:
            permissions.add('activeTab')
            permissions.add('scripting')
        
        # Storage permission (common for most extensions)
        if 'storage' in self.prompt or 'save' in self.prompt or 'remember' in self.prompt:
            permissions.add('storage')
        
        # Tabs permission
        if 'tab' in self.prompt or 'url' in self.prompt or 'website' in self.prompt:
            permissions.add('tabs')
        
        # WebRequest permissions for blocking
        if 'block' in self.prompt or 'filter' in self.prompt:
            permissions.add('webRequest')
            permissions.add('webRequestBlocking')
            permissions.add('declarativeNetRequest')
            permissions.add('declarativeNetRequestWithHostAccess')
        
        # Alarms permission
        if 'alarm' in self.prompt or 'timer' in self.prompt or 'schedule' in self.prompt:
            permissions.add('alarms')
    
    def _detect_css(self):
        """Detect if CSS styling is needed"""
        css_keywords = [
            'style', 'css', 'color', 'theme', 'design', 'beautiful',
            'styled', 'gradient', 'background', 'font', 'layout'
        ]
        
        for keyword in css_keywords:
            if keyword in self.prompt:
                self.requirements['needs_css'] = True
                break
        
        # Auto-enable CSS if popup is needed
        if self.requirements['needs_popup']:
            self.requirements['needs_css'] = True


def convert_to_manifest_format(requirements, user_prompt):
    """Convert Part A requirements to Part B manifest format"""
    return {
        "name": "Generated Extension",
        "version": "1.0",
        "description": user_prompt[:100],  # Use first 100 chars of prompt
        "need_popup": requirements['needs_popup'],
        "need_content": requirements['needs_content_script'],
        "need_background": requirements['needs_background'],
        "need_css": requirements['needs_css'],
        "permissions": list(requirements['permissions']),
        "content_matches": ["<all_urls>"] if requirements['needs_content_script'] else []
    }


def main():
    """Main function to run ChromeForge"""
    print("=" * 60)
    print("ChromeForge - Chrome Extension Generator".center(60))
    print("=" * 60)
    print()
    
    # Get user input
    print("Describe the Chrome Extension you want to generate:")
    user_prompt = input("> ").strip()
    
    if not user_prompt:
        print("Error: Please provide a description.")
        return
    
    print("\n" + "=" * 60)
    print("Analyzing your prompt...".center(60))
    print("=" * 60 + "\n")
    
    # Part A - Analyze the prompt
    analyzer = PromptAnalyzer(user_prompt)
    requirements = analyzer.analyze()
    
    # Display analysis results
    print("📊 Analysis Results:")
    print(f"  • Needs Popup UI: {requirements['needs_popup']}")
    print(f"  • Needs Content Script: {requirements['needs_content_script']}")
    print(f"  • Needs Background Script: {requirements['needs_background']}")
    print(f"  • Needs CSS Styling: {requirements['needs_css']}")
    print(f"  • Required Permissions: {', '.join(requirements['permissions']) if requirements['permissions'] else 'None'}")
    print(f"  • Detected Features: {', '.join(requirements['features']) if requirements['features'] else 'None'}")
    print()
    
    # Part B - Generate Manifest
    print("=" * 60)
    print("Generating Manifest V3...".center(60))
    print("=" * 60 + "\n")
    
    # Convert requirements to manifest format
    manifest_analysis = convert_to_manifest_format(requirements, user_prompt)
    
    # Generate the manifest
    manifest = generate_manifest(manifest_analysis)
    
    print("\n📄 Generated Manifest Preview:")
    print(json.dumps(manifest, indent=2))
    print()
    
    # Part C - Generate Code Files
    print("=" * 60)
    print("Generating Extension Files...".center(60))
    print("=" * 60 + "\n")
    
    generator = CodeGenerator(requirements, user_prompt)
    generated_files = generator.generate_all_files("generated_extension")
    
    print("✅ Generated Files:")
    for file in generated_files:
        print(f"  • {file}")
    print()
    
    print("=" * 60)
    print("✅ Extension Generation Complete!".center(60))
    print("=" * 60)
    print("\nYour extension is ready in 'generated_extension' folder")
    print("Load it in Chrome: chrome://extensions/ > Load unpacked")
    print()


if __name__ == "__main__":
    main()

"""
ChromeForge - Chrome Extension Generator
Generates Chrome extensions from natural language descriptions
"""

import json
import os
import re


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
        return self.requirements
    
    def _detect_popup(self):
        """Detect if a popup UI is needed"""
        popup_keywords = [
            'popup', 'button', 'menu', 'click', 'interface', 'ui',
            'show', 'display', 'panel', 'window', 'input', 'form',
            'date', 'time', 'calculator', 'converter', 'tool'
        ]
        
        for keyword in popup_keywords:
            if keyword in self.prompt:
                self.requirements['needs_popup'] = True
                self.requirements['features'].append('popup_ui')
                break
    
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


if __name__ == "__main__":
    main()

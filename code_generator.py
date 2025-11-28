"""
code_generator.py
Part C — Dynamic Code Generation

Generates HTML, JS, and CSS files based on analysis requirements
"""

import os
from typing import Dict

try:
    # optional import — gemini_client is provided but may raise if requests isn't available
    from gemini_client import generate_files as gemini_generate_files
except Exception:
    gemini_generate_files = None


class CodeGenerator:
    """Generates code files for Chrome extension based on requirements"""
    
    def __init__(self, requirements, user_prompt):
        self.requirements = requirements
        self.user_prompt = user_prompt
        self.prompt_lower = user_prompt.lower()

        # If caller explicitly requests Gemini-driven generation, note it here.
        # The presence of a key 'use_gemini' (truthy) in requirements triggers
        # an attempt to call the Gemini client. If the client isn't available
        # or API key isn't provided, a RuntimeError will be raised by the
        # client — callers are expected to handle that.
        self.use_gemini = bool(self.requirements.get('use_gemini'))
    
    def generate_popup_html(self):
        """Generate popup.html based on user prompt"""
        
        # Detect what the popup should contain
        has_button = 'button' in self.prompt_lower or 'click' in self.prompt_lower
        has_input = 'input' in self.prompt_lower or 'form' in self.prompt_lower
        has_timer = 'timer' in self.prompt_lower or 'pomodoro' in self.prompt_lower
        show_date = 'date' in self.prompt_lower
        show_time = 'time' in self.prompt_lower
        extract_emails = 'extract' in self.prompt_lower and 'email' in self.prompt_lower
        needs_content_interaction = self.requirements.get('needs_content_script', False)
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extension Popup</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Generated Extension</h1>
"""
        
        # Compact content: include extract button and generic action when relevant
        # Date/time displays (compact placement)
        if show_date:
            html += '        <div class="content"><h2>Today\'s Date</h2> <p id="date-display"></p></div>\n'

        if show_time:
            html += '        <div class="content"><h2>Current Time</h2> <p id="time-display"></p></div>\n'
        if extract_emails:
            html += (
                '        <div class="content"><h2>Email Extractor</h2>'
                ' <button id="extract-btn">Extract Emails</button>'
                ' <div id="email-list"></div><p id="email-count"></p></div>\n'
            )

        if has_button or needs_content_interaction:
            html += (
                '        <div class="content">'
                ' <button id="action-btn">Execute Action</button>'
                ' <p id="status"></p></div>\n'
            )

        # Minimal fallback
        if not (extract_emails or has_button or has_input or has_timer or show_date or show_time):
            html += '        <div class="content"><p>Extension is active.</p> <button id="action-btn">Click Me</button></div>\n'
        
        html += """    </div>
    <script src="popup.js"></script>
</body>
</html>"""
        
        return html
    
    def generate_popup_js(self):
        """Generate popup.js based on user prompt"""
        
        has_button = 'button' in self.prompt_lower or 'click' in self.prompt_lower
        has_timer = 'timer' in self.prompt_lower or 'pomodoro' in self.prompt_lower
        show_date = 'date' in self.prompt_lower
        show_time = 'time' in self.prompt_lower
        needs_content_interaction = self.requirements.get('needs_content_script', False)
        extract_emails = 'extract' in self.prompt_lower and 'email' in self.prompt_lower
        
        # Build a concise popup script that supports extract and execute actions
        js = (
            "// Popup script for generated extension\n"
            "document.addEventListener('DOMContentLoaded', function(){\n"
        )

        # Populate date/time if requested
        if show_date:
            js += (
                "    const dateDisplay = document.getElementById('date-display');\n"
                "    if(dateDisplay){ const today = new Date(); const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }; dateDisplay.textContent = today.toLocaleDateString('en-US', opts); }\n\n"
            )

        if show_time:
            js += (
                "    const timeDisplay = document.getElementById('time-display');\n"
                "    if(timeDisplay){ function updateTime(){ const now=new Date(); timeDisplay.textContent = now.toLocaleTimeString(); } updateTime(); setInterval(updateTime, 1000); }\n\n"
            )

        if extract_emails or has_button:
            js += (
                "    async function postToActiveTab(msg){\n"
                "        const [tab]=await chrome.tabs.query({active:true,currentWindow:true});\n"
                "        return new Promise(res=>chrome.tabs.sendMessage(tab.id,msg,res));\n"
                "    }\n\n"
            )

            if extract_emails:
                js += (
                    "    const extractBtn=document.getElementById('extract-btn');\n"
                    "    if(extractBtn){\n"
                    "        extractBtn.addEventListener('click',async()=>{\n"
                    "            const resp=await postToActiveTab({action:'getEmails'});\n"
                    "            const list=document.getElementById('email-list');\n"
                    "            const count=document.getElementById('email-count');\n"
                    "            if(resp&&resp.emails&&resp.emails.length){\n"
                    "                list.innerHTML='<ul style=\"text-align:left;margin-top:10px;\">'+resp.emails.map(e=>`<li style=\"padding:5px;word-break:break-all;\">${e}</li>`).join('')+'</ul>';\n"
                    "                count.textContent='Found '+resp.emails.length+' email(s)';\n"
                    "            }else{ list.innerHTML='<p style=\"margin-top:10px;\">No emails found on this page.</p>'; count.textContent=''; }\n"
                    "        });\n"
                    "    }\n\n"
                )

            # generic action button
            js += (
                "    const actionBtn=document.getElementById('action-btn');\n"
                "    if(actionBtn){\n"
                "        actionBtn.addEventListener('click',async()=>{\n"
                "            const resp=await postToActiveTab({action:'execute'});\n"
                "            const status=document.getElementById('status'); if(status) status.textContent=(resp&&resp.message)||'Action executed';\n"
                "        });\n"
                "    }\n\n"
            )

        js += "});\n"
        return js
    
    def generate_content_js(self):
        """Generate content.js based on user prompt"""
        # Compact content script: single listener handles actions
        js = """// Content script - runs on web pages

console.log('Content script loaded');

function extractEmails(){
    const re=/\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b/g;
    return (document.body.innerText.match(re)||[]);
}

chrome.runtime.onMessage.addListener(function(request,sender,sendResponse){
    if(request.action==='getEmails'){
        sendResponse({emails: extractEmails()});
    }else if(request.action==='execute'){
        // default execute behavior: change text color to blue
        document.querySelectorAll('body, body *').forEach(el=>{ try{ el.style.color='blue'; }catch(e){} });
        sendResponse({message:'Text color changed to blue!'});
    }
    return true;
});

// Auto-extract on load for debugging
console.log('Auto-extracted', extractEmails().length, 'emails from page');

"""
        return js
    
    def generate_background_js(self):
        """Generate background.js service worker"""
        
        block_sites = 'block' in self.prompt_lower
        timer = 'timer' in self.prompt_lower or 'alarm' in self.prompt_lower
        monitor = 'monitor' in self.prompt_lower or 'track' in self.prompt_lower
        
        js = """// Background service worker

console.log('Background service worker loaded');

"""
        
        # Site blocking logic
        if block_sites:
            blocked_sites = []
            if 'facebook' in self.prompt_lower:
                blocked_sites.append('*://*.facebook.com/*')
            if 'tiktok' in self.prompt_lower:
                blocked_sites.append('*://*.tiktok.com/*')
            if 'youtube' in self.prompt_lower:
                blocked_sites.append('*://*.youtube.com/*')
            
            if not blocked_sites:
                blocked_sites = ['*://example.com/*']
            
            js += f"""// Block specific websites
const blockedSites = {blocked_sites};

chrome.webRequest.onBeforeRequest.addListener(
    function(details) {{
        return {{ cancel: true }};
    }},
    {{ urls: blockedSites }},
    ["blocking"]
);

console.log('Blocking these sites:', blockedSites);

"""
        
        # Timer/Alarm functionality
        if timer:
            js += """// Timer alarm functionality
chrome.alarms.create('timerAlarm', {
    delayInMinutes: 25,
    periodInMinutes: 25
});

chrome.alarms.onAlarm.addListener(function(alarm) {
    if (alarm.name === 'timerAlarm') {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icon.png',
            title: 'Timer Alert',
            message: 'Time is up! Take a break.',
            priority: 2
        });
    }
});

"""
        
        # URL monitoring
        if monitor:
            js += """// Monitor and track URLs
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
    if (changeInfo.status === 'complete' && tab.url) {
        console.log('Visited URL:', tab.url);
        
        // Store in chrome.storage
        chrome.storage.local.get(['visitedUrls'], function(result) {
            const urls = result.visitedUrls || [];
            urls.push({
                url: tab.url,
                timestamp: new Date().toISOString()
            });
            chrome.storage.local.set({ visitedUrls: urls });
        });
    }
});

"""
        
        # Default background logic
        if not (block_sites or timer or monitor):
            js += """// Extension installation
chrome.runtime.onInstalled.addListener(function() {
    console.log('Extension installed successfully');
});

// Listen for messages from content scripts or popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log('Background received message:', request);
    sendResponse({ status: 'Message received by background' });
    return true;
});

"""
        
        return js
    
    def generate_styles_css(self):
        """Generate styles.css for popup"""
        
        css = """/* Styles for extension popup */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    width: 300px;
    min-height: 200px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
}

.container {
    padding: 20px;
}

h1 {
    font-size: 24px;
    margin-bottom: 15px;
    text-align: center;
}

h2 {
    font-size: 18px;
    margin-bottom: 10px;
}

.content {
    background: rgba(255, 255, 255, 0.1);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    backdrop-filter: blur(10px);
}

button {
    background: #fff;
    color: #667eea;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    margin: 5px;
    transition: all 0.3s ease;
}

button:hover {
    background: #f0f0f0;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

button:active {
    transform: translateY(0);
}

input[type="text"] {
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 5px;
    margin-bottom: 10px;
    font-size: 14px;
}

p {
    font-size: 16px;
    line-height: 1.5;
}

#date-display,
#time-display,
#timer-display {
    font-size: 20px;
    font-weight: 700;
    text-align: center;
    padding: 10px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 5px;
    margin: 10px 0;
}

#status {
    margin-top: 10px;
    font-size: 14px;
    text-align: center;
    font-style: italic;
}
"""
        
        return css
    
    def generate_all_files(self, output_dir="generated_extension"):
        """Generate all required files based on requirements"""
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        
        # If configured to use Gemini / LLM, try to ask it for the files directly
        if self.use_gemini and gemini_generate_files:
            try:
                files_map = gemini_generate_files(self.requirements, self.user_prompt)
                if not isinstance(files_map, dict):
                    raise RuntimeError('Gemini client returned an unexpected shape')

                for fname, content in files_map.items():
                    # Only write files we know we want (guards and whitelist)
                    if fname not in ('popup.html', 'popup.js', 'content.js', 'styles.css'):
                        continue
                    with open(os.path.join(output_dir, fname), 'w', encoding='utf-8') as f:
                        f.write(content)
                    generated_files.append(fname)

                # When using Gemini we skip local generation of the same files
                return generated_files
            except Exception as exc:
                # Don't crash the whole flow — fall back to default generator
                print('⚠️ Gemini generation failed, falling back to heuristic generator: ', exc)

        # Generate popup files
        if self.requirements.get('needs_popup', False):
            popup_html = self.generate_popup_html()
            popup_js = self.generate_popup_js()
            
            with open(os.path.join(output_dir, 'popup.html'), 'w', encoding='utf-8') as f:
                f.write(popup_html)
            generated_files.append('popup.html')
            
            with open(os.path.join(output_dir, 'popup.js'), 'w', encoding='utf-8') as f:
                f.write(popup_js)
            generated_files.append('popup.js')
        
        # Generate content script
        if self.requirements.get('needs_content_script', False):
            content_js = self.generate_content_js()
            with open(os.path.join(output_dir, 'content.js'), 'w', encoding='utf-8') as f:
                f.write(content_js)
            generated_files.append('content.js')
        
        # Generate background script
        if self.requirements.get('needs_background', False):
            background_js = self.generate_background_js()
            with open(os.path.join(output_dir, 'background.js'), 'w', encoding='utf-8') as f:
                f.write(background_js)
            generated_files.append('background.js')
        
        # Generate CSS
        if self.requirements.get('needs_css', False):
            styles_css = self.generate_styles_css()
            with open(os.path.join(output_dir, 'styles.css'), 'w', encoding='utf-8') as f:
                f.write(styles_css)
            generated_files.append('styles.css')
        
        return generated_files


if __name__ == "__main__":
    # Test the code generator
    print("Testing Code Generator...\n")
    
    # Test case 1: Popup with date
    test_requirements = {
        'needs_popup': True,
        'needs_content_script': False,
        'needs_background': False,
        'needs_css': True,
        'permissions': set()
    }
    
    generator = CodeGenerator(test_requirements, "Create an extension that shows a popup with today's date.")
    files = generator.generate_all_files("test_code_gen")
    
    print(f"Generated files: {', '.join(files)}")
    print("Check 'test_code_gen' folder for output")

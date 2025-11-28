"""
code_generator.py
Part C — Dynamic Code Generation

Generates HTML, JS, and CSS files based on analysis requirements
"""

import os


class CodeGenerator:
    """Generates code files for Chrome extension based on requirements"""
    
    def __init__(self, requirements, user_prompt):
        self.requirements = requirements
        self.user_prompt = user_prompt
        self.prompt_lower = user_prompt.lower()
    
    def generate_popup_html(self):
        """Generate popup.html based on user prompt"""
        
        # Detect what the popup should contain
        has_button = 'button' in self.prompt_lower or 'click' in self.prompt_lower
        has_input = 'input' in self.prompt_lower or 'form' in self.prompt_lower
        has_timer = 'timer' in self.prompt_lower or 'pomodoro' in self.prompt_lower
        show_date = 'date' in self.prompt_lower
        show_time = 'time' in self.prompt_lower
        extract_emails = 'extract' in self.prompt_lower and 'email' in self.prompt_lower
        
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
        
        # Add specific content based on prompt
        if show_date:
            html += """        <div class="content">
            <h2>Today's Date</h2>
            <p id="date-display"></p>
        </div>
"""
        
        if show_time:
            html += """        <div class="content">
            <h2>Current Time</h2>
            <p id="time-display"></p>
        </div>
"""
        
        if has_timer:
            html += """        <div class="content">
            <h2>Timer</h2>
            <p id="timer-display">25:00</p>
            <button id="start-timer">Start</button>
            <button id="stop-timer">Stop</button>
            <button id="reset-timer">Reset</button>
        </div>
"""
        
        if has_input:
            html += """        <div class="content">
            <input type="text" id="user-input" placeholder="Enter value...">
            <button id="submit-btn">Submit</button>
        </div>
"""
        
        if extract_emails:
            # Email extraction display area
            html += """        <div class="content">
            <h2>Email Extractor</h2>
            <button id="extract-btn">Extract Emails</button>
            <div id="email-list"></div>
            <p id="email-count"></p>
        </div>
"""
        
        if has_button and not has_input and not has_timer and not extract_emails:
            # Generic action button for content script interaction
            html += """        <div class="content">
            <button id="action-btn">Execute Action</button>
            <p id="status"></p>
        </div>
"""
        
        # Default content if nothing specific detected
        if not (show_date or show_time or has_timer or has_input or has_button or extract_emails):
            html += """        <div class="content">
            <p>Extension is active and ready!</p>
            <button id="action-btn">Click Me</button>
        </div>
"""
        
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
        
        js = """// Popup script for generated extension

document.addEventListener('DOMContentLoaded', function() {
"""
        
        # Date display logic
        if show_date:
            js += """    // Display today's date
    const dateDisplay = document.getElementById('date-display');
    if (dateDisplay) {
        const today = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateDisplay.textContent = today.toLocaleDateString('en-US', options);
    }

"""
        
        # Time display logic
        if show_time:
            js += """    // Display current time
    const timeDisplay = document.getElementById('time-display');
    if (timeDisplay) {
        function updateTime() {
            const now = new Date();
            timeDisplay.textContent = now.toLocaleTimeString();
        }
        updateTime();
        setInterval(updateTime, 1000);
    }

"""
        
        # Timer logic
        if has_timer:
            js += """    // Pomodoro Timer Logic
    let timerInterval;
    let timeLeft = 25 * 60; // 25 minutes in seconds
    
    const timerDisplay = document.getElementById('timer-display');
    const startBtn = document.getElementById('start-timer');
    const stopBtn = document.getElementById('stop-timer');
    const resetBtn = document.getElementById('reset-timer');
    
    function updateDisplay() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    if (startBtn) {
        startBtn.addEventListener('click', function() {
            if (!timerInterval) {
                timerInterval = setInterval(function() {
                    timeLeft--;
                    updateDisplay();
                    
                    if (timeLeft <= 0) {
                        clearInterval(timerInterval);
                        timerInterval = null;
                        alert('Time is up!');
                        timeLeft = 25 * 60;
                        updateDisplay();
                    }
                }, 1000);
            }
        });
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            clearInterval(timerInterval);
            timerInterval = null;
        });
    }
    
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            clearInterval(timerInterval);
            timerInterval = null;
            timeLeft = 25 * 60;
            updateDisplay();
        });
    }

"""
        
        # Email extraction logic
        if extract_emails:
            js += """    // Email extraction button
    const extractBtn = document.getElementById('extract-btn');
    if (extractBtn) {
        extractBtn.addEventListener('click', async function() {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            chrome.tabs.sendMessage(tab.id, { action: 'getEmails' }, function(response) {
                const emailList = document.getElementById('email-list');
                const emailCount = document.getElementById('email-count');
                
                if (response && response.emails && response.emails.length > 0) {
                    // Display emails as a list
                    let html = '<ul style="text-align: left; margin-top: 10px;">';
                    response.emails.forEach(function(email) {
                        html += '<li style="padding: 5px; word-break: break-all;">' + email + '</li>';
                    });
                    html += '</ul>';
                    emailList.innerHTML = html;
                    emailCount.textContent = 'Found ' + response.emails.length + ' email(s)';
                } else {
                    emailList.innerHTML = '<p style="margin-top: 10px;">No emails found on this page.</p>';
                    emailCount.textContent = '';
                }
            });
        });
    }

"""
        
        # Button interaction with content script
        if has_button and needs_content_interaction and not extract_emails:
            js += """    // Action button to interact with content script
    const actionBtn = document.getElementById('action-btn');
    if (actionBtn) {
        actionBtn.addEventListener('click', async function() {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            chrome.tabs.sendMessage(tab.id, { action: 'execute' }, function(response) {
                const status = document.getElementById('status');
                if (status) {
                    status.textContent = response ? response.message : 'Action executed!';
                }
            });
        });
    }

"""
        elif has_button and not needs_content_interaction:
            js += """    // Generic button click handler
    const actionBtn = document.getElementById('action-btn');
    if (actionBtn) {
        actionBtn.addEventListener('click', function() {
            const status = document.getElementById('status');
            if (status) {
                status.textContent = 'Button clicked!';
            }
            console.log('Action button clicked');
        });
    }

"""
        
        js += """});
"""
        
        return js
    
    def generate_content_js(self):
        """Generate content.js based on user prompt"""
        
        highlight_text = 'highlight' in self.prompt_lower
        phone_numbers = 'phone' in self.prompt_lower
        email = 'email' in self.prompt_lower
        change_color = 'color' in self.prompt_lower or 'blue' in self.prompt_lower
        extract = 'extract' in self.prompt_lower
        
        js = """// Content script - runs on web pages

console.log('Content script loaded');

"""
        
        # Highlight phone numbers
        if highlight_text and phone_numbers:
            js += """// Highlight all phone numbers on the page
function highlightPhoneNumbers() {
    const phoneRegex = /\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b/g;
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    const textNodes = [];
    while (walker.nextNode()) {
        if (walker.currentNode.parentNode.nodeName !== 'SCRIPT' && 
            walker.currentNode.parentNode.nodeName !== 'STYLE') {
            textNodes.push(walker.currentNode);
        }
    }
    
    textNodes.forEach(function(node) {
        const text = node.textContent;
        if (phoneRegex.test(text)) {
            const span = document.createElement('span');
            span.innerHTML = text.replace(phoneRegex, '<mark style="background-color: yellow; padding: 2px;">$&</mark>');
            node.parentNode.replaceChild(span, node);
        }
    });
}

highlightPhoneNumbers();

"""
        
        # Extract email addresses
        if extract and email:
            js += """// Extract all email addresses and send to popup
function extractEmails() {
    const emailRegex = /\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b/g;
    const bodyText = document.body.innerText;
    const emails = bodyText.match(emailRegex) || [];
    console.log('Found emails:', emails);
    return emails;
}

// Listen for requests from popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'getEmails') {
        const emails = extractEmails();
        sendResponse({ emails: emails });
    }
    return true;
});

// Auto-extract on page load
const foundEmails = extractEmails();
console.log('Extracted', foundEmails.length, 'emails from page');

"""
        
        # Change text color
        if change_color:
            js += """// Listen for messages from popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'execute') {
        // Change all text to blue
        document.querySelectorAll('*').forEach(function(element) {
            element.style.color = 'blue';
        });
        sendResponse({ message: 'Text color changed to blue!' });
    }
    return true;
});

"""
        
        # Generic content modification
        if not (highlight_text or extract or change_color):
            js += """// Generic content script functionality
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'execute') {
        console.log('Content script received message:', request);
        // Add your custom logic here
        sendResponse({ message: 'Content script executed successfully!' });
    }
    return true;
});

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

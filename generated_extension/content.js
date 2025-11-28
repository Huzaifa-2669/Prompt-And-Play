// Content script - runs on web pages

console.log('Content script loaded');

// Extract all email addresses and send to popup
function extractEmails() {
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
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


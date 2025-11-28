// Popup script for generated extension

document.addEventListener('DOMContentLoaded', function() {
    // Email extraction button
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

});

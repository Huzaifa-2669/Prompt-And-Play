// Content script - runs on web pages

console.log('Content script loaded');

function extractEmails(){
    const re=/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
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


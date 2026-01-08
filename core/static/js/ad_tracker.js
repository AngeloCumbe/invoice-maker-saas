// Ad Click Tracking System
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function trackAdClick(adId, placement, targetUrl, context = '', invoiceId = null) {
    const csrftoken = getCookie('csrftoken');
    
    fetch('/track-ad/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: new URLSearchParams({
            'ad_id': adId,
            'placement': placement,
            'target_url': targetUrl,
            'context': context,
            'invoice_id': invoiceId || ''
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Ad click tracked:', data);
    })
    .catch(error => {
        console.error('Error tracking ad click:', error);
    });
}

// Automatically attach tracking to all ad links
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.ad-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const container = this.closest('.ad-container');
            if (container) {
                const adId = container.dataset.adId;
                const placement = container.dataset.placement;
                const targetUrl = this.href;
                
                // Get invoice ID if available
                const invoiceId = container.dataset.invoiceId || null;
                
                trackAdClick(adId, placement, targetUrl, 'ad_click', invoiceId);
            }
        });
    });
});

// Track PDF download ad
window.trackPdfDownloadAd = function() {
    trackAdClick(
        'pdf-download-ad-001',
        'pdf_download',
        'https://example.com/pdf-tools',
        'before_pdf_download'
    );
};
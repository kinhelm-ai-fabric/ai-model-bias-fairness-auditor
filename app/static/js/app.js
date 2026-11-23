/* ── App JavaScript ── */

function _basePath() {
    var m = window.location.pathname.match(/^(\/preview\/[^/]+)/);
    return m ? m[1] : '';
}

function toggleTheme() {
    fetch(_basePath() + '/toggle-theme', { method: 'POST' })
        .then(function(resp) { return resp.json(); })
        .then(function(data) {
            document.documentElement.setAttribute('data-theme', data.theme);
        })
        .catch(function(err) {
            // Fallback: toggle client-side
            var current = document.documentElement.getAttribute('data-theme') || 'light';
            var next = current === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', next);
        });
}

function openHelp() {
    document.getElementById('helpOverlay').classList.add('active');
    document.getElementById('helpPanel').classList.add('active');
}

function closeHelp() {
    document.getElementById('helpOverlay').classList.remove('active');
    document.getElementById('helpPanel').classList.remove('active');
}

// Close help on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeHelp();
    }
});

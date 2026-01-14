document.getElementById('pdfFile').addEventListener('change', function(e) {
    const fileName = e.target.files[0]?.name || '';
    document.getElementById('fileName').textContent = fileName ? `✓ ${fileName}` : '';
});

function resetForm() {
    document.getElementById('uploadForm').reset();
    document.getElementById('fileName').textContent = '';
}

setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 300);
    });
}, 5000);
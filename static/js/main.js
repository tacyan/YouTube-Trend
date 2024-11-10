document.addEventListener('DOMContentLoaded', function() {
    // Search form handling with more defensive checks
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            const spinner = analyzeBtn.querySelector('.spinner-border');
            if (spinner) {
                searchForm.addEventListener('submit', function() {
                    analyzeBtn.disabled = true;
                    spinner.classList.remove('d-none');
                });
            }
        }
    }
    
    // Thumbnail preview handling
    const preview = document.getElementById('thumbnailPreview');
    if (preview) {
        const previewImg = preview.querySelector('img');
        
        document.querySelectorAll('.thumbnail-container img').forEach(img => {
            img.addEventListener('mouseenter', function(e) {
                const highRes = this.dataset.highRes;
                const title = this.dataset.videoTitle;
                
                if (previewImg) {
                    previewImg.src = highRes;
                    previewImg.alt = title;
                    
                    // Position the preview
                    const previewRect = preview.getBoundingClientRect();
                    const viewportWidth = window.innerWidth;
                    const viewportHeight = window.innerHeight;
                    
                    let left = e.clientX + 20;
                    let top = e.clientY + 20;
                    
                    // Adjust position if preview would go off screen
                    if (left + previewRect.width > viewportWidth) {
                        left = e.clientX - previewRect.width - 20;
                    }
                    if (top + previewRect.height > viewportHeight) {
                        top = e.clientY - previewRect.height - 20;
                    }
                    
                    preview.style.left = left + 'px';
                    preview.style.top = top + 'px';
                    preview.style.display = 'block';
                }
            });
            
            img.addEventListener('mouseleave', function() {
                preview.style.display = 'none';
            });
            
            // Update preview position on mouse move
            img.addEventListener('mousemove', function(e) {
                const previewRect = preview.getBoundingClientRect();
                const viewportWidth = window.innerWidth;
                const viewportHeight = window.innerHeight;
                
                let left = e.clientX + 20;
                let top = e.clientY + 20;
                
                if (left + previewRect.width > viewportWidth) {
                    left = e.clientX - previewRect.width - 20;
                }
                if (top + previewRect.height > viewportHeight) {
                    top = e.clientY - previewRect.height - 20;
                }
                
                preview.style.left = left + 'px';
                preview.style.top = top + 'px';
            });
        });
    }
    
    // Transcript handling
    document.querySelectorAll('.toggle-transcript').forEach(button => {
        button.addEventListener('click', async function() {
            const videoId = this.dataset.videoId;
            const textArea = this.nextElementSibling;
            
            if (textArea.classList.contains('d-none')) {
                textArea.classList.remove('d-none');
                this.textContent = '文字起こしを非表示';
                
                // Fetch transcript
                try {
                    const response = await fetch('/get_transcript/' + videoId);
                    const data = await response.json();
                    
                    // Remove timestamps from display
                    const cleanTranscript = data.transcript.replace(/\[\d{2}:\d{2}\]\s/g, '');
                    textArea.value = cleanTranscript;
                } catch (error) {
                    textArea.value = '文字起こしの読み込みに失敗しました';
                }
            } else {
                textArea.classList.add('d-none');
                this.textContent = '文字起こしを表示';
            }
        });
    });

    // Copy script functionality
    const copyScriptBtn = document.getElementById('copyScriptBtn');
    if (copyScriptBtn) {
        const scriptContent = document.querySelector('.script-content');
        if (scriptContent) {
            copyScriptBtn.addEventListener('click', async function() {
                try {
                    await navigator.clipboard.writeText(scriptContent.textContent);
                    this.textContent = 'コピーしました！';
                    setTimeout(() => {
                        this.textContent = 'スクリプトをコピー';
                    }, 2000);
                } catch (err) {
                    this.textContent = 'コピーに失敗しました';
                    setTimeout(() => {
                        this.textContent = 'スクリプトをコピー';
                    }, 2000);
                }
            });
        }
    }
});

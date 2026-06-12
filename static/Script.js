/**
 * ScribeAI - Client-side Interactive Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // Determine which page we are on
    const generatorForm = document.getElementById('generator-form');
    const historyGrid = document.getElementById('history-grid');

    if (generatorForm) {
        initGenerator();
    }
    
    if (historyGrid || document.getElementById('history-empty')) {
        initHistory();
    }

    // Common setup: chip selections
    setupChips();
});

/**
 * Handle custom radio-button chips selection
 */
function setupChips() {
    const chips = document.querySelectorAll('.type-chips .chip');
    chips.forEach(chip => {
        chip.addEventListener('click', function() {
            // Remove active from all in the same group
            chips.forEach(c => c.classList.remove('active'));
            // Add active to current
            this.classList.add('active');
            // Check the radio input inside
            const radio = this.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });
}

/**
 * Simple Markdown Parser to render HTML in output viewer
 */
function parseMarkdown(mdText) {
    if (!mdText) return '';
    
    let html = mdText
        // Escape HTML entities to prevent XSS
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Headings
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Bullet points (handle lines starting with - or *)
    const lines = html.split('\n');
    let inList = false;
    let listHtml = [];

    for (let line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            const content = trimmed.substring(2);
            if (!inList) {
                listHtml.push('<ul>');
                inList = true;
            }
            listHtml.push(`<li>${content}</li>`);
        } else {
            if (inList) {
                listHtml.push('</ul>');
                inList = false;
            }
            // Add paragraph tags for normal non-empty text lines that aren't header tags
            if (trimmed && !trimmed.startsWith('<h') && !trimmed.startsWith('</h') && !trimmed.startsWith('<ul') && !trimmed.startsWith('</ul') && !trimmed.startsWith('<li')) {
                listHtml.push(`<p>${line}</p>`);
            } else {
                listHtml.push(line);
            }
        }
    }
    if (inList) {
        listHtml.push('</ul>');
    }

    return listHtml.join('\n');
}

/**
 * PAGE 1: GENERATOR CONTROLLER
 */
function initGenerator() {
    const form = document.getElementById('generator-form');
    const generateBtn = document.getElementById('generate-btn');
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const contentViewer = document.getElementById('content-viewer');
    const textContent = document.getElementById('generated-text-content');
    const errorState = document.getElementById('error-state');
    const errorMessage = document.getElementById('error-message');
    const outputActions = document.getElementById('output-actions');
    const ragVisualizer = document.getElementById('rag-visualizer');
    const ragSourcesList = document.getElementById('rag-sources-list');
    
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');

    let currentGeneratedText = '';
    let currentTopic = '';
    let currentType = '';

    // Message cycler during loading
    let loadingInterval = null;
    function startLoadingAnimation() {
        const messages = document.querySelectorAll('.loading-messages p');
        let index = 0;
        
        messages.forEach(m => m.classList.remove('active'));
        messages[0].classList.add('active');

        loadingInterval = setInterval(() => {
            messages[index].classList.remove('active');
            index = (index + 1) % messages.length;
            messages[index].classList.add('active');
        }, 3000);
    }

    function stopLoadingAnimation() {
        if (loadingInterval) {
            clearInterval(loadingInterval);
            loadingInterval = null;
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const topic = document.getElementById('topic').value.trim();
        const content_type = form.querySelector('input[name="content_type"]:checked').value;
        const tone = document.getElementById('tone').value;
        const keywords = document.getElementById('keywords').value.trim();

        currentTopic = topic;
        currentType = content_type;

        // Reset UI States
        emptyState.classList.add('hidden');
        contentViewer.classList.add('hidden');
        errorState.classList.add('hidden');
        outputActions.classList.add('hidden');
        ragVisualizer.classList.add('hidden');
        
        // Show Loading
        loadingState.classList.remove('hidden');
        generateBtn.disabled = true;
        generateBtn.querySelector('span').innerText = 'Generating...';
        startLoadingAnimation();

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, content_type, tone, keywords })
            });
            const result = await response.json();

            stopLoadingAnimation();
            loadingState.classList.add('hidden');
            generateBtn.disabled = false;
            generateBtn.querySelector('span').innerText = 'Generate Content';

            if (result.success) {
                currentGeneratedText = result.content;
                
                // Render content (HTML markdown)
                textContent.innerHTML = parseMarkdown(result.content);
                contentViewer.classList.remove('hidden');
                outputActions.classList.remove('hidden');

                // Render RAG sources if any
                if (result.rag_sources && result.rag_sources.length > 0) {
                    ragSourcesList.innerHTML = '';
                    result.rag_sources.forEach(source => {
                        const item = document.createElement('div');
                        item.className = 'rag-source-item';
                        item.innerHTML = `
                            <div class="rag-source-meta">
                                <span class="badge badge-secondary">${source.content_type}</span>
                                <span>${source.timestamp}</span>
                            </div>
                            <div class="rag-source-title">${source.topic}</div>
                        `;
                        ragSourcesList.appendChild(item);
                    });
                    ragVisualizer.classList.remove('hidden');
                }
            } else {
                errorMessage.innerText = result.error || 'Failed to generate content. Please try again.';
                errorState.classList.remove('hidden');
            }
        } catch (err) {
            stopLoadingAnimation();
            loadingState.classList.add('hidden');
            generateBtn.disabled = false;
            generateBtn.querySelector('span').innerText = 'Generate Content';
            
            errorMessage.innerText = 'Unable to connect to the server. Make sure the backend Flask app is running.';
            errorState.classList.remove('hidden');
            console.error(err);
        }
    });

    // Copy Content Actions
    copyBtn.addEventListener('click', () => {
        if (!currentGeneratedText) return;
        navigator.clipboard.writeText(currentGeneratedText).then(() => {
            const origHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            copyBtn.disabled = true;
            setTimeout(() => {
                copyBtn.innerHTML = origHTML;
                copyBtn.disabled = false;
            }, 2000);
        });
    });

    // Download Content Actions
    downloadBtn.addEventListener('click', () => {
        if (!currentGeneratedText) return;
        const blob = new Blob([currentGeneratedText], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const safeName = currentTopic.toLowerCase().replace(/[^a-z0-9]+/g, '_').substring(0, 30);
        a.download = `${safeName}_${currentType.toLowerCase().replace(' ', '_')}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
}

/**
 * PAGE 2: HISTORY CONTROLLER
 */
function initHistory() {
    const historyLoading = document.getElementById('history-loading');
    const historyEmpty = document.getElementById('history-empty');
    const historyGrid = document.getElementById('history-grid');
    const searchInput = document.getElementById('search-input');
    const filterChips = document.querySelectorAll('.filter-chip');
    const clearAllBtn = document.getElementById('clear-all-btn');

    // Modal elements
    const modal = document.getElementById('content-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalType = document.getElementById('modal-type');
    const modalTone = document.getElementById('modal-tone');
    const modalDate = document.getElementById('modal-date');
    const modalBodyContent = document.getElementById('modal-body-content');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalBackdrop = document.getElementById('modal-backdrop');
    const modalCopyBtn = document.getElementById('modal-copy-btn');
    const modalDownloadBtn = document.getElementById('modal-download-btn');

    let historyData = [];
    let activeFilter = 'all';
    let activeSearch = '';
    let currentModalText = '';
    let currentModalTitle = '';
    let currentModalType = '';

    // Load history from API
    async function loadHistory() {
        historyLoading.classList.remove('hidden');
        historyGrid.classList.add('hidden');
        historyEmpty.classList.add('hidden');
        clearAllBtn.classList.add('hidden');

        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            historyData = data;
            
            historyLoading.classList.add('hidden');
            
            if (historyData.length === 0) {
                historyEmpty.classList.remove('hidden');
            } else {
                clearAllBtn.classList.remove('hidden');
                renderHistory();
            }
        } catch (err) {
            historyLoading.classList.add('hidden');
            console.error('Failed to load history', err);
        }
    }

    // Render history grid items based on filters
    function renderHistory() {
        historyGrid.innerHTML = '';
        
        const filtered = historyData.filter(item => {
            // Filter by type
            let matchesType = true;
            if (activeFilter !== 'all') {
                matchesType = item.content_type.toLowerCase().includes(activeFilter.toLowerCase());
            }

            // Filter by search text
            let matchesSearch = true;
            if (activeSearch) {
                const searchLower = activeSearch.toLowerCase();
                matchesSearch = item.topic.toLowerCase().includes(searchLower) || 
                                item.generated_content.toLowerCase().includes(searchLower) ||
                                (item.keywords && item.keywords.toLowerCase().includes(searchLower));
            }

            return matchesType && matchesSearch;
        });

        if (filtered.length === 0) {
            historyGrid.classList.add('hidden');
            historyEmpty.classList.remove('hidden');
            return;
        }

        historyEmpty.classList.add('hidden');
        historyGrid.classList.remove('hidden');

        filtered.forEach(item => {
            const card = document.createElement('div');
            card.className = 'card history-card';
            
            const cleanText = item.generated_content.replace(/[#*`_-]/g, '').substring(0, 160);
            
            card.innerHTML = `
                <div class="history-card-meta">
                    <span class="badge badge-success">${item.content_type}</span>
                    <span class="badge badge-secondary">${item.tone}</span>
                </div>
                <h3 class="history-card-title">${item.topic}</h3>
                <p class="history-card-preview">${cleanText}...</p>
                <div class="history-card-footer">
                    <span class="history-card-date"><i class="fa-regular fa-clock"></i> ${item.timestamp}</span>
                    <button class="btn btn-secondary btn-sm card-view-btn"><i class="fa-regular fa-eye"></i> View</button>
                </div>
            `;

            card.addEventListener('click', () => {
                openModal(item);
            });

            historyGrid.appendChild(card);
        });
    }

    // Modal Control functions
    function openModal(item) {
        currentModalText = item.generated_content;
        currentModalTitle = item.topic;
        currentModalType = item.content_type;

        modalTitle.innerText = item.topic;
        modalType.innerText = item.content_type;
        modalTone.innerText = item.tone;
        modalDate.innerHTML = `<i class="fa-solid fa-calendar-days"></i> Generated on: ${item.timestamp}`;
        modalBodyContent.innerHTML = parseMarkdown(item.generated_content);
        
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // lock scroll
    }

    function closeModal() {
        modal.classList.add('hidden');
        document.body.style.overflow = ''; // unlock scroll
    }

    modalCloseBtn.addEventListener('click', closeModal);
    modalBackdrop.addEventListener('click', closeModal);

    modalCopyBtn.addEventListener('click', () => {
        if (!currentModalText) return;
        navigator.clipboard.writeText(currentModalText).then(() => {
            const origHTML = modalCopyBtn.innerHTML;
            modalCopyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            modalCopyBtn.disabled = true;
            setTimeout(() => {
                modalCopyBtn.innerHTML = origHTML;
                modalCopyBtn.disabled = false;
            }, 2000);
        });
    });

    modalDownloadBtn.addEventListener('click', () => {
        if (!currentModalText) return;
        const blob = new Blob([currentModalText], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const safeName = currentModalTitle.toLowerCase().replace(/[^a-z0-9]+/g, '_').substring(0, 30);
        a.download = `${safeName}_${currentModalType.toLowerCase().replace(' ', '_')}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    searchInput.addEventListener('input', (e) => {
        activeSearch = e.target.value;
        renderHistory();
    });

    filterChips.forEach(chip => {
        chip.addEventListener('click', function() {
            filterChips.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            activeFilter = this.getAttribute('data-type');
            renderHistory();
        });
    });

    clearAllBtn.addEventListener('click', async () => {
        if (confirm('Are you absolutely sure you want to clear your entire content archive and vector store? This cannot be undone.')) {
            try {
                const response = await fetch('/api/clear', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    historyData = [];
                    renderHistory();
                } else {
                    alert('Error clearing history: ' + result.error);
                }
            } catch (err) {
                alert('Connection error. Failed to clear history.');
                console.error(err);
            }
        }
    });

    loadHistory();
}
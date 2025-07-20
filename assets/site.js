// ============================================================================
// MATHJAX MANAGEMENT
// ============================================================================

/**
 * Processa i blocchi matematici MathJax per distinguere tra display e inline
 */
function processMathBlocks() {
    // Verifica che ci siano contenitori MathJax da processare
    const mathContainers = document.querySelectorAll('mjx-container.MathJax');
    if (mathContainers.length === 0) {
        console.log('Nessun contenitore MathJax trovato');
        return;
    }
    
    // Trova tutti i contenitori MathJax
    mathContainers.forEach(function(mathContainer) {
        // Controlla se contiene un elemento mjx-mspace
        if(!mathContainer.classList.contains("math-display") && !mathContainer.classList.contains("math-inline")){
            const mspaceElements = mathContainer.querySelectorAll('mjx-mspace');
            
            if(mspaceElements.length){
                const br = document.createElement('br');
                mathContainer.parentNode.insertBefore(br, mathContainer);
                mathContainer.classList.add('math-display');

                mspaceElements.forEach(function(mspace) {
                    const br = document.createElement('br');
                    mspace.parentNode.replaceChild(br, mspace);
                });
            }
            else{
                mathContainer.classList.add('math-inline');
            }
        }
    });
}

/**
 * Configura i blocchi matematici aspettando che MathJax sia pronto
 */
function setupMathBlocks() {
    // Aspetta che MathJax abbia finito il rendering
    if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
        MathJax.startup.promise.then(function() {
            processMathBlocks();
        }).catch(function(error) {
            console.log('MathJax startup error:', error);
            // Prova comunque a processare i blocchi math
            setTimeout(processMathBlocks, 2000);
        });
    } else {
        // Fallback se MathJax non è ancora caricato o non ha la promise
        setTimeout(processMathBlocks, 2000);
    }
}

// ============================================================================
// PRISM CODE HIGHLIGHTING
// ============================================================================

/**
 * Configura Prism per la colorazione dei blocchi di codice
 */
function setupPrismCodeBlocks() {
    // Trova tutti i div con classe language-*
    document.querySelectorAll('div[class*="language-"]').forEach(function(div) {
        const languageClass = Array.from(div.classList).find(cls => cls.startsWith('language-'));
        if (languageClass) {
            const codeElement = div.querySelector('code');
            if (codeElement && !codeElement.classList.contains(languageClass)) {
                codeElement.classList.add(languageClass);
            }
        }
    });
    
    // Crea un alias per x86asm che usa la grammatica NASM
    if (window.Prism && Prism.languages.nasm) {
        Prism.languages.x86asm = Prism.languages.nasm;
    }

    // Riapplica Prism dopo aver aggiunto le classi
    if (window.Prism) {
        Prism.highlightAll();
    }
}

// ============================================================================
// DYNAMIC HEADER MANAGEMENT
// ============================================================================

/**
 * Gestisce il comportamento dinamico dell'header durante lo scroll
 */
function setupDynamicHeader() {
    let lastScrollY = window.scrollY;
    let isScrollingDown = false;
    let ticking = false;
    
    const header = document.querySelector('.site-header');
    
    if (!header) {
        console.warn('Header non trovato');
        return;
    }
    
    function updateHeader() {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > lastScrollY && currentScrollY > 100) {
            // Scrolling down - hide header
            if (!isScrollingDown) {
                header.classList.add('hidden');
                header.classList.remove('visible');
                isScrollingDown = true;
            }
        } else if (currentScrollY < lastScrollY) {
            // Scrolling up - show header
            if (isScrollingDown || currentScrollY > 50) {
                header.classList.remove('hidden');
                header.classList.add('visible');
                isScrollingDown = false;
            }
        }
        
        // Se siamo in cima alla pagina, rimuovi tutte le classi
        if (currentScrollY <= 50) {
            header.classList.remove('hidden', 'visible');
            isScrollingDown = false;
        }
        
        lastScrollY = currentScrollY;
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateHeader);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick);
}

// ============================================================================
// MATHJAX CONFIGURATION
// ============================================================================

/**
 * Configurazione MathJax
 */
window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true,
        processRefs: true,
        tags: 'none'
    },
    options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
        processHtmlClass: 'tex2jax_process',
        ignoreHtmlClass: 'tex2jax_ignore'
    },
    chtml: {
        displayAlign: 'center',
        displayIndent: '0em'
    },
    startup: {
        ready() {
            MathJax.startup.defaultReady();
            
            // Hook per processare il contenuto dopo il rendering
            const originalTypesetPromise = MathJax.typesetPromise;
            MathJax.typesetPromise = function(elements) {
                return originalTypesetPromise.call(this, elements).then(function() {
                    // Dopo che MathJax ha fatto il rendering, applica le nostre correzioni
                    if (window.processMathBlocks) {
                        window.processMathBlocks();
                    }
                });
            };
        }
    }
};

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Inizializzazione principale del sito
 */
function initializeSite() {
    // Esponi le funzioni globalmente per compatibilità
    window.processMathBlocks = processMathBlocks;
    
    // Configura i blocchi di codice Prism
    setupPrismCodeBlocks();
    
    // Configura i blocchi matematici MathJax
    setupMathBlocks();
    
    // Configura l'header dinamico
    setupDynamicHeader();
}

// Avvia l'inizializzazione quando il DOM è pronto
document.addEventListener('DOMContentLoaded', initializeSite);

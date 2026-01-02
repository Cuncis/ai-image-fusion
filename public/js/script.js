// State management
let state = {
    apiKey: '',
    personImage: null,
    productImage: null
};

// DOM Elements
const apiKeyInput = document.getElementById('apiKey');
const apiStatus = document.getElementById('apiStatus');
const personUpload = document.getElementById('personUpload');
const productUpload = document.getElementById('productUpload');
const personInput = document.getElementById('personInput');
const productInput = document.getElementById('productInput');
const personPreview = document.getElementById('personPreview');
const productPreview = document.getElementById('productPreview');
const personImg = document.getElementById('personImg');
const productImg = document.getElementById('productImg');
const removePerson = document.getElementById('removePerson');
const removeProduct = document.getElementById('removeProduct');
const mergeButton = document.getElementById('mergeButton');
const setupSection = document.getElementById('setupSection');
const resultSection = document.getElementById('resultSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const resultImage = document.getElementById('resultImage');
const aiAnalysis = document.getElementById('aiAnalysis');
const downloadBtn = document.getElementById('downloadBtn');
const newMergeBtn = document.getElementById('newMergeBtn');

// API Key handling
apiKeyInput.addEventListener('input', (e) => {
    state.apiKey = e.target.value.trim();
    updateAPIStatus();
    updateMergeButton();
});

function updateAPIStatus() {
    if (state.apiKey) {
        apiStatus.textContent = 'Connected';
        apiStatus.classList.add('connected');
    } else {
        apiStatus.textContent = 'Not Connected';
        apiStatus.classList.remove('connected');
    }
}

// File upload handling
personUpload.addEventListener('click', () => personInput.click());
productUpload.addEventListener('click', () => productInput.click());

personInput.addEventListener('change', (e) => handleFileSelect(e, 'person'));
productInput.addEventListener('change', (e) => handleFileSelect(e, 'product'));

// Drag and drop
[personUpload, productUpload].forEach(area => {
    area.addEventListener('dragover', handleDragOver);
    area.addEventListener('dragleave', handleDragLeave);
});

personUpload.addEventListener('drop', (e) => handleDrop(e, 'person'));
productUpload.addEventListener('drop', (e) => handleDrop(e, 'product'));

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e, type) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0], type);
    }
}

function handleFileSelect(e, type) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file, type);
    }
}

function handleFile(file, type) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
        if (type === 'person') {
            state.personImage = e.target.result;
            personImg.src = e.target.result;
            personUpload.style.display = 'none';
            personPreview.style.display = 'block';
        } else {
            state.productImage = e.target.result;
            productImg.src = e.target.result;
            productUpload.style.display = 'none';
            productPreview.style.display = 'block';
        }
        updateMergeButton();
    };
    reader.readAsDataURL(file);
}

// Remove image
removePerson.addEventListener('click', () => removeImage('person'));
removeProduct.addEventListener('click', () => removeImage('product'));

function removeImage(type) {
    if (type === 'person') {
        state.personImage = null;
        personUpload.style.display = 'flex';
        personPreview.style.display = 'none';
        personInput.value = '';
    } else {
        state.productImage = null;
        productUpload.style.display = 'flex';
        productPreview.style.display = 'none';
        productInput.value = '';
    }
    updateMergeButton();
}

// Update merge button state
function updateMergeButton() {
    const canMerge = state.apiKey && state.personImage && state.productImage;
    mergeButton.disabled = !canMerge;
}

// Merge images
mergeButton.addEventListener('click', async () => {
    if (!state.apiKey || !state.personImage || !state.productImage) {
        return;
    }
    
    showLoading('Analyzing images with AI...');
    
    try {
        updateLoadingText('Analyzing images with AI...');
        
        // Send base64 images to API
        const response = await fetch('/api/merge', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                person_image: state.personImage,
                product_image: state.productImage,
                api_key: state.apiKey
            })
        });
        
        updateLoadingText('Creating composite image...');
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Merge failed');
        }
        
        const result = await response.json();
        
        updateLoadingText('Finalizing result...');
        
        // Show result
        setTimeout(() => {
            hideLoading();
            showResult(result);
        }, 500);
        
    } catch (error) {
        hideLoading();
        alert('Error: ' + error.message + '\n\nPlease check:\n1. Your API key is valid\n2. Images are not too large\n3. You have internet connection');
    }
});

function showLoading(text) {
    loadingText.textContent = text;
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

function updateLoadingText(text) {
    loadingText.textContent = text;
}

function showResult(result) {
    resultImage.src = result.image;
    aiAnalysis.textContent = result.settings.description || result.analysis || 'Successfully merged images!';
    
    setupSection.style.display = 'none';
    resultSection.style.display = 'block';
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// Download result
downloadBtn.addEventListener('click', () => {
    const link = document.createElement('a');
    link.href = resultImage.src;
    link.download = 'merged-image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

// New merge
newMergeBtn.addEventListener('click', () => {
    // Reset state
    removeImage('person');
    removeImage('product');
    
    // Show setup section
    setupSection.style.display = 'block';
    resultSection.style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Initialize
updateAPIStatus();
updateMergeButton();

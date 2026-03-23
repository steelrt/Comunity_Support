// ============ SERVICE DATA ============
const servicesData = [
    {
        id: 1,
        title: 'Online Government Services',
        icon: '🏛️',
        description: 'Access essential public services efficiently online.',
        link: '/services/government'
    },
    {
        id: 2,
        title: 'Digital Identity & Security',
        icon: '🔐',
        description: 'Securely manage your digital identification.',
        link: '/services/digital-identity'
    },
    {
        id: 3,
        title: 'Citizen Engagement Initiatives',
        icon: '🤝',
        description: 'Participate in local civic initiatives.',
        link: '/services/engagement'
    }
];

// ============ LOAD SERVICES ============
function loadServices() {
    const grid = document.getElementById('servicesGrid');
    grid.innerHTML = servicesData.map(service => `
        <div class="service-card" onclick="openService('${service.link}')">
            <div class="service-icon">${service.icon}</div>
            <h3>${service.title}</h3>
            <p>${service.description}</p>
            <button class="btn btn-primary">Learn More →</button>
        </div>
    `).join('');
}

// ============ CHATBOT FUNCTIONS ============
function toggleChatbot() {
    const container = document.getElementById('chatbotContainer');
    container.style.display = container.style.display === 'none' ? 'flex' : 'none';
}

function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;

    // Add user message to chat
    addMessageToChat('user', message);
    input.value = '';

    // Send to backend
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        addMessageToChat('bot', data.response);
    })
    .catch(err => {
        console.error('Error:', err);
        addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
    });
}

function addMessageToChat(sender, text) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = `<div class="message-text">${escapeHtml(text)}</div>`;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============ NAVIGATION ============
function scrollToServices() {
    document.getElementById('services-anchor').scrollIntoView({ behavior: 'smooth' });
}

function openService(link) {
    // In production: window.location.href = link;
    alert('Opening: ' + link + '\n\nIn production, this would load the service page.');
}

function showServiceCategory(category) {
    alert('Showing ' + category + ' services...');
}

// ============ INITIALIZE ============
document.addEventListener('DOMContentLoaded', function() {
    loadServices();
});

// static/js/main.js

// Web3 initialization
let web3;
let userAccount;
let votingContract;

// Contract ABI (simplified version)
const contractABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "age", "type": "uint256"}],
        "name": "registerVoter",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_electionId", "type": "uint256"},
            {"internalType": "uint256", "name": "_candidateId", "type": "uint256"}
        ],
        "name": "vote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_electionId", "type": "uint256"}],
        "name": "isVotingTime",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
];

// Initialize Web3
async function initWeb3() {
    if (typeof window.ethereum !== 'undefined') {
        web3 = new Web3(window.ethereum);
        try {
            await window.ethereum.request({ method: 'eth_requestAccounts' });
            const accounts = await web3.eth.getAccounts();
            userAccount = accounts[0];
            console.log('Connected account:', userAccount);
            return true;
        } catch (error) {
            console.error('User denied account access:', error);
            return false;
        }
    } else {
        console.log('MetaMask not detected');
        alert('Please install MetaMask to use blockchain features!');
        return false;
    }
}

// Connect wallet
async function connectWallet() {
    const connected = await initWeb3();
    if (connected) {
        const walletInput = document.getElementById('ethereum_address');
        if (walletInput) {
            walletInput.value = userAccount;
        }
        alert('Wallet connected successfully!');
    }
}

// Check if MetaMask is installed
function checkMetaMask() {
    if (typeof window.ethereum === 'undefined') {
        const metaMaskWarning = document.createElement('div');
        metaMaskWarning.className = 'alert alert-warning';
        metaMaskWarning.innerHTML = `
            <p>⚠️ MetaMask not detected. Please install MetaMask to use blockchain features.</p>
            <a href="https://metamask.io/download/" target="_blank" class="btn btn-primary">Install MetaMask</a>
        `;
        document.body.insertBefore(metaMaskWarning, document.body.firstChild);
    }
}

// Listen for account changes
if (typeof window.ethereum !== 'undefined') {
    window.ethereum.on('accountsChanged', function (accounts) {
        userAccount = accounts[0];
        console.log('Account changed to:', userAccount);
        location.reload();
    });

    window.ethereum.on('chainChanged', function (chainId) {
        console.log('Chain changed to:', chainId);
        location.reload();
    });
}

// Form validation
function validateRegistrationForm() {
    const form = document.getElementById('registerForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        const age = parseInt(document.getElementById('age').value);
        const password1 = document.getElementById('password1').value;
        const password2 = document.getElementById('password2').value;
        const ethereumAddress = document.getElementById('ethereum_address').value;

        if (age < 18) {
            e.preventDefault();
            alert('You must be 18 or older to register.');
            return false;
        }

        if (password1 !== password2) {
            e.preventDefault();
            alert('Passwords do not match!');
            return false;
        }

        if (!ethereumAddress.startsWith('0x') || ethereumAddress.length !== 42) {
            e.preventDefault();
            alert('Please enter a valid Ethereum address.');
            return false;
        }
    });
}

// Auto-dismiss alerts
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
}

// Voting time checker
function checkVotingTime(startHour, endHour) {
    const now = new Date();
    const currentHour = now.getHours();
    return currentHour >= startHour && currentHour <= endHour;
}

// Real-time voting status
function updateVotingStatus() {
    const statusElements = document.querySelectorAll('[data-voting-status]');
    statusElements.forEach(element => {
        const isOpen = checkVotingTime(9, 17);
        if (isOpen) {
            element.textContent = '🟢 Voting is OPEN';
            element.className = 'badge badge-success';
        } else {
            element.textContent = '🔴 Voting is CLOSED';
            element.className = 'badge badge-danger';
        }
    });
}

// Countdown timer
function startCountdown(targetDate) {
    const countdownElement = document.getElementById('countdown');
    if (!countdownElement) return;

    setInterval(() => {
        const now = new Date().getTime();
        const distance = new Date(targetDate).getTime() - now;

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        countdownElement.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;

        if (distance < 0) {
            countdownElement.innerHTML = "Election Ended";
        }
    }, 1000);
}

// Smooth scrolling
function smoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Animation on scroll
function animateOnScroll() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out';
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    document.querySelectorAll('.feature-card, .election-card, .step').forEach(el => {
        observer.observe(el);
    });
}

// Add fadeInUp animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    checkMetaMask();
    validateRegistrationForm();
    autoDismissAlerts();
    smoothScroll();
    animateOnScroll();
    updateVotingStatus();

    // Update voting status every minute
    setInterval(updateVotingStatus, 60000);
});

// Export functions for use in templates
window.connectWallet = connectWallet;
window.initWeb3 = initWeb3;


/* ============================================
   INSTALLATION AND SETUP INSTRUCTIONS
   ============================================

1. CREATE DJANGO PROJECT:
   ```bash
   django-admin startproject voting_system
   cd voting_system
   python manage.py startapp voting_app
   ```

2. INSTALL REQUIRED PACKAGES:
   ```bash
   pip install django pillow web3
   ```

3. CREATE DIRECTORY STRUCTURE:
   ```
   voting_system/
   ├── voting_system/
   │   ├── settings.py
   │   ├── urls.py
   │   └── wsgi.py
   ├── voting_app/
   │   ├── models.py
   │   ├── views.py
   │   ├── urls.py
   │   ├── forms.py
   │   └── admin.py
   ├── templates/
   │   ├── base.html
   │   ├── home.html
   │   ├── register.html
   │   ├── login.html
   │   ├── dashboard.html
   │   ├── election_detail.html
   │   └── results.html
   ├── static/
   │   ├── css/
   │   │   └── style.css
   │   └── js/
   │       └── main.js
   └── media/
       └── candidates/
   ```

4. UPDATE settings.py:
   - Add 'voting_app' to INSTALLED_APPS
   - Configure TEMPLATES dirs
   - Set STATIC_URL and STATICFILES_DIRS
   - Set MEDIA_URL and MEDIA_ROOT
   - Configure database (default SQLite is fine for development)

5. RUN MIGRATIONS:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. CREATE SUPERUSER:
   ```bash
   python manage.py createsuperuser
   ```

7. CREATE MEDIA FOLDER:
   ```bash
   mkdir -p media/candidates
   ```

8. RUN DEVELOPMENT SERVER:
   ```bash
   python manage.py runserver
   ```

9. ACCESS THE APPLICATION:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

10. DEPLOY SMART CONTRACT (Optional):
    - Install Truffle: `npm install -g truffle`
    - Compile contract: `truffle compile`
    - Deploy to testnet (Sepolia/Goerli)
    - Update contract address in Election model

11. METAMASK SETUP:
    - Install MetaMask browser extension
    - Create/import wallet
    - Get testnet ETH from faucet
    - Connect to appropriate network

12. CREATE FIRST ELECTION (Admin Panel):
    - Login to admin panel
    - Create an Election with:
      * Title
      * Description
      * Start/End dates
      * Voting hours (9 AM - 5 PM by default)

13. FEATURES IMPLEMENTED:
    ✅ User registration (18+ only)
    ✅ Candidate profiles
    ✅ Stand for election option
    ✅ Time-restricted voting (9 AM - 5 PM)
    ✅ Ethereum blockchain integration
    ✅ Vote recording with transaction hash
    ✅ Real-time results
    ✅ Responsive design
    ✅ MetaMask wallet integration

14. SECURITY NOTES:
    - Use environment variables for sensitive data
    - Enable CSRF protection (Django default)
    - Use HTTPS in production
    - Implement rate limiting
    - Add email verification
    - Secure private keys properly

15. PRODUCTION DEPLOYMENT:
    - Set DEBUG = False
    - Configure allowed hosts
    - Use PostgreSQL database
    - Set up proper static file serving
    - Use gunicorn/uwsgi
    - Configure nginx
    - Enable SSL/TLS
    - Set up proper logging

============================================ */
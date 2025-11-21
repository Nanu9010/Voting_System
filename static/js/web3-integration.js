class MetaMaskIntegration {
    constructor() {
        this.web3 = null;
        this.contract = null;
        this.userAccount = null;
        this.contractAddress = 'YOUR_CONTRACT_ADDRESS'; // Replace with deployed contract
        this.contractABI = []; // Your contract ABI will go here
        
        this.init();
    }

    async init() {
        if (typeof window.ethereum !== 'undefined') {
            this.web3 = new Web3(window.ethereum);
            await this.loadContract();
        } else {
            this.showMetaMaskAlert();
        }
    }

    async loadContract() {
        try {
            // Load contract ABI (you'll need to replace this with your actual ABI)
            const response = await fetch('/static/contracts/Voting.json');
            const contractData = await response.json();
            this.contractABI = contractData.abi;
            
            this.contract = new this.web3.eth.Contract(this.contractABI, this.contractAddress);
            console.log('Contract loaded successfully');
        } catch (error) {
            console.error('Error loading contract:', error);
            this.showError('Failed to load voting contract');
        }
    }

    async connectMetaMask() {
        try {
            // Request account access
            const accounts = await window.ethereum.request({
                method: 'eth_requestAccounts'
            });
            
            this.userAccount = accounts[0];
            console.log('Connected account:', this.userAccount);
            
            // Update UI
            this.updateUIWithAccount();
            
            // Check if user is registered
            await this.checkVoterRegistration();
            
            return this.userAccount;
        } catch (error) {
            console.error('User denied account access:', error);
            this.showError('Please connect MetaMask to continue');
            return null;
        }
    }

    async checkVoterRegistration() {
        try {
            const isRegistered = await this.contract.methods.registeredVoters(this.userAccount).call();
            if (!isRegistered) {
                this.showRegistrationPrompt();
            }
            return isRegistered;
        } catch (error) {
            console.error('Error checking registration:', error);
            return false;
        }
    }

    async registerVoter(age) {
        try {
            const gasEstimate = await this.contract.methods.registerVoter(age).estimateGas({
                from: this.userAccount
            });

            const transaction = await this.contract.methods.registerVoter(age).send({
                from: this.userAccount,
                gas: gasEstimate
            });

            console.log('Registration successful:', transaction);
            this.showSuccess('Voter registration successful!');
            return transaction;
        } catch (error) {
            console.error('Registration failed:', error);
            this.showError('Voter registration failed: ' + error.message);
            throw error;
        }
    }

    async registerCandidate(name, manifesto, age, email) {
        try {
            const gasEstimate = await this.contract.methods.registerCandidate(
                name, manifesto, age, email
            ).estimateGas({
                from: this.userAccount
            });

            const transaction = await this.contract.methods.registerCandidate(
                name, manifesto, age, email
            ).send({
                from: this.userAccount,
                gas: gasEstimate
            });

            console.log('Candidate registration successful:', transaction);
            this.showSuccess('Candidate registration submitted! Waiting for admin approval.');
            return transaction;
        } catch (error) {
            console.error('Candidate registration failed:', error);
            this.showError('Candidate registration failed: ' + error.message);
            throw error;
        }
    }

    async castVote(electionId, candidateId) {
        try {
            // First check if user can vote
            const canVote = await this.canVote(electionId);
            if (!canVote) {
                throw new Error('You are not eligible to vote in this election');
            }

            const gasEstimate = await this.contract.methods.vote(electionId, candidateId).estimateGas({
                from: this.userAccount
            });

            const transaction = await this.contract.methods.vote(electionId, candidateId).send({
                from: this.userAccount,
                gas: gasEstimate
            });

            console.log('Vote cast successfully:', transaction);
            this.showSuccess('Vote cast successfully! Transaction: ' + transaction.transactionHash);
            return transaction;
        } catch (error) {
            console.error('Vote casting failed:', error);
            this.showError('Vote failed: ' + error.message);
            throw error;
        }
    }

    async canVote(electionId) {
        try {
            const [isRegistered, hasVoted, isVotingTime] = await Promise.all([
                this.contract.methods.registeredVoters(this.userAccount).call(),
                this.contract.methods.hasVoted(electionId, this.userAccount).call(),
                this.contract.methods.isVotingTime(electionId).call()
            ]);

            return isRegistered && !hasVoted && isVotingTime;
        } catch (error) {
            console.error('Error checking voting eligibility:', error);
            return false;
        }
    }

    async getElectionDetails(electionId) {
        try {
            return await this.contract.methods.getElection(electionId).call();
        } catch (error) {
            console.error('Error getting election details:', error);
            throw error;
        }
    }

    async getCandidateDetails(candidateId) {
        try {
            return await this.contract.methods.getCandidate(candidateId).call();
        } catch (error) {
            console.error('Error getting candidate details:', error);
            throw error;
        }
    }

    async getApprovedCandidates() {
        try {
            const candidateIds = await this.contract.methods.getApprovedCandidates().call();
            const candidates = [];
            
            for (const candidateId of candidateIds) {
                const candidate = await this.getCandidateDetails(candidateId);
                candidates.push({
                    id: candidateId,
                    ...candidate
                });
            }
            
            return candidates;
        } catch (error) {
            console.error('Error getting approved candidates:', error);
            throw error;
        }
    }

    async getElectionResults(electionId) {
        try {
            const [candidateIds, votes] = await this.contract.methods.getElectionResults(electionId).call();
            const results = [];
            
            for (let i = 0; i < candidateIds.length; i++) {
                const candidate = await this.getCandidateDetails(candidateIds[i]);
                results.push({
                    candidate: candidate,
                    votes: votes[i]
                });
            }
            
            return results;
        } catch (error) {
            console.error('Error getting election results:', error);
            throw error;
        }
    }

    // UI Update methods
    updateUIWithAccount() {
        const accountElements = document.querySelectorAll('.user-account');
        accountElements.forEach(element => {
            element.textContent = this.formatAddress(this.userAccount);
            element.title = this.userAccount;
        });

        // Show blockchain features
        document.querySelectorAll('.blockchain-feature').forEach(el => {
            el.style.display = 'block';
        });
    }

    formatAddress(address) {
        return address.substring(0, 6) + '...' + address.substring(address.length - 4);
    }

    showMetaMaskAlert() {
        const alertHTML = `
            <div class="alert alert-warning">
                <h4>MetaMask Required</h4>
                <p>Please install MetaMask to use blockchain features.</p>
                <a href="https://metamask.io/download.html" target="_blank" class="btn btn-primary">
                    Install MetaMask
                </a>
            </div>
        `;
        document.getElementById('alerts-container').innerHTML = alertHTML;
    }

    showRegistrationPrompt() {
        const promptHTML = `
            <div class="alert alert-info">
                <h4>Complete Your Registration</h4>
                <p>You need to register as a voter to participate in elections.</p>
                <button onclick="showVoterRegistrationModal()" class="btn btn-success">
                    Register as Voter
                </button>
            </div>
        `;
        document.getElementById('alerts-container').innerHTML += promptHTML;
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'error');
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="close" onclick="this.parentElement.remove()">&times;</button>
        `;
        document.getElementById('alerts-container').appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Listen for account changes
    setupEventListeners() {
        if (window.ethereum) {
            window.ethereum.on('accountsChanged', (accounts) => {
                this.userAccount = accounts[0];
                this.updateUIWithAccount();
                this.checkVoterRegistration();
            });

            window.ethereum.on('chainChanged', (chainId) => {
                // Reload the page when network changes
                window.location.reload();
            });
        }
    }
}

// Initialize MetaMask integration
let metaMask;

document.addEventListener('DOMContentLoaded', function() {
    metaMask = new MetaMaskIntegration();
    metaMask.setupEventListeners();
});

// Global functions for HTML onclick events
async function connectWallet() {
    if (metaMask) {
        return await metaMask.connectMetaMask();
    }
    return null;
}

async function castVote(electionId, candidateId, candidateName) {
    if (!metaMask.userAccount) {
        await connectWallet();
    }
    
    try {
        await metaMask.castVote(electionId, candidateId);
        // Update UI to show voted status
        document.getElementById(`candidate-${candidateId}`).style.opacity = '0.5';
        document.querySelector(`#candidate-${candidateId} .vote-btn`).disabled = true;
        document.querySelector(`#candidate-${candidateId} .vote-btn`).textContent = 'Voted ✓';
    } catch (error) {
        console.error('Vote failed:', error);
    }
}
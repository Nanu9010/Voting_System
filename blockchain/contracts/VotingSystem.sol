// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DecentralizedVoting {
    struct Candidate {
        uint256 id;
        string name;
        string manifesto;
        uint256 voteCount;
        bool isApproved;
        uint256 age;
        string email;
    }
    
    struct Election {
        uint256 id;
        string title;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 votingStartHour; // 9 AM = 9
        uint256 votingEndHour;   // 5 PM = 17
        bool isActive;
        bool candidacyRegistrationOpen;
        bool votingOpen;
        address[] candidates;
        mapping(address => bool) hasVoted;
        uint256 totalVotes;
    }
    
    address public admin;
    uint256 public electionCount;
    uint256 public candidateCount;
    
    mapping(uint256 => Election) public elections;
    mapping(uint256 => Candidate) public candidates;
    mapping(address => uint256) public voterAge;
    mapping(address => bool) public registeredVoters;
    mapping(address => uint256) public candidateToId;
    
    event VoterRegistered(address indexed voter, uint256 age);
    event CandidateRegistered(uint256 indexed candidateId, string name, string manifesto);
    event CandidateApproved(uint256 indexed candidateId, bool approved);
    event VoteCast(uint256 indexed electionId, address indexed voter, uint256 candidateId);
    event ElectionCreated(uint256 indexed electionId, string title);
    event VotingStatusChanged(uint256 indexed electionId, bool votingOpen);
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }
    
    modifier onlyRegisteredVoter() {
        require(registeredVoters[msg.sender], "Voter not registered");
        require(voterAge[msg.sender] >= 18, "Must be 18 or older to vote");
        _;
    }
    
    constructor() {
        admin = msg.sender;
        electionCount = 0;
        candidateCount = 0;
    }
    
    // Register voter with age verification
    function registerVoter(uint256 _age) public {
        require(_age >= 18, "Must be 18 or older to register");
        require(!registeredVoters[msg.sender], "Already registered");
        
        registeredVoters[msg.sender] = true;
        voterAge[msg.sender] = _age;
        
        emit VoterRegistered(msg.sender, _age);
    }
    
    // Register as candidate (requires admin approval)
    function registerCandidate(
        string memory _name,
        string memory _manifesto,
        uint256 _age,
        string memory _email
    ) public onlyRegisteredVoter {
        require(_age >= 18, "Must be 18 or older to be candidate");
        
        candidateCount++;
        candidates[candidateCount] = Candidate({
            id: candidateCount,
            name: _name,
            manifesto: _manifesto,
            voteCount: 0,
            isApproved: false,
            age: _age,
            email: _email
        });
        
        candidateToId[msg.sender] = candidateCount;
        
        emit CandidateRegistered(candidateCount, _name, _manifesto);
    }
    
    // Admin approve candidate
    function approveCandidate(uint256 _candidateId, bool _approved) public onlyAdmin {
        require(_candidateId > 0 && _candidateId <= candidateCount, "Invalid candidate ID");
        candidates[_candidateId].isApproved = _approved;
        
        emit CandidateApproved(_candidateId, _approved);
    }
    
    // Create election (admin only)
    function createElection(
        string memory _title,
        string memory _description,
        uint256 _startTime,
        uint256 _endTime
    ) public onlyAdmin {
        electionCount++;
        Election storage newElection = elections[electionCount];
        
        newElection.id = electionCount;
        newElection.title = _title;
        newElection.description = _description;
        newElection.startTime = _startTime;
        newElection.endTime = _endTime;
        newElection.votingStartHour = 9;  // 9 AM
        newElection.votingEndHour = 17;   // 5 PM
        newElection.isActive = true;
        newElection.candidacyRegistrationOpen = true;
        newElection.votingOpen = true;
        newElection.totalVotes = 0;
        
        emit ElectionCreated(electionCount, _title);
    }
    
    // Check if voting is allowed based on time
    function isVotingTime(uint256 _electionId) public view returns (bool) {
        Election storage election = elections[_electionId];
        
        if (!election.isActive || !election.votingOpen) return false;
        if (block.timestamp < election.startTime || block.timestamp > election.endTime) return false;
        
        // Check if current hour is between 9 AM and 5 PM
        uint256 currentHour = (block.timestamp / 3600) % 24;
        return currentHour >= election.votingStartHour && currentHour <= election.votingEndHour;
    }
    
    // Cast vote
    function vote(uint256 _electionId, uint256 _candidateId) public onlyRegisteredVoter {
        require(_electionId > 0 && _electionId <= electionCount, "Invalid election ID");
        Election storage election = elections[_electionId];
        
        require(election.isActive && election.votingOpen, "Election is not active");
        require(!election.hasVoted[msg.sender], "You have already voted");
        require(isVotingTime(_electionId), "Voting is only allowed between 9 AM and 5 PM");
        require(_candidateId > 0 && _candidateId <= candidateCount, "Invalid candidate ID");
        require(candidates[_candidateId].isApproved, "Candidate is not approved");
        
        election.hasVoted[msg.sender] = true;
        candidates[_candidateId].voteCount++;
        election.totalVotes++;
        
        emit VoteCast(_electionId, msg.sender, _candidateId);
    }
    
    // Get candidate details
    function getCandidate(uint256 _candidateId) public view returns (
        uint256 id,
        string memory name,
        string memory manifesto,
        uint256 voteCount,
        bool isApproved,
        uint256 age,
        string memory email
    ) {
        require(_candidateId > 0 && _candidateId <= candidateCount, "Invalid candidate ID");
        Candidate memory candidate = candidates[_candidateId];
        
        return (
            candidate.id,
            candidate.name,
            candidate.manifesto,
            candidate.voteCount,
            candidate.isApproved,
            candidate.age,
            candidate.email
        );
    }
    
    // Get election details
    function getElection(uint256 _electionId) public view returns (
        uint256 id,
        string memory title,
        string memory description,
        uint256 startTime,
        uint256 endTime,
        bool isActive,
        bool votingOpen,
        uint256 totalVotes
    ) {
        require(_electionId > 0 && _electionId <= electionCount, "Invalid election ID");
        Election storage election = elections[_electionId];
        
        return (
            election.id,
            election.title,
            election.description,
            election.startTime,
            election.endTime,
            election.isActive,
            election.votingOpen,
            election.totalVotes
        );
    }
    
    // Check if voter has voted in election
    function hasVoted(uint256 _electionId, address _voter) public view returns (bool) {
        require(_electionId > 0 && _electionId <= electionCount, "Invalid election ID");
        return elections[_electionId].hasVoted[_voter];
    }
    
    // Admin functions
    function toggleElectionStatus(uint256 _electionId, bool _isActive) public onlyAdmin {
        elections[_electionId].isActive = _isActive;
    }
    
    function toggleVotingStatus(uint256 _electionId, bool _votingOpen) public onlyAdmin {
        elections[_electionId].votingOpen = _votingOpen;
        emit VotingStatusChanged(_electionId, _votingOpen);
    }
    
    function toggleCandidacyRegistration(uint256 _electionId, bool _registrationOpen) public onlyAdmin {
        elections[_electionId].candidacyRegistrationOpen = _registrationOpen;
    }
    
    // Get all approved candidates
    function getApprovedCandidates() public view returns (uint256[] memory) {
        uint256 approvedCount = 0;
        
        // First count approved candidates
        for (uint256 i = 1; i <= candidateCount; i++) {
            if (candidates[i].isApproved) {
                approvedCount++;
            }
        }
        
        // Create array of approved candidate IDs
        uint256[] memory approvedCandidates = new uint256[](approvedCount);
        uint256 currentIndex = 0;
        
        for (uint256 i = 1; i <= candidateCount; i++) {
            if (candidates[i].isApproved) {
                approvedCandidates[currentIndex] = i;
                currentIndex++;
            }
        }
        
        return approvedCandidates;
    }
    
    // Get election results
    function getElectionResults(uint256 _electionId) public view returns (uint256[] memory, uint256[] memory) {
        require(_electionId > 0 && _electionId <= electionCount, "Invalid election ID");
        
        uint256[] memory candidateIds = getApprovedCandidates();
        uint256[] memory votes = new uint256[](candidateIds.length);
        
        for (uint256 i = 0; i < candidateIds.length; i++) {
            votes[i] = candidates[candidateIds[i]].voteCount;
        }
        
        return (candidateIds, votes);
    }
}
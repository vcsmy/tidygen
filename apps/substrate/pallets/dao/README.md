# DAO (Decentralized Autonomous Organization) Pallet

A comprehensive Substrate pallet for on-chain governance with proposals, voting, and execution.

## Overview

This pallet provides decentralized governance functionality for the TidyGen ERP system, allowing community members to propose, vote on, and execute business decisions on-chain.

## Features

- ✅ **Proposal Creation**: Submit governance proposals with title and description
- ✅ **Democratic Voting**: One account, one vote (yes/no)
- ✅ **Proposal Execution**: Execute approved proposals on-chain
- ✅ **Lifecycle Management**: Active → Approved/Rejected → Executed
- ✅ **Voting Period**: Configurable voting periods (10-1000 blocks)
- ✅ **Deposit System**: Proposal deposits (refunded on execution)
- ✅ **Comprehensive Tests**: 15+ test cases covering full lifecycle

## Data Structures

### Proposal

```rust
struct Proposal {
    id: u64,                          // Unique proposal ID
    proposer: AccountId,              // Proposal creator
    title: BoundedVec<u8>,           // Proposal title
    description: BoundedVec<u8>,     // Proposal description
    created_at: BlockNumber,          // Creation block
    voting_start: BlockNumber,        // Voting start block
    voting_end: BlockNumber,          // Voting end block
    status: ProposalStatus,           // Current status
    votes_for: u64,                   // Yes votes
    votes_against: u64,               // No votes
    total_votes: u64,                 // Total votes cast
    executed: bool,                   // Execution status
    executed_at: Option<BlockNumber>, // Execution block
}
```

### ProposalStatus

```rust
enum ProposalStatus {
    Active,      // Accepting votes
    Approved,    // Passed, ready for execution
    Rejected,    // Failed to pass
    Executed,    // Successfully executed
    Cancelled,   // Cancelled by proposer
    Expired,     // Voting period expired
}
```

## Storage

### Proposals

Map of proposal ID to proposal data:
```rust
Proposals: map ProposalId => Proposal
```

### Votes

Double map for vote storage:
```rust
Votes: double_map (ProposalId, AccountId) => bool
```

- `true` = vote in favor
- `false` = vote against

### HasVoted

Track voting participation:
```rust
HasVoted: double_map (ProposalId, AccountId) => bool
```

### ProposalCount

Global proposal counter:
```rust
ProposalCount: u64
```

## Extrinsics

### create_proposal

Create a new governance proposal.

```rust
create_proposal(
    origin: OriginFor<T>,
    title: Vec<u8>,
    description: Vec<u8>,
    voting_period: Option<BlockNumber>
) -> DispatchResult
```

**Parameters:**
- `origin`: Transaction signer (proposer)
- `title`: Proposal title (max 256 bytes)
- `description`: Proposal description (max 2048 bytes)
- `voting_period`: Voting duration in blocks (10-1000, default 10)

**Example:**
```javascript
// Polkadot.js
await api.tx.dao.createProposal(
    'Approve Q4 Budget',
    'Proposal to approve Q4 2025 budget allocation of $50,000',
    100  // 100 blocks voting period
).signAndSend(alice);
```

```python
# Python (Django)
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="ws://127.0.0.1:9944")
keypair = Keypair.create_from_uri('//Alice')

call = substrate.compose_call(
    call_module='Dao',
    call_function='create_proposal',
    call_params={
        'title': 'Approve Q4 Budget',
        'description': 'Proposal to approve Q4 2025 budget allocation',
        'voting_period': 100
    }
)

extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
```

### vote

Cast a vote on a proposal.

```rust
vote(
    origin: OriginFor<T>,
    proposal_id: u64,
    in_favor: bool
) -> DispatchResult
```

**Parameters:**
- `origin`: Transaction signer (voter)
- `proposal_id`: ID of proposal to vote on
- `in_favor`: `true` for yes, `false` for no

**Example:**
```javascript
// Vote in favor
await api.tx.dao.vote(0, true).signAndSend(bob);

// Vote against
await api.tx.dao.vote(0, false).signAndSend(charlie);
```

```python
# Python
call = substrate.compose_call(
    call_module='Dao',
    call_function='vote',
    call_params={
        'proposal_id': 0,
        'in_favor': True
    }
)
```

### execute_proposal

Execute an approved proposal after voting ends.

```rust
execute_proposal(
    origin: OriginFor<T>,
    proposal_id: u64
) -> DispatchResult
```

**Parameters:**
- `origin`: Transaction signer (executor)
- `proposal_id`: ID of proposal to execute

**Requirements:**
- Voting period must have ended
- Proposal must be approved (votes_for > votes_against)
- Proposal not already executed

**Example:**
```javascript
await api.tx.dao.executeProposal(0).signAndSend(alice);
```

### close_proposal

Close a proposal after voting period (finalizes status).

```rust
close_proposal(
    origin: OriginFor<T>,
    proposal_id: u64
) -> DispatchResult
```

### cancel_proposal

Cancel a proposal (only proposer, before voting ends).

```rust
cancel_proposal(
    origin: OriginFor<T>,
    proposal_id: u64
) -> DispatchResult
```

## Events

### ProposalCreated

```rust
ProposalCreated {
    proposal_id: u64,
    proposer: AccountId,
    title: Vec<u8>,
}
```

### VoteCast

```rust
VoteCast {
    proposal_id: u64,
    voter: AccountId,
    in_favor: bool,
}
```

### ProposalExecuted

```rust
ProposalExecuted {
    proposal_id: u64,
    executor: AccountId,
}
```

### ProposalStatusChanged

```rust
ProposalStatusChanged {
    proposal_id: u64,
    old_status: ProposalStatus,
    new_status: ProposalStatus,
}
```

### ProposalClosed

```rust
ProposalClosed {
    proposal_id: u64,
    final_status: ProposalStatus,
}
```

### VotingEnded

```rust
VotingEnded {
    proposal_id: u64,
    approved: bool,
}
```

## Complete Governance Workflow

### Phase 1: Proposal Creation

```rust
// 1. Create proposal
create_proposal(
    origin,
    "Approve New Feature",
    "Proposal to add blockchain analytics dashboard",
    100  // 100 block voting period
)

// Status: Active
// Votes: 0 for, 0 against
```

### Phase 2: Voting Period

```rust
// 2. Community members vote
vote(origin, proposal_id, true)   // Alice votes yes
vote(origin, proposal_id, true)   // Bob votes yes
vote(origin, proposal_id, false)  // Charlie votes no
vote(origin, proposal_id, true)   // Dave votes yes

// Status: Active
// Votes: 3 for, 1 against (75% approval)
```

### Phase 3: Close Voting

```rust
// 3. After voting period ends, close proposal
close_proposal(origin, proposal_id)

// Status: Approved (because votes_for > votes_against)
// Ready for execution
```

### Phase 4: Execution

```rust
// 4. Execute approved proposal
execute_proposal(origin, proposal_id)

// Status: Executed
// Proposal implementation proceeds
```

## Django Integration

### Create Proposal from Django

```python
# apps/backend/apps/web3/services/dao_service.py

from substrateinterface import SubstrateInterface, Keypair
import json

class DaoService:
    """Service for DAO operations on Substrate blockchain"""
    
    def __init__(self):
        self.substrate = SubstrateInterface(
            url="ws://127.0.0.1:9944",
            ss58_format=42
        )
        self.keypair = Keypair.create_from_uri('//Alice')
    
    def create_proposal(self, title, description, voting_period_blocks=100):
        """Create governance proposal on blockchain"""
        call = self.substrate.compose_call(
            call_module='Dao',
            call_function='create_proposal',
            call_params={
                'title': title,
                'description': description,
                'voting_period': voting_period_blocks
            }
        )
        
        extrinsic = self.substrate.create_signed_extrinsic(
            call=call,
            keypair=self.keypair
        )
        
        receipt = self.substrate.submit_extrinsic(
            extrinsic,
            wait_for_inclusion=True
        )
        
        return receipt.extrinsic_hash
    
    def vote_on_proposal(self, proposal_id, in_favor, voter_keypair):
        """Cast vote on proposal"""
        call = self.substrate.compose_call(
            call_module='Dao',
            call_function='vote',
            call_params={
                'proposal_id': proposal_id,
                'in_favor': in_favor
            }
        )
        
        extrinsic = self.substrate.create_signed_extrinsic(
            call=call,
            keypair=voter_keypair
        )
        
        receipt = self.substrate.submit_extrinsic(
            extrinsic,
            wait_for_inclusion=True
        )
        
        return receipt.extrinsic_hash
    
    def get_proposal(self, proposal_id):
        """Get proposal details"""
        result = self.substrate.query(
            module='Dao',
            storage_function='Proposals',
            params=[proposal_id]
        )
        return result.value
    
    def get_vote(self, proposal_id, voter_account):
        """Get vote for an account"""
        result = self.substrate.query(
            module='Dao',
            storage_function='Votes',
            params=[proposal_id, voter_account]
        )
        return result.value
    
    def execute_proposal(self, proposal_id):
        """Execute approved proposal"""
        call = self.substrate.compose_call(
            call_module='Dao',
            call_function='execute_proposal',
            call_params={'proposal_id': proposal_id}
        )
        
        extrinsic = self.substrate.create_signed_extrinsic(
            call=call,
            keypair=self.keypair
        )
        
        receipt = self.substrate.submit_extrinsic(
            extrinsic,
            wait_for_inclusion=True
        )
        
        return receipt.extrinsic_hash
```

### Django Model Integration

```python
# apps/backend/apps/web3/models.py

from django.db import models
from apps.core.models import BaseModel

class DAOProposal(BaseModel):
    """Django model for DAO proposals (synced with blockchain)"""
    
    # Blockchain reference
    proposal_id = models.BigIntegerField(unique=True)
    blockchain_tx_hash = models.CharField(max_length=66)
    
    # Proposal data
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=2048)
    proposer = models.ForeignKey(User, on_delete=models.CASCADE)
    proposer_wallet = models.CharField(max_length=48)
    
    # Voting info
    voting_start_block = models.BigIntegerField()
    voting_end_block = models.BigIntegerField()
    votes_for = models.BigIntegerField(default=0)
    votes_against = models.BigIntegerField(default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('executed', 'Executed'),
            ('cancelled', 'Cancelled'),
        ],
        default='active'
    )
    executed = models.BooleanField(default=False)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    def sync_from_blockchain(self):
        """Sync proposal data from blockchain"""
        from apps.web3.services.dao_service import DaoService
        
        dao = DaoService()
        blockchain_proposal = dao.get_proposal(self.proposal_id)
        
        if blockchain_proposal:
            self.votes_for = blockchain_proposal['votes_for']
            self.votes_against = blockchain_proposal['votes_against']
            self.status = blockchain_proposal['status'].lower()
            self.executed = blockchain_proposal['executed']
            self.save()
    
    @property
    def approval_percentage(self):
        total = self.votes_for + self.votes_against
        if total == 0:
            return 0
        return (self.votes_for / total) * 100


class DAOVote(BaseModel):
    """Django model for DAO votes"""
    
    proposal = models.ForeignKey(DAOProposal, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    voter_wallet = models.CharField(max_length=48)
    in_favor = models.BooleanField()
    blockchain_tx_hash = models.CharField(max_length=66)
    
    class Meta:
        unique_together = ['proposal', 'voter']
```

### Django Views Integration

```python
# apps/backend/apps/web3/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DAOProposal, DAOVote
from .services.dao_service import DaoService

class DAOProposalViewSet(viewsets.ModelViewSet):
    """ViewSet for DAO proposals"""
    queryset = DAOProposal.objects.all()
    
    @action(detail=False, methods=['post'])
    def create_blockchain_proposal(self, request):
        """Create proposal on both Django and blockchain"""
        title = request.data.get('title')
        description = request.data.get('description')
        voting_period = request.data.get('voting_period', 100)
        
        # Create on blockchain
        dao = DaoService()
        tx_hash = dao.create_proposal(title, description, voting_period)
        
        # Create in Django
        proposal = DAOProposal.objects.create(
            title=title,
            description=description,
            proposer=request.user,
            proposer_wallet=request.user.wallet_address,
            blockchain_tx_hash=tx_hash,
            voting_period_blocks=voting_period
        )
        
        return Response({
            'proposal_id': proposal.id,
            'blockchain_tx_hash': tx_hash,
            'status': 'active'
        })
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote on proposal"""
        proposal = self.get_object()
        in_favor = request.data.get('in_favor', True)
        
        # Vote on blockchain
        dao = DaoService()
        voter_keypair = Keypair.create_from_uri(f'//{request.user.username}')
        tx_hash = dao.vote_on_proposal(
            proposal.proposal_id,
            in_favor,
            voter_keypair
        )
        
        # Record in Django
        vote = DAOVote.objects.create(
            proposal=proposal,
            voter=request.user,
            voter_wallet=request.user.wallet_address,
            in_favor=in_favor,
            blockchain_tx_hash=tx_hash
        )
        
        # Sync proposal data
        proposal.sync_from_blockchain()
        
        return Response({
            'vote_id': vote.id,
            'blockchain_tx_hash': tx_hash,
            'in_favor': in_favor
        })
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute approved proposal"""
        proposal = self.get_object()
        
        # Execute on blockchain
        dao = DaoService()
        tx_hash = dao.execute_proposal(proposal.proposal_id)
        
        # Update Django
        proposal.executed = True
        proposal.status = 'executed'
        proposal.save()
        
        return Response({
            'blockchain_tx_hash': tx_hash,
            'status': 'executed'
        })
```

## Tests

The pallet includes 15 comprehensive test cases:

1. ✅ `create_proposal_works` - Basic proposal creation
2. ✅ `vote_in_favor_works` - Voting yes
3. ✅ `vote_against_works` - Voting no
4. ✅ `multiple_votes_work` - Multiple voters
5. ✅ `cannot_vote_twice` - Duplicate vote prevention
6. ✅ `execute_approved_proposal_works` - Proposal execution
7. ✅ `cannot_execute_before_voting_ends` - Premature execution
8. ✅ `cannot_execute_rejected_proposal` - Rejected proposal
9. ✅ `close_proposal_works` - Proposal closing (approved)
10. ✅ `close_rejected_proposal_works` - Proposal closing (rejected)
11. ✅ `full_proposal_lifecycle_approved` - Complete lifecycle
12. ✅ `full_proposal_lifecycle_rejected` - Rejection flow
13. ✅ `multiple_proposals_work` - Multiple proposals
14. ✅ `cannot_vote_on_nonexistent_proposal` - Error handling
15. ✅ `approval_percentage_calculation_works` - Percentage calc
16. ✅ `cancel_proposal_works` - Cancellation
17. ✅ `only_proposer_can_cancel` - Authorization
18. ✅ `cannot_execute_twice` - Double execution prevention
19. ✅ `title_too_long_fails` - Validation
20. ✅ `description_too_long_fails` - Validation
21. ✅ `voting_period_validation_works` - Period validation
22. ✅ `unanimous_approval_works` - 100% approval
23. ✅ `tie_vote_rejects_proposal` - Tie handling
24. ✅ `events_are_emitted_correctly` - Event verification

### Running Tests

```bash
# Test all
cargo test -p pallet-dao

# Test with output
cargo test -p pallet-dao -- --nocapture

# Specific test
cargo test -p pallet-dao full_proposal_lifecycle
```

## Configuration

```rust
// In runtime/src/lib.rs
impl pallet_dao::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type MaxTitleLength = ConstU32<256>;
    type MaxDescriptionLength = ConstU32<2048>;
    type MinVotingPeriod = ConstU32<100>;        // ~10 minutes (6 sec blocks)
    type MaxVotingPeriod = ConstU32<201600>;     // ~2 weeks
    type ProposalDeposit = ConstU128<1000000>;   // 1 token
}

// Add to construct_runtime!
construct_runtime!(
    pub enum Runtime {
        // ... other pallets
        Dao: pallet_dao,
    }
);
```

## Use Cases

### 1. Budget Approval

```javascript
// Propose budget
await api.tx.dao.createProposal(
    'Q4 2025 Budget',
    'Approve budget allocation: Engineering $30k, Marketing $15k, Operations $10k',
    14400  // ~1 day voting
).signAndSend(cfo);

// Team votes
await api.tx.dao.vote(0, true).signAndSend(ceo);
await api.tx.dao.vote(0, true).signAndSend(manager);
await api.tx.dao.vote(0, true).signAndSend(teamLead);

// Execute if approved
await api.tx.dao.executeProposal(0).signAndSend(cfo);
```

### 2. Feature Approval

```python
# Django - Feature request voting
dao = DaoService()

# Create proposal
tx_hash = dao.create_proposal(
    title="Add Mobile App",
    description="Develop iOS and Android mobile applications",
    voting_period_blocks=28800  # ~2 days
)

# Users vote via Django API
for user in stakeholders:
    dao.vote_on_proposal(
        proposal_id=0,
        in_favor=user.preference,
        voter_keypair=user.get_keypair()
    )
```

### 3. Freelancer Gig Approval

```python
# Approve high-value gigs via DAO
def approve_high_value_gig(gig):
    if gig.budget > 10000:
        # Create DAO proposal
        dao = DaoService()
        tx_hash = dao.create_proposal(
            title=f"Approve Gig: {gig.title}",
            description=f"Budget: ${gig.budget}, Duration: {gig.duration}",
            voting_period_blocks=7200  # ~12 hours
        )
        
        gig.dao_proposal_id = proposal_id
        gig.requires_dao_approval = True
        gig.save()
```

## Voting Mechanisms

### Simple Majority (Current Implementation)

- **Rule**: `votes_for > votes_against`
- **Example**: 6 yes, 4 no → Approved (60%)
- **Tie**: 5 yes, 5 no → Rejected (requires majority)

### Future Enhancements

#### Token-Weighted Voting
```rust
// Each vote weighted by token balance
let vote_weight = T::Currency::total_balance(&voter);
proposal.votes_for += vote_weight;
```

#### Quorum Requirements
```rust
// Minimum participation required
let quorum = total_members / 2;
ensure!(proposal.total_votes >= quorum, Error::QuorumNotReached);
```

#### Time-Locked Voting
```rust
// Votes locked for certain period
let unlock_block = current_block + lock_period;
```

## Error Handling

- `ProposalNotFound` - Invalid proposal ID
- `ProposalNotActive` - Proposal not accepting votes
- `AlreadyVoted` - Account already voted
- `VotingPeriodNotEnded` - Voting still in progress
- `VotingPeriodEnded` - Voting period over
- `ProposalNotApproved` - Proposal rejected
- `AlreadyExecuted` - Proposal already executed
- `TitleTooLong` - Title > 256 bytes
- `DescriptionTooLong` - Description > 2048 bytes
- `InvalidVotingPeriod` - Period outside 10-1000 blocks
- `InsufficientDeposit` - Not enough balance for deposit

## Performance

- **Create Proposal**: O(1)
- **Vote**: O(1)
- **Execute**: O(1)
- **Close**: O(1)
- **Query Votes**: O(1) with double map

## Security Features

- **Deposit System**: Prevents spam proposals
- **One Vote Per Account**: Prevents vote manipulation
- **Controller Authorization**: Only proposer can cancel
- **Time Locks**: Voting period enforcement
- **Double Execution Prevention**: Cannot execute twice

## License

Apache-2.0

## Resources

- [Substrate Documentation](https://docs.substrate.io/)
- [Django Integration](../../backend/apps/web3/README.md)
- [TidyGen Documentation](../../../README.md)


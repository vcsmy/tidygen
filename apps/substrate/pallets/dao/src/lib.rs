#![cfg_attr(not(feature = "std"), no_std)]

//! # DAO (Decentralized Autonomous Organization) Pallet
//!
//! A pallet for on-chain governance with proposals and voting.
//!
//! ## Overview
//!
//! The DAO pallet provides functionality for:
//! - Creating governance proposals
//! - Voting on proposals (yes/no voting)
//! - Executing approved proposals
//! - Managing proposal lifecycle
//! - Token-weighted voting (optional)
//!
//! ## Interface
//!
//! ### Dispatchable Functions
//!
//! * `create_proposal` - Create a new governance proposal
//! * `vote` - Cast a vote on a proposal
//! * `execute_proposal` - Execute an approved proposal
//! * `close_proposal` - Close a proposal after voting period

pub use pallet::*;

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::{Currency, Get, ReservableCurrency},
    };
    use frame_system::pallet_prelude::*;
    use sp_runtime::traits::Saturating;
    use sp_std::vec::Vec;

    type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Proposal status
    #[derive(Clone, Encode, Decode, Eq, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum ProposalStatus {
        /// Proposal is active and accepting votes
        Active,
        /// Proposal passed and ready for execution
        Approved,
        /// Proposal was rejected
        Rejected,
        /// Proposal was executed
        Executed,
        /// Proposal was cancelled
        Cancelled,
        /// Proposal voting period expired
        Expired,
    }

    impl Default for ProposalStatus {
        fn default() -> Self {
            Self::Active
        }
    }

    /// Proposal data structure
    #[derive(Clone, Encode, Decode, Eq, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct Proposal<T: Config> {
        /// Unique proposal ID
        pub id: u64,
        /// Proposal creator
        pub proposer: T::AccountId,
        /// Proposal title
        pub title: BoundedVec<u8, T::MaxTitleLength>,
        /// Proposal description
        pub description: BoundedVec<u8, T::MaxDescriptionLength>,
        /// Block number when created
        pub created_at: BlockNumberFor<T>,
        /// Voting start block
        pub voting_start: BlockNumberFor<T>,
        /// Voting end block
        pub voting_end: BlockNumberFor<T>,
        /// Current status
        pub status: ProposalStatus,
        /// Number of votes in favor
        pub votes_for: u64,
        /// Number of votes against
        pub votes_against: u64,
        /// Total number of votes cast
        pub total_votes: u64,
        /// Whether proposal has been executed
        pub executed: bool,
        /// Execution block (if executed)
        pub executed_at: Option<BlockNumberFor<T>>,
    }

    impl<T: Config> Proposal<T> {
        /// Check if proposal is active
        pub fn is_active(&self) -> bool {
            self.status == ProposalStatus::Active
        }

        /// Check if voting period is over
        pub fn is_voting_ended(&self, current_block: BlockNumberFor<T>) -> bool {
            current_block >= self.voting_end
        }

        /// Calculate if proposal is approved
        /// Simple majority: votes_for > votes_against
        pub fn is_approved(&self) -> bool {
            self.votes_for > self.votes_against && self.total_votes > 0
        }

        /// Get approval percentage
        pub fn approval_percentage(&self) -> u32 {
            if self.total_votes == 0 {
                return 0;
            }
            ((self.votes_for as u128 * 100) / self.total_votes as u128) as u32
        }
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        /// Currency type for bonds and deposits
        type Currency: Currency<Self::AccountId> + ReservableCurrency<Self::AccountId>;

        /// Maximum length of proposal title
        #[pallet::constant]
        type MaxTitleLength: Get<u32>;

        /// Maximum length of proposal description
        #[pallet::constant]
        type MaxDescriptionLength: Get<u32>;

        /// Minimum voting period in blocks
        #[pallet::constant]
        type MinVotingPeriod: Get<BlockNumberFor<Self>>;

        /// Maximum voting period in blocks
        #[pallet::constant]
        type MaxVotingPeriod: Get<BlockNumberFor<Self>>;

        /// Proposal deposit amount
        #[pallet::constant]
        type ProposalDeposit: Get<BalanceOf<Self>>;
    }

    /// Storage for proposals mapped by ProposalId
    #[pallet::storage]
    #[pallet::getter(fn proposals)]
    pub type Proposals<T: Config> = StorageMap<_, Blake2_128Concat, u64, Proposal<T>, OptionQuery>;

    /// Storage for votes: double map (ProposalId, AccountId) => bool
    /// bool = true means vote in favor, false means vote against
    #[pallet::storage]
    #[pallet::getter(fn votes)]
    pub type Votes<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u64, // ProposalId
        Blake2_128Concat,
        T::AccountId, // Voter
        bool,         // in_favor
        OptionQuery,
    >;

    /// Proposal counter for unique IDs
    #[pallet::storage]
    #[pallet::getter(fn proposal_count)]
    pub type ProposalCount<T> = StorageValue<_, u64, ValueQuery>;

    /// Track who has voted on which proposals (for UI purposes)
    #[pallet::storage]
    #[pallet::getter(fn has_voted)]
    pub type HasVoted<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u64, // ProposalId
        Blake2_128Concat,
        T::AccountId, // Voter
        bool,         // has voted
        ValueQuery,
    >;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Proposal created [proposal_id, proposer, title]
        ProposalCreated {
            proposal_id: u64,
            proposer: T::AccountId,
            title: Vec<u8>,
        },
        /// Vote cast [proposal_id, voter, in_favor]
        VoteCast {
            proposal_id: u64,
            voter: T::AccountId,
            in_favor: bool,
        },
        /// Proposal executed [proposal_id, executor]
        ProposalExecuted {
            proposal_id: u64,
            executor: T::AccountId,
        },
        /// Proposal status changed [proposal_id, old_status, new_status]
        ProposalStatusChanged {
            proposal_id: u64,
            old_status: ProposalStatus,
            new_status: ProposalStatus,
        },
        /// Proposal closed [proposal_id, final_status]
        ProposalClosed {
            proposal_id: u64,
            final_status: ProposalStatus,
        },
        /// Voting period ended [proposal_id, approved]
        VotingEnded {
            proposal_id: u64,
            approved: bool,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        /// Proposal not found
        ProposalNotFound,
        /// Proposal is not active
        ProposalNotActive,
        /// Already voted on this proposal
        AlreadyVoted,
        /// Voting period has not ended
        VotingPeriodNotEnded,
        /// Voting period has ended
        VotingPeriodEnded,
        /// Proposal not approved
        ProposalNotApproved,
        /// Proposal already executed
        AlreadyExecuted,
        /// Title too long
        TitleTooLong,
        /// Description too long
        DescriptionTooLong,
        /// Invalid voting period
        InvalidVotingPeriod,
        /// Insufficient funds for proposal deposit
        InsufficientDeposit,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new governance proposal
        ///
        /// # Arguments
        /// * `origin` - Transaction origin (proposer)
        /// * `title` - Proposal title
        /// * `description` - Proposal description
        /// * `voting_period` - Voting period in blocks (optional, uses minimum if None)
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `ProposalCreated` - Emitted when proposal is created
        ///
        /// # Errors
        /// * `TitleTooLong` - Title exceeds maximum length
        /// * `DescriptionTooLong` - Description exceeds maximum length
        /// * `InvalidVotingPeriod` - Voting period outside allowed range
        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn create_proposal(
            origin: OriginFor<T>,
            title: Vec<u8>,
            description: Vec<u8>,
            voting_period: Option<BlockNumberFor<T>>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Validate inputs
            let bounded_title: BoundedVec<u8, T::MaxTitleLength> = title
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::TitleTooLong)?;

            let bounded_description: BoundedVec<u8, T::MaxDescriptionLength> = description
                .try_into()
                .map_err(|_| Error::<T>::DescriptionTooLong)?;

            // Determine voting period
            let period = voting_period.unwrap_or_else(|| T::MinVotingPeriod::get());
            ensure!(
                period >= T::MinVotingPeriod::get() && period <= T::MaxVotingPeriod::get(),
                Error::<T>::InvalidVotingPeriod
            );

            // Reserve deposit
            T::Currency::reserve(&who, T::ProposalDeposit::get())
                .map_err(|_| Error::<T>::InsufficientDeposit)?;

            // Get proposal ID
            let proposal_id = ProposalCount::<T>::get();
            let current_block = frame_system::Pallet::<T>::block_number();
            let voting_end = current_block.saturating_add(period);

            // Create proposal
            let proposal = Proposal {
                id: proposal_id,
                proposer: who.clone(),
                title: bounded_title.clone(),
                description: bounded_description,
                created_at: current_block,
                voting_start: current_block,
                voting_end,
                status: ProposalStatus::Active,
                votes_for: 0,
                votes_against: 0,
                total_votes: 0,
                executed: false,
                executed_at: None,
            };

            // Store proposal
            Proposals::<T>::insert(proposal_id, proposal);
            ProposalCount::<T>::put(proposal_id.saturating_add(1));

            // Emit event
            Self::deposit_event(Event::ProposalCreated {
                proposal_id,
                proposer: who,
                title: bounded_title.to_vec(),
            });

            Ok(())
        }

        /// Vote on a proposal
        ///
        /// # Arguments
        /// * `origin` - Transaction origin (voter)
        /// * `proposal_id` - ID of the proposal to vote on
        /// * `in_favor` - true for yes, false for no
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `VoteCast` - Emitted when vote is successfully cast
        ///
        /// # Errors
        /// * `ProposalNotFound` - Proposal doesn't exist
        /// * `ProposalNotActive` - Proposal is not active
        /// * `AlreadyVoted` - Account has already voted
        /// * `VotingPeriodEnded` - Voting period has ended
        #[pallet::call_index(1)]
        #[pallet::weight(8_000)]
        pub fn vote(
            origin: OriginFor<T>,
            proposal_id: u64,
            in_favor: bool,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Get proposal
            let mut proposal =
                Proposals::<T>::get(proposal_id).ok_or(Error::<T>::ProposalNotFound)?;

            // Check proposal is active
            ensure!(proposal.is_active(), Error::<T>::ProposalNotActive);

            // Check voting period hasn't ended
            let current_block = frame_system::Pallet::<T>::block_number();
            ensure!(
                !proposal.is_voting_ended(current_block),
                Error::<T>::VotingPeriodEnded
            );

            // Check if already voted
            ensure!(
                !HasVoted::<T>::get(proposal_id, &who),
                Error::<T>::AlreadyVoted
            );

            // Record vote
            Votes::<T>::insert(proposal_id, &who, in_favor);
            HasVoted::<T>::insert(proposal_id, &who, true);

            // Update vote counts
            if in_favor {
                proposal.votes_for = proposal.votes_for.saturating_add(1);
            } else {
                proposal.votes_against = proposal.votes_against.saturating_add(1);
            }
            proposal.total_votes = proposal.total_votes.saturating_add(1);

            // Store updated proposal
            Proposals::<T>::insert(proposal_id, proposal);

            // Emit event
            Self::deposit_event(Event::VoteCast {
                proposal_id,
                voter: who,
                in_favor,
            });

            Ok(())
        }

        /// Execute an approved proposal
        ///
        /// # Arguments
        /// * `origin` - Transaction origin (executor)
        /// * `proposal_id` - ID of the proposal to execute
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `ProposalExecuted` - Emitted when proposal is executed
        /// * `ProposalStatusChanged` - Emitted when status changes
        ///
        /// # Errors
        /// * `ProposalNotFound` - Proposal doesn't exist
        /// * `VotingPeriodNotEnded` - Voting still in progress
        /// * `ProposalNotApproved` - Proposal was not approved
        /// * `AlreadyExecuted` - Proposal already executed
        #[pallet::call_index(2)]
        #[pallet::weight(15_000)]
        pub fn execute_proposal(origin: OriginFor<T>, proposal_id: u64) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Get proposal
            let mut proposal =
                Proposals::<T>::get(proposal_id).ok_or(Error::<T>::ProposalNotFound)?;

            // Check voting period ended
            let current_block = frame_system::Pallet::<T>::block_number();
            ensure!(
                proposal.is_voting_ended(current_block),
                Error::<T>::VotingPeriodNotEnded
            );

            // Check proposal is approved
            ensure!(proposal.is_approved(), Error::<T>::ProposalNotApproved);

            // Check not already executed
            ensure!(!proposal.executed, Error::<T>::AlreadyExecuted);

            // Update proposal status
            let old_status = proposal.status.clone();
            proposal.status = ProposalStatus::Executed;
            proposal.executed = true;
            proposal.executed_at = Some(current_block);

            // Store updated proposal
            Proposals::<T>::insert(proposal_id, proposal);

            // Unreserve deposit (return to proposer)
            T::Currency::unreserve(&who, T::ProposalDeposit::get());

            // Emit events
            Self::deposit_event(Event::ProposalExecuted {
                proposal_id,
                executor: who,
            });

            Self::deposit_event(Event::ProposalStatusChanged {
                proposal_id,
                old_status,
                new_status: ProposalStatus::Executed,
            });

            Ok(())
        }

        /// Close a proposal after voting period
        ///
        /// This function finalizes the proposal status based on voting results.
        /// Can be called by anyone after voting period ends.
        ///
        /// # Arguments
        /// * `origin` - Transaction origin
        /// * `proposal_id` - ID of the proposal to close
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `VotingEnded` - Emitted when voting ends
        /// * `ProposalClosed` - Emitted when proposal is closed
        /// * `ProposalStatusChanged` - Emitted when status changes
        #[pallet::call_index(3)]
        #[pallet::weight(5_000)]
        pub fn close_proposal(origin: OriginFor<T>, proposal_id: u64) -> DispatchResult {
            let _who = ensure_signed(origin)?;

            // Get proposal
            let mut proposal =
                Proposals::<T>::get(proposal_id).ok_or(Error::<T>::ProposalNotFound)?;

            // Check voting period ended
            let current_block = frame_system::Pallet::<T>::block_number();
            ensure!(
                proposal.is_voting_ended(current_block),
                Error::<T>::VotingPeriodNotEnded
            );

            // Check not already executed or closed
            ensure!(proposal.is_active(), Error::<T>::ProposalNotActive);

            // Determine final status
            let old_status = proposal.status.clone();
            let is_approved = proposal.is_approved();
            let new_status = if is_approved {
                ProposalStatus::Approved
            } else {
                ProposalStatus::Rejected
            };

            proposal.status = new_status.clone();

            // Store updated proposal
            Proposals::<T>::insert(proposal_id, proposal);

            // Emit events
            Self::deposit_event(Event::VotingEnded {
                proposal_id,
                approved: is_approved,
            });

            Self::deposit_event(Event::ProposalClosed {
                proposal_id,
                final_status: new_status.clone(),
            });

            Self::deposit_event(Event::ProposalStatusChanged {
                proposal_id,
                old_status,
                new_status,
            });

            Ok(())
        }

        /// Cancel a proposal (only proposer can cancel before voting ends)
        ///
        /// # Arguments
        /// * `origin` - Transaction origin (must be proposer)
        /// * `proposal_id` - ID of the proposal to cancel
        #[pallet::call_index(4)]
        #[pallet::weight(5_000)]
        pub fn cancel_proposal(origin: OriginFor<T>, proposal_id: u64) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Get proposal
            let mut proposal =
                Proposals::<T>::get(proposal_id).ok_or(Error::<T>::ProposalNotFound)?;

            // Only proposer can cancel
            ensure!(proposal.proposer == who, Error::<T>::ProposalNotActive);

            // Can only cancel active proposals
            ensure!(proposal.is_active(), Error::<T>::ProposalNotActive);

            // Update status
            let old_status = proposal.status.clone();
            proposal.status = ProposalStatus::Cancelled;

            // Store updated proposal
            Proposals::<T>::insert(proposal_id, proposal);

            // Unreserve deposit
            T::Currency::unreserve(&who, T::ProposalDeposit::get());

            // Emit event
            Self::deposit_event(Event::ProposalStatusChanged {
                proposal_id,
                old_status,
                new_status: ProposalStatus::Cancelled,
            });

            Ok(())
        }
    }

    // Helper functions
    impl<T: Config> Pallet<T> {
        /// Get vote for an account on a proposal
        pub fn get_vote(proposal_id: u64, voter: &T::AccountId) -> Option<bool> {
            Votes::<T>::get(proposal_id, voter)
        }

        /// Check if account has voted
        pub fn has_account_voted(proposal_id: u64, voter: &T::AccountId) -> bool {
            HasVoted::<T>::get(proposal_id, voter)
        }

        /// Get proposal with vote counts
        pub fn get_proposal_details(proposal_id: u64) -> Option<Proposal<T>> {
            Proposals::<T>::get(proposal_id)
        }
    }
}


#![cfg_attr(not(feature = "std"), no_std)]

//! # TidyGen Ledger Pallet
//!
//! A pallet for managing ERP invoice and transaction ledger entries on-chain.
//!
//! ## Overview
//!
//! The TidyGen Ledger pallet provides functionality for:
//! - Creating tamper-proof ledger entries for invoices and transactions
//! - Updating ledger entry status
//! - Anchoring transaction hashes on-chain for verification
//! - Querying ledger history
//!
//! ## Interface
//!
//! ### Dispatchable Functions
//!
//! * `create_ledger_entry` - Create a new ledger entry with transaction data
//! * `update_ledger_status` - Update the status of an existing ledger entry
//! * `anchor_transaction` - Anchor a transaction hash on-chain

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::{Currency, ExistenceRequirement, Get},
    };
    use frame_system::pallet_prelude::*;
    use sp_std::vec::Vec;

    type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Ledger entry status
    #[derive(Clone, Encode, Decode, Eq, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum LedgerStatus {
        Pending,
        Confirmed,
        Failed,
        Cancelled,
    }

    impl Default for LedgerStatus {
        fn default() -> Self {
            Self::Pending
        }
    }

    /// Ledger entry data structure
    #[derive(Clone, Encode, Decode, Eq, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct LedgerEntry<T: Config> {
        /// Entry creator
        pub creator: T::AccountId,
        /// Transaction type (e.g., "invoice", "payment", "expense")
        pub transaction_type: BoundedVec<u8, T::MaxTransactionTypeLength>,
        /// Transaction data hash (SHA-256)
        pub data_hash: [u8; 32],
        /// Amount (if applicable)
        pub amount: Option<BalanceOf<T>>,
        /// Status
        pub status: LedgerStatus,
        /// Block number when created
        pub created_at: BlockNumberFor<T>,
        /// Block number when last updated
        pub updated_at: BlockNumberFor<T>,
    }

    /// Transaction anchor data structure
    #[derive(Clone, Encode, Decode, Eq, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct TransactionAnchor<T: Config> {
        /// Account that anchored the transaction
        pub anchored_by: T::AccountId,
        /// Transaction hash
        pub tx_hash: [u8; 32],
        /// Block number when anchored
        pub block_number: BlockNumberFor<T>,
        /// Additional metadata
        pub metadata: BoundedVec<u8, T::MaxMetadataLength>,
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        /// Currency type for handling balances
        type Currency: Currency<Self::AccountId>;

        /// Maximum length of transaction type string
        #[pallet::constant]
        type MaxTransactionTypeLength: Get<u32>;

        /// Maximum length of metadata
        #[pallet::constant]
        type MaxMetadataLength: Get<u32>;
    }

    /// Storage for ledger entries
    #[pallet::storage]
    #[pallet::getter(fn ledger_entries)]
    pub type LedgerEntries<T: Config> =
        StorageMap<_, Blake2_128Concat, u64, LedgerEntry<T>, OptionQuery>;

    /// Storage for transaction anchors
    #[pallet::storage]
    #[pallet::getter(fn transaction_anchors)]
    pub type TransactionAnchors<T: Config> =
        StorageMap<_, Blake2_128Concat, [u8; 32], TransactionAnchor<T>, OptionQuery>;

    /// Counter for ledger entries
    #[pallet::storage]
    #[pallet::getter(fn entry_count)]
    pub type EntryCount<T> = StorageValue<_, u64, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Ledger entry created [entry_id, creator, data_hash]
        LedgerEntryCreated {
            entry_id: u64,
            creator: T::AccountId,
            data_hash: [u8; 32],
        },
        /// Ledger entry status updated [entry_id, old_status, new_status]
        LedgerStatusUpdated {
            entry_id: u64,
            old_status: LedgerStatus,
            new_status: LedgerStatus,
        },
        /// Transaction anchored [tx_hash, anchored_by, block_number]
        TransactionAnchored {
            tx_hash: [u8; 32],
            anchored_by: T::AccountId,
            block_number: BlockNumberFor<T>,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        /// Ledger entry not found
        EntryNotFound,
        /// Transaction already anchored
        TransactionAlreadyAnchored,
        /// Invalid status transition
        InvalidStatusTransition,
        /// Unauthorized operation
        Unauthorized,
        /// Transaction type too long
        TransactionTypeTooLong,
        /// Metadata too long
        MetadataTooLong,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new ledger entry
        ///
        /// # Arguments
        /// * `origin` - Transaction origin
        /// * `transaction_type` - Type of transaction (e.g., "invoice", "payment")
        /// * `data_hash` - SHA-256 hash of the transaction data
        /// * `amount` - Optional amount associated with the transaction
        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn create_ledger_entry(
            origin: OriginFor<T>,
            transaction_type: Vec<u8>,
            data_hash: [u8; 32],
            amount: Option<BalanceOf<T>>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let bounded_type: BoundedVec<u8, T::MaxTransactionTypeLength> = transaction_type
                .try_into()
                .map_err(|_| Error::<T>::TransactionTypeTooLong)?;

            let entry_id = EntryCount::<T>::get();
            let current_block = frame_system::Pallet::<T>::block_number();

            let entry = LedgerEntry {
                creator: who.clone(),
                transaction_type: bounded_type,
                data_hash,
                amount,
                status: LedgerStatus::Pending,
                created_at: current_block,
                updated_at: current_block,
            };

            LedgerEntries::<T>::insert(entry_id, entry);
            EntryCount::<T>::put(entry_id.saturating_add(1));

            Self::deposit_event(Event::LedgerEntryCreated {
                entry_id,
                creator: who,
                data_hash,
            });

            Ok(())
        }

        /// Update ledger entry status
        ///
        /// # Arguments
        /// * `origin` - Transaction origin
        /// * `entry_id` - ID of the ledger entry to update
        /// * `new_status` - New status to set
        #[pallet::call_index(1)]
        #[pallet::weight(10_000)]
        pub fn update_ledger_status(
            origin: OriginFor<T>,
            entry_id: u64,
            new_status: LedgerStatus,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            LedgerEntries::<T>::try_mutate(entry_id, |entry_opt| {
                let entry = entry_opt.as_mut().ok_or(Error::<T>::EntryNotFound)?;

                // Only creator can update status
                ensure!(entry.creator == who, Error::<T>::Unauthorized);

                let old_status = entry.status.clone();
                entry.status = new_status.clone();
                entry.updated_at = frame_system::Pallet::<T>::block_number();

                Self::deposit_event(Event::LedgerStatusUpdated {
                    entry_id,
                    old_status,
                    new_status,
                });

                Ok(())
            })
        }

        /// Anchor a transaction hash on-chain
        ///
        /// # Arguments
        /// * `origin` - Transaction origin
        /// * `tx_hash` - Transaction hash to anchor
        /// * `metadata` - Optional metadata about the transaction
        #[pallet::call_index(2)]
        #[pallet::weight(10_000)]
        pub fn anchor_transaction(
            origin: OriginFor<T>,
            tx_hash: [u8; 32],
            metadata: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Ensure transaction not already anchored
            ensure!(
                !TransactionAnchors::<T>::contains_key(tx_hash),
                Error::<T>::TransactionAlreadyAnchored
            );

            let bounded_metadata: BoundedVec<u8, T::MaxMetadataLength> = metadata
                .try_into()
                .map_err(|_| Error::<T>::MetadataTooLong)?;

            let current_block = frame_system::Pallet::<T>::block_number();

            let anchor = TransactionAnchor {
                anchored_by: who.clone(),
                tx_hash,
                block_number: current_block,
                metadata: bounded_metadata,
            };

            TransactionAnchors::<T>::insert(tx_hash, anchor);

            Self::deposit_event(Event::TransactionAnchored {
                tx_hash,
                anchored_by: who,
                block_number: current_block,
            });

            Ok(())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use frame_support::{assert_noop, assert_ok};
    use sp_core::H256;
    use sp_runtime::{
        traits::{BlakeTwo256, IdentityLookup},
        BuildStorage,
    };

    type Block = frame_system::mocking::MockBlock<Test>;

    frame_support::construct_runtime!(
        pub enum Test {
            System: frame_system,
            TidygenLedger: pallet,
        }
    );

    impl frame_system::Config for Test {
        type BaseCallFilter = frame_support::traits::Everything;
        type BlockWeights = ();
        type BlockLength = ();
        type DbWeight = ();
        type RuntimeOrigin = RuntimeOrigin;
        type RuntimeCall = RuntimeCall;
        type Nonce = u64;
        type Hash = H256;
        type Hashing = BlakeTwo256;
        type AccountId = u64;
        type Lookup = IdentityLookup<Self::AccountId>;
        type Block = Block;
        type RuntimeEvent = RuntimeEvent;
        type BlockHashCount = frame_support::traits::ConstU64<250>;
        type Version = ();
        type PalletInfo = PalletInfo;
        type AccountData = ();
        type OnNewAccount = ();
        type OnKilledAccount = ();
        type SystemWeightInfo = ();
        type SS58Prefix = frame_support::traits::ConstU16<42>;
        type OnSetCode = ();
        type MaxConsumers = frame_support::traits::ConstU32<16>;
    }

    impl pallet::Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type Currency = ();
        type MaxTransactionTypeLength = frame_support::traits::ConstU32<32>;
        type MaxMetadataLength = frame_support::traits::ConstU32<256>;
    }

    fn new_test_ext() -> sp_io::TestExternalities {
        frame_system::GenesisConfig::<Test>::default()
            .build_storage()
            .unwrap()
            .into()
    }

    #[test]
    fn create_ledger_entry_works() {
        new_test_ext().execute_with(|| {
            let creator = 1u64;
            let tx_type = b"invoice".to_vec();
            let data_hash = [1u8; 32];

            assert_ok!(TidygenLedger::create_ledger_entry(
                RuntimeOrigin::signed(creator),
                tx_type,
                data_hash,
                None
            ));

            assert_eq!(TidygenLedger::entry_count(), 1);
        });
    }
}


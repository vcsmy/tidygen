#![cfg_attr(not(feature = "std"), no_std)]

//! # Decentralized Identity (DID) Pallet
//!
//! A W3C DID-compliant pallet for decentralized identity management.
//!
//! ## Overview
//!
//! The DID pallet provides functionality for:
//! - Registering decentralized identities (DIDs) for accounts
//! - Storing DID documents with public keys and metadata
//! - Resolving DID documents for verification
//! - Updating and revoking DIDs
//! - Integration with Django user authentication
//!
//! ## DID Specification
//!
//! This pallet follows W3C DID Core specification principles:
//! - Each AccountId can have one DID document
//! - DID documents contain verification methods (public keys)
//! - Metadata supports service endpoints and additional properties
//! - DIDs can be updated or revoked by the controller
//!
//! ## Interface
//!
//! ### Dispatchable Functions
//!
//! * `register_did` - Register a new DID for an account
//! * `update_did` - Update an existing DID document
//! * `revoke_did` - Revoke a DID
//! * `resolve_did` - Resolve a DID document (emits event)
//!
//! ### RPC Methods
//!
//! * `get_did` - Query DID document for an account

pub use pallet::*;

#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::Get,
    };
    use frame_system::pallet_prelude::*;
    use sp_core::H256;
    use sp_io::hashing::blake2_256;
    use sp_std::vec::Vec;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// DID Document status
    #[derive(Clone, Encode, Decode, Eq, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    pub enum DidStatus {
        /// DID is active and valid
        Active,
        /// DID has been revoked
        Revoked,
        /// DID is temporarily suspended
        Suspended,
    }

    impl Default for DidStatus {
        fn default() -> Self {
            Self::Active
        }
    }

    /// DID Document structure
    /// Follows W3C DID Core specification principles
    #[derive(Clone, Encode, Decode, Eq, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct DidDocument<T: Config> {
        /// Controller of this DID (typically the account owner)
        pub controller: T::AccountId,
        /// Public key for verification (can be used for authentication)
        pub public_key: BoundedVec<u8, T::MaxPublicKeyLength>,
        /// Metadata (JSON string or additional properties)
        /// Can include: service endpoints, authentication methods, etc.
        pub metadata: BoundedVec<u8, T::MaxMetadataLength>,
        /// Block number when DID was created
        pub created_at: BlockNumberFor<T>,
        /// Block number when DID was last updated
        pub updated_at: BlockNumberFor<T>,
        /// Status of the DID
        pub status: DidStatus,
        /// DID identifier (derived from account)
        pub did_identifier: BoundedVec<u8, T::MaxDidLength>,
        /// Nonce for updates (prevents replay attacks)
        pub nonce: u64,
    }

    impl<T: Config> DidDocument<T> {
        /// Generate DID identifier from account
        /// Format: did:substrate:{network}:{account_hash}
        pub fn generate_did_identifier(account: &T::AccountId) -> BoundedVec<u8, T::MaxDidLength> {
            let account_bytes = account.encode();
            let hash = blake2_256(&account_bytes);
            let hex_hash = Self::to_hex(&hash[..8]); // Use first 8 bytes
            
            let did_str = format!("did:substrate:tidygen:{}", hex_hash);
            did_str.as_bytes().to_vec()
                .try_into()
                .unwrap_or_default()
        }

        /// Convert bytes to hex string
        fn to_hex(bytes: &[u8]) -> String {
            const HEX_CHARS: &[u8] = b"0123456789abcdef";
            let mut hex = String::with_capacity(bytes.len() * 2);
            for &byte in bytes {
                hex.push(HEX_CHARS[(byte >> 4) as usize] as char);
                hex.push(HEX_CHARS[(byte & 0xf) as usize] as char);
            }
            hex
        }

        /// Verify if DID is active
        pub fn is_active(&self) -> bool {
            self.status == DidStatus::Active
        }
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        /// Maximum length of public key
        #[pallet::constant]
        type MaxPublicKeyLength: Get<u32>;

        /// Maximum length of metadata
        #[pallet::constant]
        type MaxMetadataLength: Get<u32>;

        /// Maximum length of DID identifier
        #[pallet::constant]
        type MaxDidLength: Get<u32>;
    }

    /// Storage for DID documents mapped by AccountId
    /// Each account can have one DID document
    #[pallet::storage]
    #[pallet::getter(fn did_documents)]
    pub type DidDocuments<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        DidDocument<T>,
        OptionQuery,
    >;

    /// Reverse mapping: DID identifier to AccountId
    /// Allows DID resolution by identifier string
    #[pallet::storage]
    #[pallet::getter(fn did_to_account)]
    pub type DidToAccount<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        BoundedVec<u8, T::MaxDidLength>,
        T::AccountId,
        OptionQuery,
    >;

    /// Total number of DIDs registered
    #[pallet::storage]
    #[pallet::getter(fn did_count)]
    pub type DidCount<T> = StorageValue<_, u64, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// DID registered [account_id, did_identifier]
        DidRegistered {
            account: T::AccountId,
            did_identifier: Vec<u8>,
        },
        /// DID updated [account_id, nonce]
        DidUpdated {
            account: T::AccountId,
            nonce: u64,
        },
        /// DID revoked [account_id]
        DidRevoked {
            account: T::AccountId,
        },
        /// DID resolved [account_id, status]
        DidResolved {
            account: T::AccountId,
            status: DidStatus,
        },
        /// DID status changed [account_id, old_status, new_status]
        DidStatusChanged {
            account: T::AccountId,
            old_status: DidStatus,
            new_status: DidStatus,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        /// DID already exists for this account
        DidAlreadyExists,
        /// DID does not exist
        DidNotFound,
        /// Public key too long
        PublicKeyTooLong,
        /// Metadata too long
        MetadataTooLong,
        /// Only the controller can perform this action
        NotController,
        /// DID is revoked and cannot be used
        DidRevoked,
        /// DID is suspended
        DidSuspended,
        /// Invalid DID identifier
        InvalidDidIdentifier,
        /// DID identifier too long
        DidIdentifierTooLong,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register a new DID for an account
        ///
        /// # Arguments
        /// * `origin` - Transaction origin (becomes the DID controller)
        /// * `account_id` - Account to register DID for (can be self or another account)
        /// * `public_key` - Public key for verification
        /// * `metadata` - Additional metadata (JSON string, service endpoints, etc.)
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `DidRegistered` - Emitted when DID is successfully registered
        ///
        /// # Errors
        /// * `DidAlreadyExists` - Account already has a DID
        /// * `PublicKeyTooLong` - Public key exceeds maximum length
        /// * `MetadataTooLong` - Metadata exceeds maximum length
        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn register_did(
            origin: OriginFor<T>,
            account_id: T::AccountId,
            public_key: Vec<u8>,
            metadata: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Ensure DID doesn't already exist
            ensure!(
                !DidDocuments::<T>::contains_key(&account_id),
                Error::<T>::DidAlreadyExists
            );

            // Validate lengths
            let bounded_public_key: BoundedVec<u8, T::MaxPublicKeyLength> = public_key
                .try_into()
                .map_err(|_| Error::<T>::PublicKeyTooLong)?;

            let bounded_metadata: BoundedVec<u8, T::MaxMetadataLength> = metadata
                .try_into()
                .map_err(|_| Error::<T>::MetadataTooLong)?;

            // Generate DID identifier
            let did_identifier = DidDocument::<T>::generate_did_identifier(&account_id);

            let current_block = frame_system::Pallet::<T>::block_number();

            // Create DID document
            let did_doc = DidDocument {
                controller: who.clone(),
                public_key: bounded_public_key,
                metadata: bounded_metadata,
                created_at: current_block,
                updated_at: current_block,
                status: DidStatus::Active,
                did_identifier: did_identifier.clone(),
                nonce: 0,
            };

            // Store DID document
            DidDocuments::<T>::insert(&account_id, did_doc);

            // Store reverse mapping
            DidToAccount::<T>::insert(did_identifier.clone(), &account_id);

            // Increment count
            let count = DidCount::<T>::get();
            DidCount::<T>::put(count.saturating_add(1));

            // Emit event
            Self::deposit_event(Event::DidRegistered {
                account: account_id,
                did_identifier: did_identifier.to_vec(),
            });

            Ok(())
        }

        /// Update an existing DID document
        ///
        /// # Arguments
        /// * `origin` - Transaction origin (must be the controller)
        /// * `account_id` - Account whose DID to update
        /// * `public_key` - New public key (optional, pass None to keep existing)
        /// * `metadata` - New metadata (optional, pass None to keep existing)
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `DidUpdated` - Emitted when DID is successfully updated
        ///
        /// # Errors
        /// * `DidNotFound` - DID does not exist
        /// * `NotController` - Origin is not the DID controller
        /// * `DidRevoked` - DID is revoked and cannot be updated
        #[pallet::call_index(1)]
        #[pallet::weight(10_000)]
        pub fn update_did(
            origin: OriginFor<T>,
            account_id: T::AccountId,
            public_key: Option<Vec<u8>>,
            metadata: Option<Vec<u8>>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Get existing DID document
            DidDocuments::<T>::try_mutate(&account_id, |did_opt| {
                let did = did_opt.as_mut().ok_or(Error::<T>::DidNotFound)?;

                // Verify controller
                ensure!(did.controller == who, Error::<T>::NotController);

                // Verify not revoked
                ensure!(did.status != DidStatus::Revoked, Error::<T>::DidRevoked);

                // Update public key if provided
                if let Some(pk) = public_key {
                    let bounded_pk: BoundedVec<u8, T::MaxPublicKeyLength> = pk
                        .try_into()
                        .map_err(|_| Error::<T>::PublicKeyTooLong)?;
                    did.public_key = bounded_pk;
                }

                // Update metadata if provided
                if let Some(md) = metadata {
                    let bounded_md: BoundedVec<u8, T::MaxMetadataLength> = md
                        .try_into()
                        .map_err(|_| Error::<T>::MetadataTooLong)?;
                    did.metadata = bounded_md;
                }

                // Update timestamp and nonce
                did.updated_at = frame_system::Pallet::<T>::block_number();
                did.nonce = did.nonce.saturating_add(1);

                // Emit event
                Self::deposit_event(Event::DidUpdated {
                    account: account_id.clone(),
                    nonce: did.nonce,
                });

                Ok(())
            })
        }

        /// Revoke a DID
        ///
        /// # Arguments
        /// * `origin` - Transaction origin (must be the controller)
        /// * `account_id` - Account whose DID to revoke
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `DidRevoked` - Emitted when DID is successfully revoked
        /// * `DidStatusChanged` - Emitted with status change details
        ///
        /// # Errors
        /// * `DidNotFound` - DID does not exist
        /// * `NotController` - Origin is not the DID controller
        #[pallet::call_index(2)]
        #[pallet::weight(5_000)]
        pub fn revoke_did(origin: OriginFor<T>, account_id: T::AccountId) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Get and update DID document
            DidDocuments::<T>::try_mutate(&account_id, |did_opt| {
                let did = did_opt.as_mut().ok_or(Error::<T>::DidNotFound)?;

                // Verify controller
                ensure!(did.controller == who, Error::<T>::NotController);

                let old_status = did.status.clone();
                did.status = DidStatus::Revoked;
                did.updated_at = frame_system::Pallet::<T>::block_number();

                // Emit events
                Self::deposit_event(Event::DidRevoked {
                    account: account_id.clone(),
                });

                Self::deposit_event(Event::DidStatusChanged {
                    account: account_id.clone(),
                    old_status,
                    new_status: DidStatus::Revoked,
                });

                Ok(())
            })
        }

        /// Resolve a DID document (query operation that emits event)
        ///
        /// In production, use RPC endpoint instead of this extrinsic
        ///
        /// # Arguments
        /// * `origin` - Transaction origin
        /// * `account_id` - Account whose DID to resolve
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `DidResolved` - Emitted with DID status
        ///
        /// # Errors
        /// * `DidNotFound` - DID does not exist
        #[pallet::call_index(3)]
        #[pallet::weight(3_000)]
        pub fn resolve_did(origin: OriginFor<T>, account_id: T::AccountId) -> DispatchResult {
            let _who = ensure_signed(origin)?;

            // Get DID document
            let did = DidDocuments::<T>::get(&account_id).ok_or(Error::<T>::DidNotFound)?;

            // Emit event
            Self::deposit_event(Event::DidResolved {
                account: account_id,
                status: did.status,
            });

            Ok(())
        }
    }

    // Helper functions for RPC
    impl<T: Config> Pallet<T> {
        /// Get DID document for an account (for RPC)
        pub fn get_did(account: &T::AccountId) -> Option<DidDocument<T>> {
            DidDocuments::<T>::get(account)
        }

        /// Get account from DID identifier (for RPC)
        pub fn get_account_from_did(did_identifier: &[u8]) -> Option<T::AccountId> {
            let bounded: BoundedVec<u8, T::MaxDidLength> = did_identifier
                .to_vec()
                .try_into()
                .ok()?;
            DidToAccount::<T>::get(bounded)
        }

        /// Verify if a DID is active
        pub fn is_did_active(account: &T::AccountId) -> bool {
            if let Some(did) = DidDocuments::<T>::get(account) {
                did.is_active()
            } else {
                false
            }
        }

        /// Get total DID count
        pub fn total_dids() -> u64 {
            DidCount::<T>::get()
        }
    }
}


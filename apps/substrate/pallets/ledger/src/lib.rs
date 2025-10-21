#![cfg_attr(not(feature = "std"), no_std)]

//! # ERP Ledger Pallet
//!
//! A pallet for managing ERP invoices with SHA256 hashing for Django integration.
//!
//! ## Overview
//!
//! The ERP Ledger pallet provides functionality for:
//! - Creating invoices with SHA256 hashing for Django record linking
//! - Storing invoices per client (AccountId)
//! - Retrieving invoice history for clients
//! - Emitting events for invoice operations
//!
//! ## Interface
//!
//! ### Dispatchable Functions
//!
//! * `create_invoice` - Create a new invoice with automatic SHA256 hashing
//! * `get_invoices` - Retrieve all invoices for a specific client
//!
//! ### Events
//!
//! * `InvoiceCreated` - Emitted when a new invoice is created
//! * `InvoiceRetrieved` - Emitted when invoices are retrieved

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use frame_support::{
        pallet_prelude::*,
        traits::{Currency, Get},
    };
    use frame_system::pallet_prelude::*;
    use sp_core::H256;
    use sp_io::hashing::sha2_256;
    use sp_runtime::traits::Hash;
    use sp_std::vec::Vec;

    type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// Invoice data structure
    /// This structure is designed to match Django ERP invoice model
    #[derive(Clone, Encode, Decode, Eq, PartialEq, RuntimeDebug, TypeInfo, MaxEncodedLen)]
    #[scale_info(skip_type_params(T))]
    pub struct Invoice<T: Config> {
        /// Unique invoice ID
        pub id: u64,
        /// Client account ID
        pub client: T::AccountId,
        /// Invoice amount
        pub amount: BalanceOf<T>,
        /// Invoice metadata (JSON string, invoice number, etc.)
        pub metadata: BoundedVec<u8, T::MaxMetadataLength>,
        /// Block number when invoice was created (timestamp)
        pub timestamp: BlockNumberFor<T>,
        /// SHA256 hash of invoice details (for Django linking)
        pub invoice_hash: [u8; 32],
        /// Creator of the invoice
        pub created_by: T::AccountId,
    }

    impl<T: Config> Invoice<T> {
        /// Calculate SHA256 hash of invoice details
        /// This hash is used to link the on-chain invoice with Django database record
        pub fn calculate_hash(&self) -> [u8; 32] {
            let mut data = Vec::new();
            
            // Encode invoice data for hashing
            data.extend_from_slice(&self.id.to_le_bytes());
            data.extend_from_slice(self.client.encode().as_slice());
            data.extend_from_slice(self.amount.encode().as_slice());
            data.extend_from_slice(self.metadata.encode().as_slice());
            data.extend_from_slice(&self.timestamp.encode());
            
            // Calculate SHA256 hash
            sha2_256(&data)
        }
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// The overarching event type.
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        /// Currency type for handling invoice amounts
        type Currency: Currency<Self::AccountId>;

        /// Maximum length of invoice metadata
        #[pallet::constant]
        type MaxMetadataLength: Get<u32>;

        /// Maximum number of invoices per client
        #[pallet::constant]
        type MaxInvoicesPerClient: Get<u32>;
    }

    /// Storage for invoices mapped by client AccountId
    /// Each client has a vector of their invoices
    #[pallet::storage]
    #[pallet::getter(fn invoices)]
    pub type Invoices<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<Invoice<T>, T::MaxInvoicesPerClient>,
        ValueQuery,
    >;

    /// Global invoice counter for unique IDs
    #[pallet::storage]
    #[pallet::getter(fn invoice_count)]
    pub type InvoiceCount<T> = StorageValue<_, u64, ValueQuery>;

    /// Storage for invoice hash to ID mapping (for quick lookups)
    #[pallet::storage]
    #[pallet::getter(fn invoice_by_hash)]
    pub type InvoiceByHash<T: Config> = StorageMap<_, Blake2_128Concat, [u8; 32], u64, OptionQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// Invoice created [invoice_id, client, amount, invoice_hash]
        InvoiceCreated {
            invoice_id: u64,
            client: T::AccountId,
            amount: BalanceOf<T>,
            invoice_hash: [u8; 32],
            created_by: T::AccountId,
        },
        /// Invoices retrieved [client, count]
        InvoiceRetrieved {
            client: T::AccountId,
            count: u32,
        },
        /// Invoice hash stored [invoice_hash, invoice_id]
        InvoiceHashStored {
            invoice_hash: [u8; 32],
            invoice_id: u64,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        /// Too many invoices for this client
        TooManyInvoices,
        /// Metadata too long
        MetadataTooLong,
        /// Invoice not found
        InvoiceNotFound,
        /// Invalid invoice data
        InvalidInvoiceData,
        /// Arithmetic overflow
        ArithmeticOverflow,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new invoice
        ///
        /// # Arguments
        /// * `origin` - Transaction origin (invoice creator)
        /// * `client` - Client account ID
        /// * `amount` - Invoice amount
        /// * `metadata` - Invoice metadata (e.g., invoice number, description, JSON data)
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `InvoiceCreated` - Emitted when invoice is successfully created
        /// * `InvoiceHashStored` - Emitted when invoice hash is stored
        ///
        /// # Example
        /// ```ignore
        /// create_invoice(
        ///     origin,
        ///     client_account,
        ///     1000000,
        ///     b"INV-2025-001|Client XYZ|Net 30".to_vec()
        /// )
        /// ```
        #[pallet::call_index(0)]
        #[pallet::weight(10_000)]
        pub fn create_invoice(
            origin: OriginFor<T>,
            client: T::AccountId,
            amount: BalanceOf<T>,
            metadata: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Validate metadata length
            let bounded_metadata: BoundedVec<u8, T::MaxMetadataLength> = metadata
                .try_into()
                .map_err(|_| Error::<T>::MetadataTooLong)?;

            // Get next invoice ID
            let invoice_id = InvoiceCount::<T>::get();
            let current_block = frame_system::Pallet::<T>::block_number();

            // Create invoice struct
            let mut invoice = Invoice {
                id: invoice_id,
                client: client.clone(),
                amount,
                metadata: bounded_metadata,
                timestamp: current_block,
                invoice_hash: [0u8; 32], // Placeholder, will be calculated
                created_by: who.clone(),
            };

            // Calculate SHA256 hash of invoice details
            let invoice_hash = invoice.calculate_hash();
            invoice.invoice_hash = invoice_hash;

            // Get or create invoice list for client
            let mut client_invoices = Invoices::<T>::get(&client);

            // Check if we can add more invoices
            client_invoices
                .try_push(invoice.clone())
                .map_err(|_| Error::<T>::TooManyInvoices)?;

            // Store updated invoice list
            Invoices::<T>::insert(&client, client_invoices);

            // Store hash mapping for quick lookup
            InvoiceByHash::<T>::insert(invoice_hash, invoice_id);

            // Increment invoice counter
            let next_id = invoice_id
                .checked_add(1)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            InvoiceCount::<T>::put(next_id);

            // Emit events
            Self::deposit_event(Event::InvoiceCreated {
                invoice_id,
                client: client.clone(),
                amount,
                invoice_hash,
                created_by: who,
            });

            Self::deposit_event(Event::InvoiceHashStored {
                invoice_hash,
                invoice_id,
            });

            Ok(())
        }

        /// Get all invoices for a specific client
        ///
        /// This is a read-only operation that emits an event for tracking purposes.
        /// In a real application, you would query this via RPC instead of as an extrinsic.
        ///
        /// # Arguments
        /// * `origin` - Transaction origin
        /// * `client` - Client account ID to query invoices for
        ///
        /// # Returns
        /// * `DispatchResult` - Success or error
        ///
        /// # Events
        /// * `InvoiceRetrieved` - Emitted with the count of invoices retrieved
        #[pallet::call_index(1)]
        #[pallet::weight(5_000)]
        pub fn get_invoices(origin: OriginFor<T>, client: T::AccountId) -> DispatchResult {
            let _who = ensure_signed(origin)?;

            // Get invoices for client
            let client_invoices = Invoices::<T>::get(&client);
            let count = client_invoices.len() as u32;

            // Emit event
            Self::deposit_event(Event::InvoiceRetrieved { client, count });

            Ok(())
        }
    }

    // Helper functions (not dispatchable, for RPC or internal use)
    impl<T: Config> Pallet<T> {
        /// Get invoice by hash (helper function for RPC)
        pub fn get_invoice_by_hash(hash: [u8; 32]) -> Option<u64> {
            InvoiceByHash::<T>::get(hash)
        }

        /// Get all invoices for a client (helper function for RPC)
        pub fn get_client_invoices(client: &T::AccountId) -> Vec<Invoice<T>> {
            Invoices::<T>::get(client).into_inner()
        }

        /// Verify invoice hash matches stored data (for Django verification)
        pub fn verify_invoice_hash(client: &T::AccountId, invoice_id: u64) -> bool {
            let invoices = Invoices::<T>::get(client);
            if let Some(invoice) = invoices.iter().find(|i| i.id == invoice_id) {
                let calculated_hash = invoice.calculate_hash();
                calculated_hash == invoice.invoice_hash
            } else {
                false
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use frame_support::{assert_noop, assert_ok, parameter_types, traits::ConstU32};
    use sp_core::H256;
    use sp_runtime::{
        traits::{BlakeTwo256, IdentityLookup},
        BuildStorage,
    };

    type Block = frame_system::mocking::MockBlock<Test>;

    // Configure a mock runtime to test the pallet
    frame_support::construct_runtime!(
        pub enum Test {
            System: frame_system,
            Ledger: pallet,
        }
    );

    parameter_types! {
        pub const BlockHashCount: u64 = 250;
        pub const SS58Prefix: u8 = 42;
    }

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
        type BlockHashCount = BlockHashCount;
        type Version = ();
        type PalletInfo = PalletInfo;
        type AccountData = ();
        type OnNewAccount = ();
        type OnKilledAccount = ();
        type SystemWeightInfo = ();
        type SS58Prefix = SS58Prefix;
        type OnSetCode = ();
        type MaxConsumers = frame_support::traits::ConstU32<16>;
    }

    parameter_types! {
        pub const MaxMetadataLength: u32 = 1024;
        pub const MaxInvoicesPerClient: u32 = 1000;
    }

    impl pallet::Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type Currency = ();
        type MaxMetadataLength = MaxMetadataLength;
        type MaxInvoicesPerClient = MaxInvoicesPerClient;
    }

    // Build genesis storage
    fn new_test_ext() -> sp_io::TestExternalities {
        frame_system::GenesisConfig::<Test>::default()
            .build_storage()
            .unwrap()
            .into()
    }

    #[test]
    fn create_invoice_works() {
        new_test_ext().execute_with(|| {
            // Setup
            let creator = 1u64;
            let client = 2u64;
            let amount = 1000u128;
            let metadata = b"INV-2025-001|Test Client|Net 30".to_vec();

            // Create invoice
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                amount,
                metadata.clone()
            ));

            // Verify invoice count incremented
            assert_eq!(Ledger::invoice_count(), 1);

            // Verify invoice is stored for client
            let client_invoices = Ledger::get_client_invoices(&client);
            assert_eq!(client_invoices.len(), 1);

            // Verify invoice data
            let invoice = &client_invoices[0];
            assert_eq!(invoice.id, 0);
            assert_eq!(invoice.client, client);
            assert_eq!(invoice.amount, amount);
            assert_eq!(invoice.metadata.to_vec(), metadata);
            assert_eq!(invoice.created_by, creator);

            // Verify hash was calculated
            assert_ne!(invoice.invoice_hash, [0u8; 32]);

            // Verify hash mapping
            let stored_id = Ledger::get_invoice_by_hash(invoice.invoice_hash);
            assert_eq!(stored_id, Some(0));
        });
    }

    #[test]
    fn create_multiple_invoices_works() {
        new_test_ext().execute_with(|| {
            let creator = 1u64;
            let client = 2u64;

            // Create first invoice
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                1000u128,
                b"Invoice 1".to_vec()
            ));

            // Create second invoice
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                2000u128,
                b"Invoice 2".to_vec()
            ));

            // Create third invoice
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                3000u128,
                b"Invoice 3".to_vec()
            ));

            // Verify count
            assert_eq!(Ledger::invoice_count(), 3);

            // Verify all invoices are stored
            let client_invoices = Ledger::get_client_invoices(&client);
            assert_eq!(client_invoices.len(), 3);

            // Verify invoice IDs are sequential
            assert_eq!(client_invoices[0].id, 0);
            assert_eq!(client_invoices[1].id, 1);
            assert_eq!(client_invoices[2].id, 2);

            // Verify amounts
            assert_eq!(client_invoices[0].amount, 1000u128);
            assert_eq!(client_invoices[1].amount, 2000u128);
            assert_eq!(client_invoices[2].amount, 3000u128);
        });
    }

    #[test]
    fn multiple_clients_work() {
        new_test_ext().execute_with(|| {
            let creator = 1u64;
            let client1 = 2u64;
            let client2 = 3u64;

            // Create invoices for client 1
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client1,
                1000u128,
                b"Client 1 - Invoice 1".to_vec()
            ));

            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client1,
                1500u128,
                b"Client 1 - Invoice 2".to_vec()
            ));

            // Create invoices for client 2
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client2,
                2000u128,
                b"Client 2 - Invoice 1".to_vec()
            ));

            // Verify client 1 invoices
            let client1_invoices = Ledger::get_client_invoices(&client1);
            assert_eq!(client1_invoices.len(), 2);

            // Verify client 2 invoices
            let client2_invoices = Ledger::get_client_invoices(&client2);
            assert_eq!(client2_invoices.len(), 1);

            // Verify total count
            assert_eq!(Ledger::invoice_count(), 3);
        });
    }

    #[test]
    fn get_invoices_works() {
        new_test_ext().execute_with(|| {
            let creator = 1u64;
            let client = 2u64;

            // Create invoices
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                1000u128,
                b"Invoice 1".to_vec()
            ));

            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                2000u128,
                b"Invoice 2".to_vec()
            ));

            // Get invoices (this emits an event)
            assert_ok!(Ledger::get_invoices(RuntimeOrigin::signed(creator), client));

            // Verify event was emitted (checking system events)
            System::assert_has_event(
                Event::InvoiceRetrieved {
                    client,
                    count: 2,
                }
                .into(),
            );
        });
    }

    #[test]
    fn invoice_hash_is_unique() {
        new_test_ext().execute_with(|| {
            let creator = 1u64;
            let client = 2u64;

            // Create first invoice
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                1000u128,
                b"Invoice 1".to_vec()
            ));

            // Create second invoice with different data
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                1000u128,  // Same amount
                b"Invoice 1".to_vec()  // Same metadata
            ));

            // Get invoices
            let invoices = Ledger::get_client_invoices(&client);

            // Hashes should be different because IDs and timestamps are different
            assert_ne!(invoices[0].invoice_hash, invoices[1].invoice_hash);
        });
    }

    #[test]
    fn verify_invoice_hash_works() {
        new_test_ext().execute_with(|| {
            let creator = 1u64;
            let client = 2u64;

            // Create invoice
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                1000u128,
                b"Test Invoice".to_vec()
            ));

            // Verify hash
            assert!(Ledger::verify_invoice_hash(&client, 0));

            // Verify non-existent invoice returns false
            assert!(!Ledger::verify_invoice_hash(&client, 999));
        });
    }

    #[test]
    fn metadata_too_long_fails() {
        new_test_ext().execute_with(|| {
            let creator = 1u64;
            let client = 2u64;
            
            // Create metadata that exceeds MaxMetadataLength (1024)
            let long_metadata = vec![0u8; 1025];

            // Should fail with MetadataTooLong error
            assert_noop!(
                Ledger::create_invoice(
                    RuntimeOrigin::signed(creator),
                    client,
                    1000u128,
                    long_metadata
                ),
                Error::<Test>::MetadataTooLong
            );
        });
    }

    #[test]
    fn invoice_hash_lookup_works() {
        new_test_ext().execute_with(|| {
            let creator = 1u64;
            let client = 2u64;

            // Create invoice
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                1000u128,
                b"Test Invoice".to_vec()
            ));

            // Get the invoice to obtain its hash
            let invoices = Ledger::get_client_invoices(&client);
            let invoice_hash = invoices[0].invoice_hash;

            // Lookup invoice by hash
            let found_id = Ledger::get_invoice_by_hash(invoice_hash);
            assert_eq!(found_id, Some(0));
        });
    }

    #[test]
    fn events_are_emitted() {
        new_test_ext().execute_with(|| {
            let creator = 1u64;
            let client = 2u64;
            let amount = 1000u128;

            // Create invoice
            assert_ok!(Ledger::create_invoice(
                RuntimeOrigin::signed(creator),
                client,
                amount,
                b"Test Invoice".to_vec()
            ));

            // Get the invoice hash
            let invoices = Ledger::get_client_invoices(&client);
            let invoice_hash = invoices[0].invoice_hash;

            // Check InvoiceCreated event
            System::assert_has_event(
                Event::InvoiceCreated {
                    invoice_id: 0,
                    client,
                    amount,
                    invoice_hash,
                    created_by: creator,
                }
                .into(),
            );

            // Check InvoiceHashStored event
            System::assert_has_event(
                Event::InvoiceHashStored {
                    invoice_hash,
                    invoice_id: 0,
                }
                .into(),
            );
        });
    }
}


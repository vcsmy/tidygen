#![cfg_attr(not(feature = "std"), no_std)]

//! Runtime API definition for the DID pallet

use codec::Codec;
use sp_std::vec::Vec;

sp_api::decl_runtime_apis! {
    /// The API to interact with DID pallet
    pub trait DidApi<AccountId, DidDocument>
    where
        AccountId: Codec,
        DidDocument: Codec,
    {
        /// Get DID document for an account
        fn get_did(account: AccountId) -> Option<DidDocument>;

        /// Get account from DID identifier
        fn get_account_from_did(did_identifier: Vec<u8>) -> Option<AccountId>;

        /// Check if DID is active
        fn is_did_active(account: AccountId) -> bool;

        /// Get total number of DIDs
        fn get_total_dids() -> u64;
    }
}


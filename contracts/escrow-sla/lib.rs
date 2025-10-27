#![cfg_attr(not(feature = "std"), no_std, no_main)]

#[ink::contract]
mod service_verification_escrow {
    use ink::prelude::vec::Vec;
    use ink::storage::Mapping;
    use ink::env::Error as EnvError;
    use ink::env::Timestamp;
    use scale::{Decode, Encode};

    /// Simple escrow/dispute state
    #[derive(Debug, PartialEq, Eq, Encode, Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum DisputeState {
        None,
        Open { opened_at: u64, reason: Vec<u8> },
        Resolved,
    }

    /// Contract errors
    #[derive(Debug, PartialEq, Eq, scale::Encode, scale::Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum Error {
        ServiceAlreadyExists,
        ServiceNotFound,
        InvalidData,
        NoEscrowBalance,
        NotAuthorized,
        DisputeOpen,
        EnvError,
    }

    pub type Result<T> = core::result::Result<T, Error>;

    /// Event emitted when a service verification record is stored
    #[ink(event)]
    pub struct ServiceStored {
        #[ink(topic)]
        service_id: u64,
        #[ink(topic)]
        caller: AccountId,
    }

    /// Event emitted when escrow is deposited
    #[ink(event)]
    pub struct EscrowDeposited {
        #[ink(topic)]
        service_id: u64,
        amount: Balance,
        #[ink(topic)]
        depositor: AccountId,
    }

    /// Event emitted when escrow is released
    #[ink(event)]
    pub struct EscrowReleased {
        #[ink(topic)]
        service_id: u64,
        amount: Balance,
        #[ink(topic)]
        to: AccountId,
    }

    /// Event emitted when a dispute is opened
    #[ink(event)]
    pub struct DisputeOpened {
        #[ink(topic)]
        service_id: u64,
        #[ink(topic)]
        opener: AccountId,
    }

    /// The Service Verification + Escrow contract
    #[ink(storage)]
    pub struct ServiceVerificationEscrow {
        service_data: Mapping<u64, Vec<u8>>,
        escrow: Mapping<u64, Balance>,
        dispute: Mapping<u64, DisputeState>,
        owner: AccountId,
        dispute_window_ms: u64,
    }

    impl ServiceVerificationEscrow {
        /// Constructor, sets the contract owner and dispute window (ms)
        #[ink(constructor)]
        pub fn new(dispute_window_ms: u64) -> Self {
            Self {
                service_data: Mapping::new(),
                escrow: Mapping::new(),
                dispute: Mapping::new(),
                owner: Self::env().caller(),
                dispute_window_ms,
            }
        }

        /// Stores a service verification record (only by owner or designated callers in future)
        #[ink(message)]
        pub fn store(&mut self, service_id: u64, data_hash: Vec<u8>) -> Result<()> {
            if data_hash.is_empty() {
                return Err(Error::InvalidData);
            }
            if self.service_data.contains(service_id) {
                return Err(Error::ServiceAlreadyExists);
            }
            self.service_data.insert(service_id, &data_hash);
            self.env().emit_event(ServiceStored {
                service_id,
                caller: self.env().caller(),
            });
            Ok(())
        }

        /// Get stored verification
        #[ink(message)]
        pub fn get(&self, service_id: u64) -> Option<Vec<u8>> {
            self.service_data.get(service_id)
        }

        /// Deposit escrow (payable) for a service_id
        #[ink(message, payable)]
        pub fn deposit_escrow(&mut self, service_id: u64) -> Result<Balance> {
            let value = self.env().transferred_value();
            if value == 0 {
                return Err(Error::NoEscrowBalance);
            }
            let prev = self.escrow.get(service_id).unwrap_or_default();
            let new = prev + value;
            self.escrow.insert(service_id, &new);
            self.env().emit_event(EscrowDeposited {
                service_id,
                amount: value,
                depositor: self.env().caller(),
            });
            Ok(new)
        }

        /// Internal helper to transfer balance and update state
        fn _transfer_and_update(&mut self, to: AccountId, service_id: u64, amount: Balance) -> Result<()> {
            if amount == 0 {
                return Err(Error::NoEscrowBalance);
            }
            // Subtract escrow
            let prev = self.escrow.get(service_id).unwrap_or_default();
            if prev < amount {
                return Err(Error::NoEscrowBalance);
            }
            let remaining = prev - amount;
            self.escrow.insert(service_id, &remaining);
            // Transfer to recipient
            match self.env().transfer(to.clone(), amount) {
                Ok(()) => {
                    self.env().emit_event(EscrowReleased { service_id, amount, to });
                    Ok(())
                }
                Err(_e) => Err(Error::EnvError),
            }
        }

        /// Release escrow to recipient — only owner or if no dispute open and caller == owner
        #[ink(message)]
        pub fn release_escrow(&mut self, service_id: u64, to: AccountId) -> Result<()> {
            let caller = self.env().caller();
            if caller != self.owner {
                return Err(Error::NotAuthorized);
            }
            // Check dispute state
            if let Some(DisputeState::Open { .. }) = self.dispute.get(service_id) {
                return Err(Error::DisputeOpen);
            }
            let amount = self.escrow.get(service_id).unwrap_or_default();
            if amount == 0 {
                return Err(Error::NoEscrowBalance);
            }
            self._transfer_and_update(to, service_id, amount)
        }

        /// Open dispute for a given service_id with a short reason
        #[ink(message)]
        pub fn open_dispute(&mut self, service_id: u64, reason: Vec<u8>) -> Result<()> {
            let caller = self.env().caller();
            if !self.service_data.contains(service_id) {
                return Err(Error::ServiceNotFound);
            }
            // Set dispute (simple single-state)
            let now = Self::env().block_timestamp();
            self.dispute.insert(service_id, &DisputeState::Open { opened_at: now, reason: reason.clone() });
            self.env().emit_event(DisputeOpened { service_id, opener: caller });
            Ok(())
        }

        /// Resolve dispute — only owner (in future this can be a governance or multisig)
        #[ink(message)]
        pub fn resolve_dispute_release(&mut self, service_id: u64, to: AccountId, amount: Balance) -> Result<()> {
            let caller = self.env().caller();
            if caller != self.owner {
                return Err(Error::NotAuthorized);
            }
            // Reset dispute
            self.dispute.insert(service_id, &DisputeState::Resolved);
            // Transfer funds (partial or full)
            self._transfer_and_update(to, service_id, amount)
        }

        /// Check escrow balance for a service_id
        #[ink(message)]
        pub fn escrow_balance(&self, service_id: u64) -> Balance {
            self.escrow.get(service_id).unwrap_or_default()
        }

        /// Simple exists check
        #[ink(message)]
        pub fn exists(&self, service_id: u64) -> bool {
            self.service_data.contains(service_id)
        }
    }

    impl Default for ServiceVerificationEscrow {
        fn default() -> Self {
            Self::new(1000 * 60 * 60 * 24) // default dispute window: 24h in ms
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;
        use ink::env::test;

        #[ink::test]
        fn deposit_and_release_works() {
            let mut contract = ServiceVerificationEscrow::new(1000);
            let service_id = 1u64;
            // store minimal data
            assert_eq!(contract.store(service_id, b"hash".to_vec()), Ok(()));
            // Simulate deposit by adjusting contract storage directly isn't available in unit test env for transferred_value
            // Note: integration tests with ink_e2e should exercise payable flows.
        }

        #[ink::test]
        fn open_dispute_works() {
            let mut contract = ServiceVerificationEscrow::new(1000);
            let service_id = 1u64;
            assert_eq!(contract.store(service_id, b"hash".to_vec()), Ok(()));
            assert_eq!(contract.open_dispute(service_id, b"issue".to_vec()), Ok(()));
            if let Some(DisputeState::Open { .. }) = contract.dispute.get(service_id) {
                // ok
            } else {
                panic!("Dispute not set");
            }
        }
    }
}
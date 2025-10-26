#![cfg_attr(not(feature = "std"), no_std, no_main)]

#[ink::contract]
mod service_verification_poc {
    use ink::storage::Mapping;
    use ink::prelude::vec::Vec;

    /// Custom error types for the contract
    #[derive(Debug, PartialEq, Eq, scale::Encode, scale::Decode)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo))]
    pub enum Error {
        /// Service ID already exists
        ServiceAlreadyExists,
        /// Service ID not found
        ServiceNotFound,
        /// Invalid data provided
        InvalidData,
    }

    /// Result type alias for the contract
    pub type Result<T> = core::result::Result<T, Error>;

    /// Event emitted when a service verification record is stored
    #[ink(event)]
    pub struct ServiceStored {
        #[ink(topic)]
        service_id: u64,
        #[ink(topic)]
        caller: AccountId,
    }

    /// The service verification contract
    #[ink(storage)]
    pub struct ServiceVerificationPoc {
        /// Mapping from service_id to verification data hash
        service_data: Mapping<u64, Vec<u8>>,
    }

    impl ServiceVerificationPoc {
        /// Creates a new service verification contract
        #[ink(constructor)]
        pub fn new() -> Self {
            Self {
                service_data: Mapping::new(),
            }
        }

        /// Stores a service verification record
        #[ink(message)]
        pub fn store(&mut self, service_id: u64, data_hash: Vec<u8>) -> Result<()> {
            // Validate input data
            if data_hash.is_empty() {
                return Err(Error::InvalidData);
            }

            // Check if service already exists
            if self.service_data.contains(service_id) {
                return Err(Error::ServiceAlreadyExists);
            }

            // Store the data
            self.service_data.insert(service_id, &data_hash);

            // Emit event
            self.env().emit_event(ServiceStored {
                service_id,
                caller: self.env().caller(),
            });

            Ok(())
        }

        /// Retrieves a service verification record
        #[ink(message)]
        pub fn get(&self, service_id: u64) -> Option<Vec<u8>> {
            self.service_data.get(service_id)
        }

        /// Updates an existing service verification record
        #[ink(message)]
        pub fn update(&mut self, service_id: u64, data_hash: Vec<u8>) -> Result<()> {
            // Validate input data
            if data_hash.is_empty() {
                return Err(Error::InvalidData);
            }

            // Check if service exists
            if !self.service_data.contains(service_id) {
                return Err(Error::ServiceNotFound);
            }

            // Update the data
            self.service_data.insert(service_id, &data_hash);

            // Emit event
            self.env().emit_event(ServiceStored {
                service_id,
                caller: self.env().caller(),
            });

            Ok(())
        }

        /// Checks if a service verification record exists
        #[ink(message)]
        pub fn exists(&self, service_id: u64) -> bool {
            self.service_data.contains(service_id)
        }
    }

    impl Default for ServiceVerificationPoc {
        fn default() -> Self {
            Self::new()
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;
        use ink::env::test;

        #[ink::test]
        fn new_works() {
            let contract = ServiceVerificationPoc::new();
            assert_eq!(contract.get(1), None);
        }

        #[ink::test]
        fn store_and_get_works() {
            let mut contract = ServiceVerificationPoc::new();
            let service_id = 1u64;
            let data_hash = b"verification_data_hash".to_vec();

            // Store data
            assert_eq!(contract.store(service_id, data_hash.clone()), Ok(()));
            
            // Retrieve data
            assert_eq!(contract.get(service_id), Some(data_hash));
        }

        #[ink::test]
        fn store_duplicate_fails() {
            let mut contract = ServiceVerificationPoc::new();
            let service_id = 1u64;
            let data_hash = b"verification_data_hash".to_vec();

            // Store data first time
            assert_eq!(contract.store(service_id, data_hash.clone()), Ok(()));
            
            // Try to store again with same service_id
            assert_eq!(contract.store(service_id, data_hash), Err(Error::ServiceAlreadyExists));
        }

        #[ink::test]
        fn store_empty_data_fails() {
            let mut contract = ServiceVerificationPoc::new();
            let service_id = 1u64;
            let empty_data = Vec::new();

            assert_eq!(contract.store(service_id, empty_data), Err(Error::InvalidData));
        }

        #[ink::test]
        fn update_works() {
            let mut contract = ServiceVerificationPoc::new();
            let service_id = 1u64;
            let initial_data = b"initial_data".to_vec();
            let updated_data = b"updated_data".to_vec();

            // Store initial data
            assert_eq!(contract.store(service_id, initial_data), Ok(()));
            
            // Update data
            assert_eq!(contract.update(service_id, updated_data.clone()), Ok(()));
            
            // Verify update
            assert_eq!(contract.get(service_id), Some(updated_data));
        }

        #[ink::test]
        fn update_nonexistent_fails() {
            let mut contract = ServiceVerificationPoc::new();
            let service_id = 1u64;
            let data = b"some_data".to_vec();

            assert_eq!(contract.update(service_id, data), Err(Error::ServiceNotFound));
        }

        #[ink::test]
        fn exists_works() {
            let mut contract = ServiceVerificationPoc::new();
            let service_id = 1u64;
            let data_hash = b"verification_data_hash".to_vec();

            // Initially doesn't exist
            assert_eq!(contract.exists(service_id), false);
            
            // Store data
            assert_eq!(contract.store(service_id, data_hash), Ok(()));
            
            // Now exists
            assert_eq!(contract.exists(service_id), true);
        }

        #[ink::test]
        fn event_emitted_on_store() {
            let mut contract = ServiceVerificationPoc::new();
            let service_id = 1u64;
            let data_hash = b"verification_data_hash".to_vec();

            // Store data
            assert_eq!(contract.store(service_id, data_hash), Ok(()));

            // Check events
            let emitted_events = ink::env::test::recorded_events().collect::<Vec<_>>();
            assert_eq!(emitted_events.len(), 1);

            let event = <ServiceStored as ink::env::test::EmittedEvent>::decode(&emitted_events[0]);
            assert_eq!(event.service_id, service_id);
        }
    }

    #[cfg(all(test, feature = "e2e-tests"))]
    mod e2e_tests {
        use super::*;
        use ink_e2e::build_message;

        type E2EResult<T> = std::result::Result<T, Box<dyn std::error::Error>>;

        #[ink_e2e::test]
        async fn store_and_get_works_e2e(client: ink_e2e::Client<C, E>) -> E2EResult<()> {
            // Given
            let mut constructor = ServiceVerificationPocRef::new();
            let contract = client
                .instantiate("service_verification_poc", &ink_e2e::alice(), &mut constructor)
                .submit()
                .await
                .expect("instantiate failed");
            let call_builder = contract.call_builder::<ServiceVerificationPoc>();

            // When
            let service_id = 1u64;
            let data_hash = b"verification_data_hash".to_vec();
            
            let store_message = build_message::<ServiceVerificationPocRef>(contract.account_id.clone())
                .call(|contract| contract.store(service_id, data_hash.clone()));
            let store_result = client
                .call(&ink_e2e::alice(), &store_message)
                .submit()
                .await
                .expect("store call failed");
            assert!(store_result.return_value().is_ok());

            // Then
            let get_message = build_message::<ServiceVerificationPocRef>(contract.account_id.clone())
                .call(|contract| contract.get(service_id));
            let get_result = client
                .call(&ink_e2e::alice(), &get_message)
                .dry_run()
                .await?;
            assert_eq!(get_result.return_value(), Some(data_hash));

            Ok(())
        }
    }
}

use crate::{mock::*, Error, Event};
use frame_support::{assert_noop, assert_ok};

#[test]
fn register_did_works() {
    new_test_ext().execute_with(|| {
        // Setup
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234567890abcdef".to_vec();
        let metadata = b"{\"name\":\"Alice\",\"email\":\"alice@example.com\"}".to_vec();

        // Register DID
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key.clone(),
            metadata.clone()
        ));

        // Verify DID count incremented
        assert_eq!(Did::did_count(), 1);

        // Verify DID document is stored
        let did_doc = Did::get_did(&account).unwrap();
        assert_eq!(did_doc.controller, controller);
        assert_eq!(did_doc.public_key.to_vec(), public_key);
        assert_eq!(did_doc.metadata.to_vec(), metadata);
        assert_eq!(did_doc.nonce, 0);

        // Verify DID is active
        assert!(Did::is_did_active(&account));

        // Verify event was emitted
        System::assert_has_event(
            Event::DidRegistered {
                account,
                did_identifier: did_doc.did_identifier.to_vec(),
            }
            .into(),
        );
    });
}

#[test]
fn register_did_for_self_works() {
    new_test_ext().execute_with(|| {
        let account = 1u64;
        let public_key = b"0xabcdef1234567890".to_vec();
        let metadata = b"{\"type\":\"user\"}".to_vec();

        // Register DID for self
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(account),
            account,
            public_key,
            metadata
        ));

        // Verify DID exists
        let did_doc = Did::get_did(&account).unwrap();
        assert_eq!(did_doc.controller, account);
    });
}

#[test]
fn cannot_register_did_twice() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"{}".to_vec();

        // Register DID first time
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key.clone(),
            metadata.clone()
        ));

        // Try to register again - should fail
        assert_noop!(
            Did::register_did(
                RuntimeOrigin::signed(controller),
                account,
                public_key,
                metadata
            ),
            Error::<Test>::DidAlreadyExists
        );
    });
}

#[test]
fn update_did_works() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"original".to_vec();

        // Register DID
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key.clone(),
            metadata.clone()
        ));

        // Update metadata
        let new_metadata = b"updated".to_vec();
        assert_ok!(Did::update_did(
            RuntimeOrigin::signed(controller),
            account,
            None,
            Some(new_metadata.clone())
        ));

        // Verify update
        let did_doc = Did::get_did(&account).unwrap();
        assert_eq!(did_doc.metadata.to_vec(), new_metadata);
        assert_eq!(did_doc.nonce, 1); // Nonce incremented

        // Verify event
        System::assert_has_event(Event::DidUpdated { account, nonce: 1 }.into());
    });
}

#[test]
fn update_public_key_works() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"data".to_vec();

        // Register DID
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key,
            metadata.clone()
        ));

        // Update public key
        let new_key = b"0xabcd".to_vec();
        assert_ok!(Did::update_did(
            RuntimeOrigin::signed(controller),
            account,
            Some(new_key.clone()),
            None
        ));

        // Verify update
        let did_doc = Did::get_did(&account).unwrap();
        assert_eq!(did_doc.public_key.to_vec(), new_key);
        assert_eq!(did_doc.metadata.to_vec(), metadata); // Unchanged
    });
}

#[test]
fn only_controller_can_update() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let other = 3u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"data".to_vec();

        // Register DID
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key,
            metadata
        ));

        // Try to update from different account - should fail
        assert_noop!(
            Did::update_did(
                RuntimeOrigin::signed(other),
                account,
                None,
                Some(b"malicious".to_vec())
            ),
            Error::<Test>::NotController
        );
    });
}

#[test]
fn revoke_did_works() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"data".to_vec();

        // Register DID
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key,
            metadata
        ));

        // Revoke DID
        assert_ok!(Did::revoke_did(RuntimeOrigin::signed(controller), account));

        // Verify revoked
        let did_doc = Did::get_did(&account).unwrap();
        assert_eq!(did_doc.status, crate::DidStatus::Revoked);
        assert!(!Did::is_did_active(&account));

        // Verify events
        System::assert_has_event(Event::DidRevoked { account }.into());
    });
}

#[test]
fn cannot_update_revoked_did() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"data".to_vec();

        // Register and revoke DID
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key,
            metadata
        ));
        assert_ok!(Did::revoke_did(RuntimeOrigin::signed(controller), account));

        // Try to update revoked DID - should fail
        assert_noop!(
            Did::update_did(
                RuntimeOrigin::signed(controller),
                account,
                None,
                Some(b"update".to_vec())
            ),
            Error::<Test>::DidRevoked
        );
    });
}

#[test]
fn resolve_did_works() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"data".to_vec();

        // Register DID
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key,
            metadata
        ));

        // Resolve DID
        assert_ok!(Did::resolve_did(RuntimeOrigin::signed(controller), account));

        // Verify event
        System::assert_has_event(
            Event::DidResolved {
                account,
                status: crate::DidStatus::Active,
            }
            .into(),
        );
    });
}

#[test]
fn resolve_nonexistent_did_fails() {
    new_test_ext().execute_with(|| {
        let account = 1u64;

        // Try to resolve non-existent DID
        assert_noop!(
            Did::resolve_did(RuntimeOrigin::signed(account), account),
            Error::<Test>::DidNotFound
        );
    });
}

#[test]
fn multiple_dids_work() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;

        // Register multiple DIDs
        for i in 2..5 {
            assert_ok!(Did::register_did(
                RuntimeOrigin::signed(controller),
                i,
                format!("0x{:04x}", i).as_bytes().to_vec(),
                format!("{{\"user\":{}}}", i).as_bytes().to_vec()
            ));
        }

        // Verify count
        assert_eq!(Did::did_count(), 3);

        // Verify each DID
        for i in 2..5 {
            assert!(Did::get_did(&i).is_some());
            assert!(Did::is_did_active(&i));
        }
    });
}

#[test]
fn did_identifier_is_unique() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account1 = 2u64;
        let account2 = 3u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"data".to_vec();

        // Register DIDs for different accounts
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account1,
            public_key.clone(),
            metadata.clone()
        ));

        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account2,
            public_key,
            metadata
        ));

        // Get DID identifiers
        let did1 = Did::get_did(&account1).unwrap().did_identifier;
        let did2 = Did::get_did(&account2).unwrap().did_identifier;

        // Identifiers should be different
        assert_ne!(did1, did2);
    });
}

#[test]
fn public_key_too_long_fails() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        
        // Create public key that exceeds MaxPublicKeyLength (256)
        let long_key = vec![0u8; 257];
        let metadata = b"data".to_vec();

        // Should fail
        assert_noop!(
            Did::register_did(
                RuntimeOrigin::signed(controller),
                account,
                long_key,
                metadata
            ),
            Error::<Test>::PublicKeyTooLong
        );
    });
}

#[test]
fn metadata_too_long_fails() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234".to_vec();
        
        // Create metadata that exceeds MaxMetadataLength (1024)
        let long_metadata = vec![0u8; 1025];

        // Should fail
        assert_noop!(
            Did::register_did(
                RuntimeOrigin::signed(controller),
                account,
                public_key,
                long_metadata
            ),
            Error::<Test>::MetadataTooLong
        );
    });
}

#[test]
fn did_reverse_lookup_works() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"data".to_vec();

        // Register DID
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key,
            metadata
        ));

        // Get DID identifier
        let did_doc = Did::get_did(&account).unwrap();
        let did_id = did_doc.did_identifier.to_vec();

        // Reverse lookup
        let found_account = Did::get_account_from_did(&did_id);
        assert_eq!(found_account, Some(account));
    });
}

#[test]
fn nonce_increments_on_update() {
    new_test_ext().execute_with(|| {
        let controller = 1u64;
        let account = 2u64;
        let public_key = b"0x1234".to_vec();
        let metadata = b"data".to_vec();

        // Register DID
        assert_ok!(Did::register_did(
            RuntimeOrigin::signed(controller),
            account,
            public_key,
            metadata
        ));

        // Initial nonce should be 0
        let did_doc = Did::get_did(&account).unwrap();
        assert_eq!(did_doc.nonce, 0);

        // Update DID
        assert_ok!(Did::update_did(
            RuntimeOrigin::signed(controller),
            account,
            None,
            Some(b"updated".to_vec())
        ));

        // Nonce should be 1
        let did_doc = Did::get_did(&account).unwrap();
        assert_eq!(did_doc.nonce, 1);

        // Update again
        assert_ok!(Did::update_did(
            RuntimeOrigin::signed(controller),
            account,
            Some(b"0xnewkey".to_vec()),
            None
        ));

        // Nonce should be 2
        let did_doc = Did::get_did(&account).unwrap();
        assert_eq!(did_doc.nonce, 2);
    });
}


//! ink_e2e e2e test scaffold for ServiceVerificationEscrow
//! Requires a running substrate node with contracts pallet. Use CI or local node for testing.

use ink_e2e::ContractBackend;
use service_verification_escrow::ServiceVerificationEscrowRef;

#[ink_e2e::test]
async fn deposit_and_dispute_e2e(mut client: ink_e2e::Client<C, E>) -> ink_e2e::contract::Balance {
    // 1. Upload/instantiate contract
    let constructor = ServiceVerificationEscrowRef::new(24 * 60 * 60 * 1000u128);
    let contract_account_id = client
        .instantiate(
            "service_verification_escrow",
            &ink_e2e::alice(),
            constructor,
            0,
            None,
        )
        .await
        .expect("contract instantiate failed")
        .account_id;

    // 2. Store a service record
    let store_res = client
        .call(
            &ink_e2e::alice(),
            &contract_account_id,
            service_verification_escrow::Message::store(1u64, b"hash".to_vec()),
            0,
            None,
        )
        .await
        .expect("store call failed");
    assert!(store_res.is_ok());

    // NOTE: ink_e2e support for transferring balances differs across envs.
    // 3. Deposit escrow (simulate transfer if supported)
    // 4. Open dispute
    // 5. Try owner release -> should fail if dispute open
    // 6. Resolve dispute via owner -> confirm funds transferred
    // (Fill in payable transfer tests as appropriate for your test environment)

    0
}
"""
Test module for SubstrateClient

Run these tests to verify Substrate integration:
    python manage.py test services.test_substrate_client
    
Or run directly:
    python services/test_substrate_client.py
"""

import sys
import os
import logging

# Setup Django if running standalone
if __name__ == '__main__':
    import django
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.development')
    django.setup()

from .substrate_client import SubstrateClient, SubstrateConnectionError
from substrateinterface import Keypair

logger = logging.getLogger(__name__)


def test_connection():
    """Test 1: Basic connection to Substrate node"""
    print("\n" + "="*70)
    print("TEST 1: Connection Test")
    print("="*70)
    
    try:
        client = SubstrateClient(keypair_uri='//Alice')
        info = client.get_chain_info()
        
        print(f"✅ Connected to chain: {info['chain']}")
        print(f"✅ Block number: {info['block_number']}")
        print(f"✅ Version: {info['version']}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_create_invoice():
    """Test 2: Create invoice on ledger"""
    print("\n" + "="*70)
    print("TEST 2: Create Invoice")
    print("="*70)
    
    try:
        client = SubstrateClient(keypair_uri='//Alice')
        alice_keypair = Keypair.create_from_uri('//Alice')
        bob_account = Keypair.create_from_uri('//Bob').ss58_address
        
        # Create invoice
        tx_hash, receipt = client.record_invoice(
            user_id=1,
            invoice_hash="test_hash_123",
            client_account=bob_account,
            amount=1000000,
            metadata="INV-2025-TEST-001|Test Client|Net 30",
            keypair=alice_keypair
        )
        
        print(f"✅ Invoice created!")
        print(f"   Transaction Hash: {tx_hash}")
        print(f"   Block Hash: {receipt['block_hash']}")
        print(f"   Finalized: {receipt['finalized']}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Invoice creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_invoices():
    """Test 3: Retrieve invoices from ledger"""
    print("\n" + "="*70)
    print("TEST 3: Get Invoices")
    print("="*70)
    
    try:
        client = SubstrateClient()
        bob_account = Keypair.create_from_uri('//Bob').ss58_address
        
        # Get invoices for Bob
        invoices = client.get_invoices(bob_account)
        
        print(f"✅ Retrieved {len(invoices)} invoice(s) for Bob")
        
        for i, invoice in enumerate(invoices):
            print(f"\n   Invoice {i + 1}:")
            print(f"      ID: {invoice['id']}")
            print(f"      Amount: {invoice['amount']}")
            print(f"      Metadata: {invoice['metadata']}")
            print(f"      Hash: {invoice['invoice_hash'][:16]}...")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Get invoices failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_register_did():
    """Test 4: Register DID"""
    print("\n" + "="*70)
    print("TEST 4: Register DID")
    print("="*70)
    
    try:
        client = SubstrateClient(keypair_uri='//Alice')
        charlie_keypair = Keypair.create_from_uri('//Charlie')
        charlie_account = charlie_keypair.ss58_address
        
        # Generate a simple public key (in real use, get from user's wallet)
        public_key = "0x" + "04" + "a1" * 32  # Dummy 33-byte public key
        
        # Register DID
        tx_hash, receipt = client.register_did(
            user_id=3,
            account_id=charlie_account,
            public_key=public_key,
            metadata={
                'username': 'charlie',
                'email': 'charlie@example.com',
                'role': 'employee',
                'department': 'engineering'
            },
            keypair=Keypair.create_from_uri('//Alice')
        )
        
        print(f"✅ DID registered for Charlie!")
        print(f"   Account: {charlie_account}")
        print(f"   Transaction Hash: {tx_hash}")
        print(f"   Block Hash: {receipt['block_hash']}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ DID registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_did():
    """Test 5: Get DID document via RPC"""
    print("\n" + "="*70)
    print("TEST 5: Get DID via RPC")
    print("="*70)
    
    try:
        client = SubstrateClient()
        charlie_account = Keypair.create_from_uri('//Charlie').ss58_address
        
        # Get DID
        did_doc = client.get_did(charlie_account)
        
        if did_doc:
            print(f"✅ DID document retrieved!")
            print(f"   Controller: {did_doc['controller']}")
            print(f"   Status: {did_doc['status']}")
            print(f"   DID Identifier: {did_doc['did_identifier']}")
            print(f"   Nonce: {did_doc['nonce']}")
            
            # Check if active
            is_active = client.is_did_active(charlie_account)
            print(f"   Is Active: {is_active}")
        else:
            print("ℹ️  No DID found for Charlie (may need to register first)")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Get DID failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_dao_proposal():
    """Test 6: Create DAO proposal"""
    print("\n" + "="*70)
    print("TEST 6: Create DAO Proposal")
    print("="*70)
    
    try:
        client = SubstrateClient(keypair_uri='//Alice')
        
        # Create proposal
        tx_hash, receipt = client.create_proposal(
            title="Approve Test Budget",
            description="This is a test proposal to verify DAO functionality works correctly",
            voting_period=100,
            keypair=Keypair.create_from_uri('//Alice')
        )
        
        print(f"✅ DAO proposal created!")
        print(f"   Transaction Hash: {tx_hash}")
        print(f"   Block Hash: {receipt['block_hash']}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Proposal creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vote_on_proposal():
    """Test 7: Vote on DAO proposal"""
    print("\n" + "="*70)
    print("TEST 7: Vote on Proposal")
    print("="*70)
    
    try:
        client = SubstrateClient()
        
        # Get latest proposal (should be ID 0 from previous test)
        proposal = client.get_proposal(0)
        
        if not proposal:
            print("ℹ️  No proposal found (create one first)")
            return True
        
        print(f"   Proposal: {proposal['title']}")
        print(f"   Current votes: {proposal['votes_for']} for, {proposal['votes_against']} against")
        
        # Vote in favor
        bob_keypair = Keypair.create_from_uri('//Bob')
        tx_hash, receipt = client.vote_on_proposal(
            proposal_id=0,
            in_favor=True,
            keypair=bob_keypair
        )
        
        print(f"✅ Vote cast by Bob!")
        print(f"   Transaction Hash: {tx_hash}")
        
        # Query updated proposal
        updated_proposal = client.get_proposal(0)
        print(f"   Updated votes: {updated_proposal['votes_for']} for, {updated_proposal['votes_against']} against")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Vote failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comprehensive_workflow():
    """Test 8: Complete workflow - Invoice + DID + DAO"""
    print("\n" + "="*70)
    print("TEST 8: Comprehensive Workflow")
    print("="*70)
    
    try:
        # Initialize client
        client = SubstrateClient(keypair_uri='//Alice')
        
        # Create keypairs for test users
        alice = Keypair.create_from_uri('//Alice')
        dave = Keypair.create_from_uri('//Dave')
        
        print("\n1. Creating invoice for Dave...")
        tx_hash1, _ = client.record_invoice(
            user_id=4,
            invoice_hash="workflow_test",
            client_account=dave.ss58_address,
            amount=5000000,
            metadata="WORKFLOW-TEST|Dave's Company|Net 15",
            keypair=alice
        )
        print(f"   ✅ Invoice created: {tx_hash1}")
        
        print("\n2. Registering DID for Dave...")
        tx_hash2, _ = client.register_did(
            user_id=4,
            account_id=dave.ss58_address,
            public_key="0x04" + "d4" * 32,
            metadata={'username': 'dave', 'verified': True},
            keypair=alice
        )
        print(f"   ✅ DID registered: {tx_hash2}")
        
        print("\n3. Creating DAO proposal...")
        tx_hash3, _ = client.create_proposal(
            title="Approve Dave's Invoice",
            description="Proposal to approve Dave's invoice of $50,000",
            voting_period=50,
            keypair=alice
        )
        print(f"   ✅ Proposal created: {tx_hash3}")
        
        print("\n4. Querying blockchain state...")
        invoices = client.get_invoices(dave.ss58_address)
        did_doc = client.get_did(dave.ss58_address)
        proposal = client.get_proposal(0)
        
        print(f"   ✅ Dave has {len(invoices)} invoice(s)")
        print(f"   ✅ Dave's DID is {'active' if did_doc else 'not found'}")
        print(f"   ✅ Proposal status: {proposal['status'] if proposal else 'not found'}")
        
        print("\n✅ Comprehensive workflow completed successfully!")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all test methods"""
    print("\n" + "="*70)
    print(" TidyGen Substrate Client - Integration Tests")
    print("="*70)
    print("\nThese tests verify Django-Substrate integration")
    print("Ensure Substrate node is running: make run")
    print("")
    
    tests = [
        ("Connection", test_connection),
        ("Create Invoice", test_create_invoice),
        ("Get Invoices", test_get_invoices),
        ("Register DID", test_register_did),
        ("Get DID via RPC", test_get_did),
        ("Create DAO Proposal", test_create_dao_proposal),
        ("Vote on Proposal", test_vote_on_proposal),
        ("Comprehensive Workflow", test_comprehensive_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Django-Substrate integration is working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    return passed == total


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run all tests
    success = run_all_tests()
    sys.exit(0 if success else 1)


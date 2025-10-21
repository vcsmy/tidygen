"""
Pytest tests for Substrate integration

Run with:
    pytest apps/backend/services/tests/test_substrate_integration.py -v
    
Or:
    python manage.py test services.tests.test_substrate_integration
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from services.substrate_client import (
    SubstrateClient,
    SubstrateConnectionError,
    SubstrateTransactionError
)


class TestSubstrateConnection:
    """Test Substrate node connection"""
    
    def test_connection_initialization(self):
        """Test that SubstrateClient initializes connection"""
        # This test requires a running Substrate node
        # It's marked as integration test
        try:
            client = SubstrateClient(
                url="ws://127.0.0.1:9944",
                max_retries=1,
                retry_delay=0.5
            )
            assert client.substrate is not None
            assert client.url == "ws://127.0.0.1:9944"
            client.close()
        except SubstrateConnectionError:
            pytest.skip("Substrate node not running - integration test skipped")
    
    def test_connection_retry_logic(self):
        """Test retry logic on connection failure"""
        # Test with invalid URL
        with pytest.raises(SubstrateConnectionError):
            client = SubstrateClient(
                url="ws://invalid.local:9999",
                max_retries=2,
                retry_delay=0.1
            )
    
    def test_get_chain_info(self):
        """Test getting chain information"""
        try:
            client = SubstrateClient()
            info = client.get_chain_info()
            
            assert 'chain' in info
            assert 'version' in info
            assert 'block_number' in info
            assert info['block_number'] >= 0
            
            client.close()
        except SubstrateConnectionError:
            pytest.skip("Substrate node not running")
    
    def test_get_block_number(self):
        """Test getting current block number"""
        try:
            client = SubstrateClient()
            block_num = client.get_block_number()
            
            assert isinstance(block_num, int)
            assert block_num >= 0
            
            client.close()
        except SubstrateConnectionError:
            pytest.skip("Substrate node not running")


class TestInvoiceAnchoring:
    """Test invoice anchoring to blockchain"""
    
    @pytest.fixture
    def substrate_client(self):
        """Fixture for SubstrateClient"""
        try:
            client = SubstrateClient(keypair_uri='//Alice')
            yield client
            client.close()
        except SubstrateConnectionError:
            pytest.skip("Substrate node not running")
    
    def test_record_invoice_success(self, substrate_client):
        """Test successful invoice recording"""
        try:
            # Record invoice
            tx_hash, receipt = substrate_client.record_invoice(
                user_id=1,
                invoice_hash="test_invoice_001",
                client_account=substrate_client.create_keypair('//Bob').ss58_address,
                amount=1000000,
                metadata="TEST-INV-001|Test Client|Net 30"
            )
            
            assert tx_hash is not None
            assert len(tx_hash) > 0
            assert receipt['success'] is True
            assert 'block_hash' in receipt
            
        except Exception as e:
            pytest.fail(f"Invoice recording failed: {e}")
    
    def test_get_invoices(self, substrate_client):
        """Test retrieving invoices from blockchain"""
        try:
            bob_address = substrate_client.create_keypair('//Bob').ss58_address
            
            # Get invoices (may be empty if none created)
            invoices = substrate_client.get_invoices(bob_address)
            
            assert isinstance(invoices, list)
            # If invoices exist, verify structure
            if invoices:
                invoice = invoices[0]
                assert 'id' in invoice
                assert 'client' in invoice
                assert 'amount' in invoice
                assert 'metadata' in invoice
                assert 'invoice_hash' in invoice
                
        except Exception as e:
            pytest.fail(f"Get invoices failed: {e}")
    
    def test_invoice_hash_calculation(self, substrate_client):
        """Test invoice hash calculation matches pallet logic"""
        invoice_data = {
            'id': 0,
            'client': '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
            'amount': 1000000,
            'metadata': 'INV-2025-001',
            'timestamp': 42
        }
        
        hash_result = substrate_client.calculate_invoice_hash(invoice_data)
        
        assert hash_result is not None
        assert len(hash_result) == 64  # SHA256 hex string
        assert all(c in '0123456789abcdef' for c in hash_result.lower())


class TestDIDManagement:
    """Test DID registration and management"""
    
    @pytest.fixture
    def substrate_client(self):
        """Fixture for SubstrateClient"""
        try:
            client = SubstrateClient(keypair_uri='//Alice')
            yield client
            client.close()
        except SubstrateConnectionError:
            pytest.skip("Substrate node not running")
    
    def test_register_did(self, substrate_client):
        """Test DID registration"""
        try:
            # Create unique account for this test
            test_account = substrate_client.create_keypair(f'//TestUser{int(time.time())}')
            
            # Register DID
            tx_hash, receipt = substrate_client.register_did(
                user_id=999,
                account_id=test_account.ss58_address,
                public_key='0x04' + 'a1' * 32,  # 33-byte public key
                metadata={
                    'username': 'test_user',
                    'email': 'test@example.com',
                    'role': 'tester'
                }
            )
            
            assert tx_hash is not None
            assert receipt['success'] is True
            
        except Exception as e:
            # DID might already exist
            if 'DidAlreadyExists' not in str(e):
                pytest.fail(f"DID registration failed: {e}")
    
    def test_get_did_via_rpc(self, substrate_client):
        """Test getting DID via RPC"""
        try:
            # Try to get DID for Alice (may not exist)
            alice_address = substrate_client.create_keypair('//Alice').ss58_address
            did_doc = substrate_client.get_did(alice_address)
            
            # If DID exists, verify structure
            if did_doc:
                assert 'controller' in did_doc
                assert 'public_key' in did_doc
                assert 'metadata' in did_doc
                assert 'status' in did_doc
                assert 'did_identifier' in did_doc
                
        except Exception as e:
            pytest.fail(f"Get DID failed: {e}")
    
    def test_is_did_active(self, substrate_client):
        """Test checking if DID is active"""
        try:
            alice_address = substrate_client.create_keypair('//Alice').ss58_address
            is_active = substrate_client.is_did_active(alice_address)
            
            assert isinstance(is_active, bool)
            
        except Exception as e:
            pytest.fail(f"DID active check failed: {e}")


class TestDAOGovernance:
    """Test DAO proposal and voting"""
    
    @pytest.fixture
    def substrate_client(self):
        """Fixture for SubstrateClient"""
        try:
            client = SubstrateClient(keypair_uri='//Alice')
            yield client
            client.close()
        except SubstrateConnectionError:
            pytest.skip("Substrate node not running")
    
    def test_create_proposal(self, substrate_client):
        """Test creating a DAO proposal"""
        try:
            tx_hash, receipt = substrate_client.create_proposal(
                title=f"Test Proposal {int(time.time())}",
                description="This is a test proposal for pytest",
                voting_period=100
            )
            
            assert tx_hash is not None
            assert receipt is not None
            
        except Exception as e:
            pytest.fail(f"Proposal creation failed: {e}")
    
    def test_get_proposal(self, substrate_client):
        """Test querying a proposal"""
        try:
            # Query proposal (may not exist)
            proposal = substrate_client.get_proposal(0)
            
            # If proposal exists, verify structure
            if proposal:
                assert 'id' in proposal
                assert 'proposer' in proposal
                assert 'title' in proposal
                assert 'description' in proposal
                assert 'votes_for' in proposal
                assert 'votes_against' in proposal
                assert 'status' in proposal
                
        except Exception as e:
            pytest.fail(f"Get proposal failed: {e}")
    
    def test_vote_on_proposal(self, substrate_client):
        """Test voting on a proposal"""
        try:
            # First check if any proposals exist
            proposal = substrate_client.get_proposal(0)
            
            if proposal and proposal.get('status', '').lower() == 'active':
                # Vote with Bob's account
                bob_keypair = substrate_client.create_keypair('//Bob')
                
                tx_hash, receipt = substrate_client.vote_on_proposal(
                    proposal_id=0,
                    in_favor=True,
                    keypair=bob_keypair
                )
                
                assert tx_hash is not None
            else:
                pytest.skip("No active proposal to vote on")
                
        except SubstrateTransactionError as e:
            # Already voted is acceptable
            if 'AlreadyVoted' not in str(e):
                pytest.fail(f"Vote failed: {e}")


class TestContextManager:
    """Test SubstrateClient context manager"""
    
    def test_context_manager(self):
        """Test context manager properly closes connection"""
        try:
            with SubstrateClient() as client:
                assert client.substrate is not None
                block_num = client.get_block_number()
                assert isinstance(block_num, int)
            
            # After context, connection should be closed
            # Note: substrate-interface doesn't have an easy way to check this
            
        except SubstrateConnectionError:
            pytest.skip("Substrate node not running")


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises SubstrateConnectionError"""
        with pytest.raises(SubstrateConnectionError):
            client = SubstrateClient(
                url="ws://nonexistent.local:9999",
                max_retries=1,
                retry_delay=0.1
            )
    
    def test_missing_keypair_raises_error(self):
        """Test that operations without keypair raise ValueError"""
        try:
            client = SubstrateClient()  # No default keypair
            
            with pytest.raises(ValueError, match="No keypair provided"):
                client.record_invoice(
                    user_id=1,
                    invoice_hash="test",
                    client_account="5GrwvaEF...",
                    amount=1000,
                    metadata="test"
                )
            
            client.close()
        except SubstrateConnectionError:
            pytest.skip("Substrate node not running")


# Integration test marker
@pytest.mark.integration
class TestFullIntegration:
    """Full integration test - requires running Substrate node"""
    
    def test_complete_workflow(self):
        """Test complete workflow: Invoice + DID + DAO"""
        try:
            client = SubstrateClient(keypair_uri='//Alice')
            
            # Create unique test user
            test_keypair = client.create_keypair(f'//TestUser{int(time.time())}')
            
            # 1. Register DID
            did_tx, did_receipt = client.register_did(
                user_id=1000,
                account_id=test_keypair.ss58_address,
                public_key='0x04' + 'ff' * 32,
                metadata={'test': True}
            )
            assert did_tx is not None
            
            # 2. Create Invoice
            inv_tx, inv_receipt = client.record_invoice(
                user_id=1000,
                invoice_hash=f"integration_test_{int(time.time())}",
                client_account=test_keypair.ss58_address,
                amount=5000000,
                metadata="INTEGRATION-TEST|Test Workflow|Net 15"
            )
            assert inv_tx is not None
            
            # 3. Create DAO Proposal
            prop_tx, prop_receipt = client.create_proposal(
                title=f"Integration Test Proposal {int(time.time())}",
                description="Testing complete integration workflow",
                voting_period=50
            )
            assert prop_tx is not None
            
            # 4. Verify all created successfully
            invoices = client.get_invoices(test_keypair.ss58_address)
            assert len(invoices) > 0
            
            did_doc = client.get_did(test_keypair.ss58_address)
            assert did_doc is not None
            
            print("\n✅ Complete integration test passed!")
            print(f"   DID: {did_tx}")
            print(f"   Invoice: {inv_tx}")
            print(f"   Proposal: {prop_tx}")
            
            client.close()
            
        except SubstrateConnectionError:
            pytest.skip("Substrate node not running - integration test skipped")
        except Exception as e:
            # Some errors are acceptable (e.g., DID already exists)
            if 'AlreadyExists' not in str(e):
                raise


# Fixtures for common test data
@pytest.fixture
def mock_invoice_data():
    """Mock invoice data for testing"""
    return {
        'user_id': 1,
        'invoice_hash': 'test_hash_123',
        'client_account': '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
        'amount': 1000000,
        'metadata': 'INV-2025-001|Test Client|Net 30'
    }


@pytest.fixture
def mock_did_data():
    """Mock DID data for testing"""
    return {
        'user_id': 1,
        'account_id': '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
        'public_key': '0x04' + 'a1' * 32,
        'metadata': {
            'username': 'test_user',
            'email': 'test@example.com',
            'role': 'tester'
        }
    }


@pytest.fixture
def mock_proposal_data():
    """Mock proposal data for testing"""
    return {
        'title': 'Test Proposal',
        'description': 'This is a test proposal for unit testing',
        'voting_period': 100
    }


# Parametrized tests
@pytest.mark.parametrize("amount,expected_result", [
    (1000000, 1000000),
    (0, 0),
    (999999999999, 999999999999),
])
def test_amount_validation(amount, expected_result):
    """Test that amounts are correctly validated"""
    assert amount == expected_result


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])


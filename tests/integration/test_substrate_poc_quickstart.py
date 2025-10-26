"""
Integration test for Substrate POC quickstart flow.

This test validates that the quickstart script runs successfully and produces
a transaction hash output.
"""

import os
import re
import subprocess
import time
from pathlib import Path

import pytest


class TestSubstratePOCQuickstart:
    """Test class for Substrate POC quickstart integration."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Setup: Ensure we're in the project root
        self.project_root = Path(__file__).parent.parent.parent
        self.original_cwd = os.getcwd()
        os.chdir(self.project_root)
        
        yield
        
        # Teardown: Clean up Docker services and restore working directory
        self._cleanup_docker_services()
        os.chdir(self.original_cwd)

    def _cleanup_docker_services(self):
        """Clean up Docker services started by quickstart."""
        try:
            # Stop any running quickstart services
            subprocess.run(
                [
                    "docker-compose",
                    "-f", "scripts/docker-compose.quickstart.yml",
                    "down"
                ],
                capture_output=True,
                timeout=30
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Ignore errors during cleanup
            pass

    def _check_docker_available(self):
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _extract_transaction_hash(self, output: str) -> str:
        """Extract transaction hash from quickstart output."""
        # Look for extrinsic hash pattern (0x followed by 64 hex characters)
        hash_pattern = r'0x[0-9a-fA-F]{64}'
        matches = re.findall(hash_pattern, output)
        
        if matches:
            return matches[0]
        
        # Look for Substrate block/tx link patterns
        link_patterns = [
            r'https://polkadot\.js\.org/apps/#/explorer/query/[0-9a-fA-F]+',
            r'Extrinsic hash: (0x[0-9a-fA-F]+)',
            r'Transaction hash: (0x[0-9a-fA-F]+)',
        ]
        
        for pattern in link_patterns:
            matches = re.findall(pattern, output)
            if matches:
                return matches[0] if isinstance(matches[0], str) else matches[0]
        
        return None

    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.path.exists("scripts/quickstart.sh"),
        reason="Quickstart script not found"
    )
    def test_quickstart_produces_transaction_hash(self):
        """Test that quickstart script produces a valid transaction hash."""
        # Skip if Docker is not available
        if not self._check_docker_available():
            pytest.skip("Docker is not available or not running")
        
        # Run quickstart script in headless mode
        quickstart_script = self.project_root / "scripts" / "quickstart.sh"
        
        try:
            # Execute quickstart script with timeout
            result = subprocess.run(
                ["bash", str(quickstart_script), "--headless"],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
                cwd=self.project_root
            )
            
            # Check if script ran successfully
            assert result.returncode == 0, f"Quickstart failed with return code {result.returncode}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            
            # Combine stdout and stderr for analysis
            full_output = result.stdout + result.stderr
            
            # Extract transaction hash
            tx_hash = self._extract_transaction_hash(full_output)
            
            # Assert that we found a transaction hash
            assert tx_hash is not None, f"No transaction hash found in output:\n{full_output}"
            
            # Validate hash format
            assert re.match(r'^0x[0-9a-fA-F]{64}$', tx_hash), f"Invalid transaction hash format: {tx_hash}"
            
            # Additional validation: check for success indicators
            success_indicators = [
                "Transaction submitted successfully",
                "SUCCESS",
                "Contract deployed successfully",
                "Demo completed successfully"
            ]
            
            has_success_indicator = any(indicator in full_output for indicator in success_indicators)
            assert has_success_indicator, f"No success indicators found in output:\n{full_output}"
            
            print(f"\n✅ Quickstart test passed!")
            print(f"📝 Transaction hash: {tx_hash}")
            print(f"📊 Output length: {len(full_output)} characters")
            
        except subprocess.TimeoutExpired:
            pytest.fail("Quickstart script timed out after 10 minutes")
        except Exception as e:
            pytest.fail(f"Unexpected error running quickstart: {e}")

    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.path.exists("scripts/quickstart.sh"),
        reason="Quickstart script not found"
    )
    def test_quickstart_with_retries(self):
        """Test quickstart with retry logic for robustness."""
        # Skip if Docker is not available
        if not self._check_docker_available():
            pytest.skip("Docker is not available or not running")
        
        max_retries = 3
        retry_delay = 30  # seconds
        
        for attempt in range(max_retries):
            try:
                # Clean up any existing services before retry
                self._cleanup_docker_services()
                time.sleep(5)  # Wait for cleanup
                
                # Run quickstart script
                quickstart_script = self.project_root / "scripts" / "quickstart.sh"
                
                result = subprocess.run(
                    ["bash", str(quickstart_script), "--headless"],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    # Success - extract and validate transaction hash
                    full_output = result.stdout + result.stderr
                    tx_hash = self._extract_transaction_hash(full_output)
                    
                    if tx_hash and re.match(r'^0x[0-9a-fA-F]{64}$', tx_hash):
                        print(f"\n✅ Quickstart test passed on attempt {attempt + 1}!")
                        print(f"📝 Transaction hash: {tx_hash}")
                        return  # Success, exit retry loop
                
                # If we get here, the attempt failed
                print(f"\n⚠️  Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                
            except subprocess.TimeoutExpired:
                print(f"\n⏰ Attempt {attempt + 1} timed out")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except Exception as e:
                print(f"\n❌ Attempt {attempt + 1} failed with error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        # If we get here, all retries failed
        pytest.fail(f"Quickstart failed after {max_retries} attempts")

    def test_quickstart_script_exists_and_executable(self):
        """Test that quickstart script exists and is executable."""
        quickstart_script = self.project_root / "scripts" / "quickstart.sh"
        
        assert quickstart_script.exists(), "Quickstart script not found"
        assert quickstart_script.is_file(), "Quickstart script is not a file"
        
        # Check if script is executable
        assert os.access(quickstart_script, os.X_OK), "Quickstart script is not executable"

    def test_docker_compose_file_exists(self):
        """Test that Docker Compose file exists and is valid."""
        docker_compose_file = self.project_root / "scripts" / "docker-compose.quickstart.yml"
        
        assert docker_compose_file.exists(), "Docker Compose file not found"
        assert docker_compose_file.is_file(), "Docker Compose file is not a file"
        
        # Validate Docker Compose file syntax
        try:
            result = subprocess.run(
                ["docker-compose", "-f", str(docker_compose_file), "config"],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, f"Docker Compose file is invalid: {result.stderr}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Docker Compose not available for validation")

    def test_contract_directory_exists(self):
        """Test that contract directory exists."""
        contract_dir = self.project_root / "contracts" / "substrate-poc"
        
        assert contract_dir.exists(), "Contract directory not found"
        assert contract_dir.is_dir(), "Contract directory is not a directory"
        
        # Check for required contract files
        required_files = ["Cargo.toml", "lib.rs"]
        for file_name in required_files:
            file_path = contract_dir / file_name
            assert file_path.exists(), f"Required contract file {file_name} not found"

    def test_backend_management_command_exists(self):
        """Test that Django management command exists."""
        management_command = (
            self.project_root / "apps" / "backend" / "backend" / 
            "management" / "commands" / "demo_submit.py"
        )
        
        assert management_command.exists(), "Django management command not found"
        assert management_command.is_file(), "Management command is not a file"

"""
IPFS Service

Service for storing and retrieving audit trail data from IPFS (InterPlanetary File System).
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class IPFSService:
    """
    Service for IPFS integration and decentralized storage of audit data.
    """
    
    def __init__(self, ipfs_url: str = None):
        """
        Initialize IPFS service.
        
        Args:
            ipfs_url: IPFS node URL
        """
        self.ipfs_url = ipfs_url or getattr(settings, 'IPFS_URL', 'http://localhost:5001')
        self.gateway_url = getattr(settings, 'IPFS_GATEWAY_URL', 'https://ipfs.io/ipfs/')
        self.timeout = getattr(settings, 'IPFS_TIMEOUT', 30)
    
    def store_audit_log(self, audit_data: Dict[str, Any]) -> Optional[str]:
        """
        Store audit log data in IPFS and return hash.
        
        Args:
            audit_data: Dictionary containing audit data
            
        Returns:
            IPFS hash if successful, None otherwise
        """
        try:
            # Add metadata to audit data
            enriched_data = {
                'data': audit_data,
                'metadata': {
                    'stored_at': timezone.now().isoformat(),
                    'version': '1.0',
                    'type': 'audit_log'
                }
            }
            
            # Convert to JSON
            json_data = json.dumps(enriched_data, indent=2)
            
            # Store in IPFS
            files = {'file': ('audit_log.json', json_data, 'application/json')}
            response = requests.post(
                f"{self.ipfs_url}/api/v0/add",
                files=files,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result['Hash']
                
                # Pin the file to prevent garbage collection
                self.pin_file(ipfs_hash)
                
                logger.info(f"Stored audit log in IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                logger.error(f"Failed to store in IPFS: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"IPFS storage error: {e}")
            return None
    
    def retrieve_audit_log(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve audit log data from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the data
            
        Returns:
            Dictionary containing audit data or None
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/cat",
                params={'arg': ipfs_hash},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = json.loads(response.text)
                logger.info(f"Retrieved audit log from IPFS: {ipfs_hash}")
                return data
            else:
                logger.error(f"Failed to retrieve from IPFS: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"IPFS retrieval error: {e}")
            return None
    
    def pin_file(self, ipfs_hash: str) -> bool:
        """
        Pin file in IPFS to prevent garbage collection.
        
        Args:
            ipfs_hash: IPFS hash of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/pin/add",
                params={'arg': ipfs_hash},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Pinned file in IPFS: {ipfs_hash}")
                return True
            else:
                logger.error(f"Failed to pin file: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"IPFS pin error: {e}")
            return False
    
    def unpin_file(self, ipfs_hash: str) -> bool:
        """
        Unpin file from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/pin/rm",
                params={'arg': ipfs_hash},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Unpinned file from IPFS: {ipfs_hash}")
                return True
            else:
                logger.error(f"Failed to unpin file: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"IPFS unpin error: {e}")
            return False
    
    def get_file_info(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a file in IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the file
            
        Returns:
            Dictionary containing file information or None
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/object/stat",
                params={'arg': ipfs_hash},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get file info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"IPFS file info error: {e}")
            return None
    
    def list_pinned_files(self) -> List[Dict[str, Any]]:
        """
        List all pinned files in IPFS.
        
        Returns:
            List of dictionaries containing pinned file information
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/pin/ls",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return list(result.get('Keys', {}).values())
            else:
                logger.error(f"Failed to list pinned files: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"IPFS list pinned files error: {e}")
            return []
    
    def get_ipfs_url(self, ipfs_hash: str) -> str:
        """
        Get IPFS URL for accessing a file.
        
        Args:
            ipfs_hash: IPFS hash of the file
            
        Returns:
            IPFS URL
        """
        return f"{self.gateway_url}{ipfs_hash}"
    
    def store_merkle_tree(self, merkle_tree_data: Dict[str, Any]) -> Optional[str]:
        """
        Store Merkle tree data in IPFS.
        
        Args:
            merkle_tree_data: Dictionary containing Merkle tree data
            
        Returns:
            IPFS hash if successful, None otherwise
        """
        try:
            # Add metadata
            enriched_data = {
                'data': merkle_tree_data,
                'metadata': {
                    'stored_at': timezone.now().isoformat(),
                    'version': '1.0',
                    'type': 'merkle_tree'
                }
            }
            
            # Convert to JSON
            json_data = json.dumps(enriched_data, indent=2)
            
            # Store in IPFS
            files = {'file': ('merkle_tree.json', json_data, 'application/json')}
            response = requests.post(
                f"{self.ipfs_url}/api/v0/add",
                files=files,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result['Hash']
                
                # Pin the file
                self.pin_file(ipfs_hash)
                
                logger.info(f"Stored Merkle tree in IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                logger.error(f"Failed to store Merkle tree in IPFS: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"IPFS Merkle tree storage error: {e}")
            return None
    
    def retrieve_merkle_tree(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve Merkle tree data from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the Merkle tree data
            
        Returns:
            Dictionary containing Merkle tree data or None
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/cat",
                params={'arg': ipfs_hash},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = json.loads(response.text)
                logger.info(f"Retrieved Merkle tree from IPFS: {ipfs_hash}")
                return data
            else:
                logger.error(f"Failed to retrieve Merkle tree from IPFS: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"IPFS Merkle tree retrieval error: {e}")
            return None
    
    def store_batch_audit_logs(self, audit_logs: List[Dict[str, Any]]) -> Optional[str]:
        """
        Store a batch of audit logs in IPFS.
        
        Args:
            audit_logs: List of audit log dictionaries
            
        Returns:
            IPFS hash if successful, None otherwise
        """
        try:
            # Create batch data
            batch_data = {
                'logs': audit_logs,
                'batch_info': {
                    'count': len(audit_logs),
                    'stored_at': timezone.now().isoformat(),
                    'version': '1.0',
                    'type': 'batch_audit_logs'
                }
            }
            
            # Convert to JSON
            json_data = json.dumps(batch_data, indent=2)
            
            # Store in IPFS
            files = {'file': ('batch_audit_logs.json', json_data, 'application/json')}
            response = requests.post(
                f"{self.ipfs_url}/api/v0/add",
                files=files,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result['Hash']
                
                # Pin the file
                self.pin_file(ipfs_hash)
                
                logger.info(f"Stored batch audit logs in IPFS: {ipfs_hash}")
                return ipfs_hash
            else:
                logger.error(f"Failed to store batch audit logs in IPFS: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"IPFS batch audit logs storage error: {e}")
            return None
    
    def retrieve_batch_audit_logs(self, ipfs_hash: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve a batch of audit logs from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the batch data
            
        Returns:
            List of audit log dictionaries or None
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/cat",
                params={'arg': ipfs_hash},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = json.loads(response.text)
                logs = data.get('logs', [])
                logger.info(f"Retrieved batch audit logs from IPFS: {ipfs_hash}")
                return logs
            else:
                logger.error(f"Failed to retrieve batch audit logs from IPFS: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"IPFS batch audit logs retrieval error: {e}")
            return None
    
    def verify_file_exists(self, ipfs_hash: str) -> bool:
        """
        Verify that a file exists in IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the file
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/object/stat",
                params={'arg': ipfs_hash},
                timeout=self.timeout
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"IPFS file verification error: {e}")
            return False
    
    def get_node_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the IPFS node.
        
        Returns:
            Dictionary containing node information or None
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/id",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get IPFS node info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"IPFS node info error: {e}")
            return None
    
    def get_node_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get statistics about the IPFS node.
        
        Returns:
            Dictionary containing node statistics or None
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/stats/repo",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get IPFS node stats: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"IPFS node stats error: {e}")
            return None
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Clean up old files from IPFS (unpin them).
        
        Args:
            days: Number of days to keep files
            
        Returns:
            Number of files cleaned up
        """
        try:
            pinned_files = self.list_pinned_files()
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            cleaned_count = 0
            
            for file_info in pinned_files:
                # This is a simplified implementation
                # In production, you would check file timestamps
                # and unpin old files
                pass
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"IPFS cleanup error: {e}")
            return 0

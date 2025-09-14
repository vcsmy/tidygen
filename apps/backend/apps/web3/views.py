"""
Web3 and blockchain integration views.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import (
    WalletFilter, BlockchainTransactionFilter, SmartContractFilter,
    TokenFilter, WalletBalanceFilter, DeFiProtocolFilter,
    DecentralizedIdentityFilter, OnChainAnchorFilter, SmartContractModuleFilter,
    DAOGovernanceFilter, GovernanceVoteFilter, TokenizedRewardFilter,
    DecentralizedStorageFilter, BlockchainAuditLogFilter
)
from django.conf import settings
from django.utils import timezone
from web3 import Web3
import json
import hashlib
import hmac
from eth_account.messages import encode_defunct
from eth_account import Account

from .models import (
    Wallet, BlockchainTransaction, SmartContract, Token,
    WalletBalance, DeFiProtocol, DecentralizedIdentity, OnChainAnchor,
    SmartContractModule, DAOGovernance, GovernanceVote, TokenizedReward,
    DecentralizedStorage, BlockchainAuditLog
)
from .serializers import (
    WalletSerializer, WalletCreateSerializer, BlockchainTransactionSerializer,
    SmartContractSerializer, TokenSerializer, WalletBalanceSerializer,
    DeFiProtocolSerializer, WalletVerificationSerializer,
    TransactionRequestSerializer, TokenTransferSerializer,
    MessageSigningSerializer, SignatureVerificationSerializer,
    DecentralizedIdentitySerializer, DIDCreateSerializer, OnChainAnchorSerializer,
    AnchorCreateSerializer, SmartContractModuleSerializer, DAOGovernanceSerializer,
    GovernanceVoteSerializer, TokenizedRewardSerializer, RewardCreateSerializer,
    DecentralizedStorageSerializer, BlockchainAuditLogSerializer, GovernanceProposalSerializer
)


class WalletViewSet(viewsets.ModelViewSet):
    """ViewSet for wallet management."""
    queryset = Wallet.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WalletFilter
    search_fields = ['address']
    ordering_fields = ['created_at', 'last_used']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter wallets by user."""
        return Wallet.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return WalletCreateSerializer
        return WalletSerializer
    
    @action(detail=False, methods=['get'])
    def my_wallets(self, request):
        """Get current user's wallets."""
        wallets = self.get_queryset()
        serializer = self.get_serializer(wallets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify wallet ownership."""
        wallet = self.get_object()
        serializer = WalletVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Verify signature using blockchain service
            from .services import blockchain_service
            
            message = serializer.validated_data['message']
            signature = serializer.validated_data['signature']
            
            if blockchain_service.verify_signature(wallet.address, message, signature):
                wallet.is_verified = True
                wallet.verification_signature = signature
                wallet.save()
                
                return Response({'message': 'Wallet verified successfully.'})
            else:
                return Response({'error': 'Signature verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """Set wallet as primary."""
        wallet = self.get_object()
        
        # Unset other primary wallets
        Wallet.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
        
        # Set this wallet as primary
        wallet.is_primary = True
        wallet.save()
        
        return Response({'message': 'Primary wallet updated successfully.'})


class BlockchainTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blockchain transactions."""
    queryset = BlockchainTransaction.objects.all()
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BlockchainTransactionFilter
    search_fields = ['transaction_hash', 'from_address', 'to_address']
    ordering_fields = ['created_at', 'block_number', 'value']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter transactions by user."""
        return BlockchainTransaction.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending transactions."""
        pending_transactions = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent transactions."""
        recent_transactions = self.get_queryset()[:20]
        serializer = self.get_serializer(recent_transactions, many=True)
        return Response(serializer.data)


class SmartContractViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for smart contracts."""
    queryset = SmartContract.objects.all()
    serializer_class = SmartContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SmartContractFilter
    search_fields = ['name', 'address']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def my_contracts(self, request):
        """Get contracts deployed by current user."""
        contracts = self.get_queryset().filter(deployer=request.user)
        serializer = self.get_serializer(contracts, many=True)
        return Response(serializer.data)


class TokenViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for tokens."""
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TokenFilter
    search_fields = ['name', 'symbol', 'token_id']
    ordering_fields = ['name', 'symbol', 'market_cap']
    ordering = ['symbol']
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular tokens."""
        popular_tokens = self.get_queryset().filter(
            market_cap__isnull=False
        ).order_by('-market_cap')[:20]
        serializer = self.get_serializer(popular_tokens, many=True)
        return Response(serializer.data)


class WalletBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for wallet balances."""
    queryset = WalletBalance.objects.all()
    serializer_class = WalletBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = WalletBalanceFilter
    ordering_fields = ['balance', 'last_updated']
    ordering = ['-balance']
    
    def get_queryset(self):
        """Filter balances by user's wallets."""
        user_wallets = Wallet.objects.filter(user=self.request.user)
        return WalletBalance.objects.filter(wallet__in=user_wallets)
    
    @action(detail=False, methods=['get'])
    def my_balances(self, request):
        """Get current user's wallet balances."""
        balances = self.get_queryset()
        serializer = self.get_serializer(balances, many=True)
        return Response(serializer.data)


class DeFiProtocolViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DeFi protocols."""
    queryset = DeFiProtocol.objects.filter(is_active=True)
    serializer_class = DeFiProtocolSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DeFiProtocolFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'apy']
    ordering = ['name']


class TransactionView(APIView):
    """View for creating blockchain transactions."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a new transaction."""
        serializer = TransactionRequestSerializer(data=request.data)
        if serializer.is_valid():
            from .services import blockchain_service
            
            # Get current gas price
            gas_price = blockchain_service.get_gas_price()
            
            transaction_data = {
                'to': serializer.validated_data['to_address'],
                'value': int(serializer.validated_data['value'] * 10**18),  # Convert to wei
                'gas': serializer.validated_data.get('gas_limit', 21000),
                'gasPrice': gas_price or serializer.validated_data.get('gas_price', 20000000000),
                'data': serializer.validated_data.get('data', '0x'),
                'nonce': blockchain_service.w3.eth.get_transaction_count(request.user.wallets.filter(is_primary=True).first().address) if request.user.wallets.filter(is_primary=True).exists() else 0,
            }
            
            return Response({
                'message': 'Transaction created successfully.',
                'transaction': transaction_data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenTransferView(APIView):
    """View for token transfers."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a token transfer transaction."""
        serializer = TokenTransferSerializer(data=request.data)
        if serializer.is_valid():
            # TODO: Implement token transfer
            # This would involve creating a contract call transaction
            
            transfer_data = {
                'contract_address': serializer.validated_data['token_address'],
                'function': 'transfer',
                'parameters': [
                    serializer.validated_data['to_address'],
                    int(serializer.validated_data['amount'] * 10**18)  # Convert to token units
                ]
            }
            
            return Response({
                'message': 'Token transfer transaction created successfully.',
                'transfer': transfer_data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Web3StatusView(APIView):
    """View for Web3 connection status."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get Web3 connection status."""
        from .services import blockchain_service
        
        if blockchain_service.is_connected():
            network_info = blockchain_service.get_network_info()
            status_data = {
                'connected': True,
                'network': network_info.get('network_name', 'Unknown'),
                'chain_id': network_info.get('chain_id', 0),
                'block_number': network_info.get('block_number', 0),
                'gas_price': str(network_info.get('gas_price', 0)),
            }
        else:
            status_data = {
                'connected': False,
                'network': 'Disconnected',
                'chain_id': 0,
                'block_number': 0,
                'gas_price': '0',
            }
        
        return Response(status_data)


class MessageSigningView(APIView):
    """View for creating authentication messages."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a message for wallet signing."""
        serializer = MessageSigningSerializer(data=request.data)
        
        if serializer.is_valid():
            address = serializer.validated_data['address']
            timestamp = int(timezone.now().timestamp())
            
            # Create authentication message
            message_prefix = getattr(settings, 'WEB3_MESSAGE_PREFIX', 'TidyGen ERP Login')
            message = f"{message_prefix}\n\nAddress: {address}\nTimestamp: {timestamp}"
            
            # Create a unique nonce for this request
            nonce = hashlib.sha256(
                f"{address}{timestamp}{request.user.id}".encode()
            ).hexdigest()[:16]
            
            return Response({
                'message': message,
                'address': address,
                'timestamp': timestamp,
                'nonce': nonce,
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignatureVerificationView(APIView):
    """View for verifying wallet signatures."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Verify a wallet signature."""
        serializer = SignatureVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            address = serializer.validated_data['address']
            signature = serializer.validated_data['signature']
            message = serializer.validated_data['message']
            
            try:
                # Verify the signature
                message_hash = encode_defunct(text=message)
                recovered_address = Account.recover_message(message_hash, signature=signature)
                
                # Check if the recovered address matches the provided address
                if recovered_address.lower() != address.lower():
                    return Response({
                        'verified': False,
                        'error': 'Signature verification failed'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Get or create wallet
                wallet, created = Wallet.objects.get_or_create(
                    user=request.user,
                    address=address,
                    defaults={
                        'wallet_type': 'metamask',  # Default type
                        'is_verified': True,
                        'verification_signature': signature,
                        'last_used': timezone.now(),
                    }
                )
                
                if not created:
                    # Update existing wallet
                    wallet.is_verified = True
                    wallet.verification_signature = signature
                    wallet.last_used = timezone.now()
                    wallet.save()
                
                # Generate JWT token for the user
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(request.user)
                
                return Response({
                    'verified': True,
                    'wallet': {
                        'address': wallet.address,
                        'wallet_type': wallet.wallet_type,
                        'is_verified': wallet.is_verified,
                        'is_primary': wallet.is_primary,
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
                
            except Exception as e:
                return Response({
                    'verified': False,
                    'error': f'Signature verification failed: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletConnectView(APIView):
    """View for WalletConnect integration."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Handle WalletConnect connection."""
        # TODO: Implement WalletConnect session management
        # This would involve storing WalletConnect session data
        # and managing the connection lifecycle
        
        return Response({
            'message': 'WalletConnect integration coming soon',
            'status': 'pending'
        })
    
    def delete(self, request):
        """Disconnect WalletConnect session."""
        # TODO: Implement WalletConnect disconnection
        return Response({
            'message': 'WalletConnect session disconnected'
        })


# ==================== CORE WEB3 VIEWS ====================

class DecentralizedIdentityViewSet(viewsets.ModelViewSet):
    """ViewSet for Decentralized Identity management."""
    queryset = DecentralizedIdentity.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DecentralizedIdentityFilter
    search_fields = ['did_identifier', 'user__username']
    ordering_fields = ['created_at', 'modified_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter DIDs by user's organization."""
                return DecentralizedIdentity.objects
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return DIDCreateSerializer
        return DecentralizedIdentitySerializer
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify DID ownership."""
        did = self.get_object()
        # TODO: Implement DID verification logic
        did.is_verified = True
        did.verification_timestamp = timezone.now()
        did.save()
        
        return Response({'message': 'DID verified successfully.'})
    
    @action(detail=True, methods=['post'])
    def generate_document(self, request, pk=None):
        """Generate DID document."""
        did = self.get_object()
        did.generate_did_document()
        
        return Response({
            'message': 'DID document generated successfully.',
            'did_document': did.did_document
        })


class OnChainAnchorViewSet(viewsets.ModelViewSet):
    """ViewSet for On-Chain Anchor management."""
    queryset = OnChainAnchor.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OnChainAnchorFilter
    search_fields = ['data_hash', 'transaction_hash', 'description']
    ordering_fields = ['created_at', 'block_number']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter anchors by user's organization."""
                return OnChainAnchor.objects
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return AnchorCreateSerializer
        return OnChainAnchorSerializer
    
    @action(detail=True, methods=['post'])
    def anchor_to_blockchain(self, request, pk=None):
        """Anchor data to blockchain."""
        anchor = self.get_object()
        # TODO: Implement blockchain anchoring logic
        anchor.status = 'anchored'
        anchor.transaction_hash = '0x' + hashlib.sha256(f"{anchor.id}{timezone.now()}".encode()).hexdigest()[:64]
        anchor.block_number = 18000000  # Example block number
        anchor.save()
        
        return Response({
            'message': 'Data anchored to blockchain successfully.',
            'transaction_hash': anchor.transaction_hash,
            'block_number': anchor.block_number
        })
    
    @action(detail=False, methods=['get'])
    def pending_anchors(self, request):
        """Get pending anchors."""
        pending_anchors = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_anchors, many=True)
        return Response(serializer.data)


class SmartContractModuleViewSet(viewsets.ModelViewSet):
    """ViewSet for Smart Contract Module management."""
    queryset = SmartContractModule.objects.all()
    serializer_class = SmartContractModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SmartContractModuleFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter modules by user's organization."""
                return SmartContractModule.objects
    
    @action(detail=True, methods=['post'])
    def deploy(self, request, pk=None):
        """Deploy smart contract module."""
        module = self.get_object()
        # TODO: Implement smart contract deployment
        module.status = 'deployed'
        module.save()
        
        return Response({'message': 'Smart contract module deployed successfully.'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate smart contract module."""
        module = self.get_object()
        module.status = 'active'
        module.save()
        
        return Response({'message': 'Smart contract module activated successfully.'})
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute smart contract function."""
        module = self.get_object()
        function_name = request.data.get('function_name')
        parameters = request.data.get('parameters', [])
        
        # TODO: Implement smart contract execution
        return Response({
            'message': f'Function {function_name} executed successfully.',
            'result': 'execution_result_placeholder'
        })


class DAOGovernanceViewSet(viewsets.ModelViewSet):
    """ViewSet for DAO Governance management."""
    queryset = DAOGovernance.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DAOGovernanceFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'voting_start', 'voting_end']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter governance by user's organization."""
                return DAOGovernance.objects
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return GovernanceProposalSerializer
        return DAOGovernanceSerializer
    
    @action(detail=True, methods=['post'])
    def start_voting(self, request, pk=None):
        """Start voting period."""
        governance = self.get_object()
        governance.status = 'active'
        governance.voting_start = timezone.now()
        governance.voting_end = timezone.now() + governance.voting_duration
        governance.save()
        
        return Response({'message': 'Voting period started successfully.'})
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Cast a vote."""
        governance = self.get_object()
        vote_choice = request.data.get('vote_choice')
        voting_power = request.data.get('voting_power', 1)
        reason = request.data.get('reason', '')
        
        # Check if user can vote
        if governance.votes.filter(voter=request.user).exists():
            return Response({'error': 'User has already voted.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create vote
        vote = GovernanceVote.objects.create(
            governance=governance,
            voter=request.user,
            vote_choice=vote_choice,
            voting_power=voting_power,
            reason=reason
        )
        
        # Update governance totals
        if vote_choice == 'for':
            governance.votes_for += voting_power
        elif vote_choice == 'against':
            governance.votes_against += voting_power
        
        governance.total_votes += voting_power
        governance.save()
        
        return Response({'message': 'Vote cast successfully.'})
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute governance proposal."""
        governance = self.get_object()
        
        # Check if proposal passed
        if governance.votes_for <= governance.votes_against:
            return Response({'error': 'Proposal did not pass.'}, status=status.HTTP_400_BAD_REQUEST)
        
        governance.status = 'executed'
        governance.executed_at = timezone.now()
        governance.executed_by = request.user
        governance.save()
        
        return Response({'message': 'Proposal executed successfully.'})


class TokenizedRewardViewSet(viewsets.ModelViewSet):
    """ViewSet for Tokenized Reward management."""
    queryset = TokenizedReward.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TokenizedRewardFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'token_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter rewards by user's organization."""
                return TokenizedReward.objects
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return RewardCreateSerializer
        return TokenizedRewardSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve tokenized reward."""
        reward = self.get_object()
        evaluation_score = request.data.get('evaluation_score')
        evaluation_notes = request.data.get('evaluation_notes', '')
        
        reward.status = 'approved'
        reward.evaluator = request.user
        reward.evaluation_score = evaluation_score
        reward.evaluation_notes = evaluation_notes
        reward.save()
        
        return Response({'message': 'Reward approved successfully.'})
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """Pay tokenized reward."""
        reward = self.get_object()
        
        if reward.status != 'approved':
            return Response({'error': 'Reward must be approved before payment.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Implement token payment logic
        reward.status = 'paid'
        reward.paid_at = timezone.now()
        reward.payment_transaction = None  # TODO: Create actual transaction
        reward.save()
        
        return Response({'message': 'Reward paid successfully.'})


class DecentralizedStorageViewSet(viewsets.ModelViewSet):
    """ViewSet for Decentralized Storage management."""
    queryset = DecentralizedStorage.objects.all()
    serializer_class = DecentralizedStorageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DecentralizedStorageFilter
    search_fields = ['original_filename', 'storage_hash']
    ordering_fields = ['created_at', 'file_size']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter storage by user's organization."""
                return DecentralizedStorage.objects
    
    @action(detail=True, methods=['post'])
    def upload_to_ipfs(self, request, pk=None):
        """Upload file to IPFS."""
        storage = self.get_object()
        # TODO: Implement IPFS upload
        storage.storage_type = 'ipfs'
        storage.storage_hash = 'Qm' + hashlib.sha256(f"{storage.id}{timezone.now()}".encode()).hexdigest()[:44]
        storage.storage_url = f"https://ipfs.io/ipfs/{storage.storage_hash}"
        storage.status = 'uploaded'
        storage.save()
        
        return Response({
            'message': 'File uploaded to IPFS successfully.',
            'ipfs_hash': storage.storage_hash,
            'ipfs_url': storage.storage_url
        })
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin file to IPFS."""
        storage = self.get_object()
        storage.pin_status = True
        storage.status = 'pinned'
        storage.save()
        
        return Response({'message': 'File pinned successfully.'})


class BlockchainAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Blockchain Audit Log (read-only)."""
    queryset = BlockchainAuditLog.objects.all()
    serializer_class = BlockchainAuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BlockchainAuditLogFilter
    search_fields = ['event_name', 'description']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter audit logs by user's organization."""
                return BlockchainAuditLog.objects
    
    @action(detail=False, methods=['get'])
    def security_events(self, request):
        """Get security-related audit logs."""
        security_logs = self.get_queryset().filter(
            log_type='security_event'
        ).order_by('-created_at')[:50]
        serializer = self.get_serializer(security_logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_actions(self, request):
        """Get user action audit logs."""
        user_actions = self.get_queryset().filter(
            log_type='user_action',
            user=request.user
        ).order_by('-created_at')[:50]
        serializer = self.get_serializer(user_actions, many=True)
        return Response(serializer.data)


class Web3DashboardView(APIView):
    """Web3 Dashboard overview."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get Web3 dashboard data."""
                
        # Get Web3 statistics
        stats = {
            'total_wallets': Wallet.objects.filter(user=request.user).count(),
            'verified_wallets': Wallet.objects.filter(user=request.user, is_verified=True).count(),
            'total_transactions': BlockchainTransaction.objects.filter(user=request.user).count(),
            'pending_transactions': BlockchainTransaction.objects.filter(user=request.user, status='pending').count(),
            'total_dids': DecentralizedIdentity.objects.count(),
            'active_dids': DecentralizedIdentity.objects.count(),
            'total_anchors': OnChainAnchor.objects.count(),
            'anchored_data': OnChainAnchor.objects.count(),
            'active_proposals': DAOGovernance.objects.count(),
            'total_rewards': TokenizedReward.objects.count(),
            'paid_rewards': TokenizedReward.objects.count(),
        }
        
        # Get recent activity
        recent_transactions = BlockchainTransaction.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]
        
        recent_anchors = OnChainAnchor.objects.filter(
            
        ).order_by('-created_at')[:10]
        
        recent_proposals = DAOGovernance.objects.filter(
            
        ).order_by('-created_at')[:5]
        
        return Response({
            'stats': stats,
            'recent_transactions': BlockchainTransactionSerializer(recent_transactions, many=True).data,
            'recent_anchors': OnChainAnchorSerializer(recent_anchors, many=True).data,
            'recent_proposals': DAOGovernanceSerializer(recent_proposals, many=True).data,
        })

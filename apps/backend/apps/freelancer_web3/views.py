"""
Views for freelancer_web3 app API.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from apps.core.permissions import IsOwnerOrReadOnly
from drf_spectacular.utils import extend_schema
from .models import (
    FreelancerNFTBadge, FreelancerNFTInstance, FreelancerSmartContract,
    FreelancerReputationToken, FreelancerWalletConnection, FreelancerWeb3Transaction
)
from .serializers import (
    FreelancerNFTBadgeSerializer, FreelancerNFTInstanceSerializer,
    FreelancerSmartContractSerializer, FreelancerReputationTokenSerializer,
    FreelancerWalletConnectionSerializer, FreelancerWeb3TransactionSerializer
)

User = get_user_model()


@extend_schema(tags=['Freelancer Web3'])
class FreelancerNFTBadgeListView(generics.ListAPIView):
    """
    List all available NFT badges.
    """
    queryset = FreelancerNFTBadge.objects.filter(is_active=True)
    serializer_class = FreelancerNFTBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=['Freelancer Web3'])
class FreelancerNFTInstanceView(generics.ListCreateAPIView):
    """
    List and create NFT badge instances for freelancers.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            freelancer = self.request.user.freelancer_profile
            return FreelancerNFTInstance.objects.filter(freelancer=freelancer).select_related(
                'freelancer', 'badge'
            )
        except:
            return FreelancerNFTInstance.objects.none()
    
    serializer_class = FreelancerNFTInstanceSerializer


@extend_schema(tags=['Freelancer Web3'])
class FreelancerSmartContractView(generics.ListCreateAPIView):
    """
    List and create smart contracts for freelancers.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            freelancer = self.request.user.freelancer_profile
            return FreelancerSmartContract.objects.filter(freelancer=freelancer).select_related(
                'freelancer', 'job'
            )
        except:
            return FreelancerSmartContract.objects.none()
    
    serializer_class = FreelancerSmartContractSerializer


@extend_schema(tags=['Freelancer Web3'])
class FreelancerReputationTokenView(generics.ListAPIView):
    """
    List reputation tokens for freelancers.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            freelancer = self.request.user.freelancer_profile
            return FreelancerReputationToken.objects.filter(freelancer=freelancer).select_related(
                'freelancer'
            )
        except:
            return FreelancerReputationToken.objects.none()
    
    serializer_class = FreelancerReputationTokenSerializer


@extend_schema(tags=['Freelancer Web3'])
class FreelancerWalletConnectionView(generics.ListCreateAPIView):
    """
    List and manage wallet connections for freelancers.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            freelancer = self.request.user.freelancer_profile
            return FreelancerWalletConnection.objects.filter(
                freelancer=freelancer, user=self.request.user
            ).select_related('freelancer', 'user')
        except:
            return FreelancerWalletConnection.objects.none()
    
    serializer_class = FreelancerWalletConnectionSerializer


@extend_schema(tags=['Freelancer Web3'])
class FreelancerWeb3TransactionView(generics.ListAPIView):
    """
    List Web3 transactions for freelancers.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            freelancer = self.request.user.freelancer_profile
            return FreelancerWeb3Transaction.objects.filter(freelancer=freelancer).select_related(
                'freelancer', 'related_nft', 'related_contract', 'related_reputation_token'
            )
        except:
            return FreelancerWeb3Transaction.objects.none()
    
    serializer_class = FreelancerWeb3TransactionSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_wallet(request):
    """
    Connect a Web3 wallet to freelancer profile.
    """
    try:
        freelancer = request.user.freelancer_profile
    except:
        return Response(
            {'error': 'Freelancer profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    wallet_address = request.data.get('wallet_address')
    wallet_type = request.data.get('wallet_type', 'metamask')
    signature = request.data.get('signature', '')
    
    if not wallet_address:
        return Response(
            {'error': 'Wallet address is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if wallet is already connected
    existing_connection = FreelancerWalletConnection.objects.filter(
        freelancer=freelancer,
        wallet_address=wallet_address,
        wallet_type=wallet_type,
        connection_status='connected'
    ).first()
    
    if existing_connection:
        return Response(
            {'error': 'This wallet is already connected.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create new wallet connection
    connection = FreelancerWalletConnection.objects.create(
        freelancer=freelancer,
        user=request.user,
        wallet_type=wallet_type,
        wallet_address=wallet_address,
        signature=signature,
        connection_status='connected'
    )
    
    serializer = FreelancerWalletConnectionSerializer(connection)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def freelancer_web3_stats(request, freelancer_id):
    """
    Get Web3 statistics for a freelancer.
    """
    try:
        freelancer = request.user.freelancer_profile
    except:
        return Response(
            {'error': 'Freelancer profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get Web3 statistics
    nft_count = FreelancerNFTInstance.objects.filter(freelancer=freelancer).count()
    contract_count = FreelancerSmartContract.objects.filter(freelancer=freelancer).count()
    wallet_count = FreelancerWalletConnection.objects.filter(
        freelancer=freelancer, connection_status='connected'
    ).count()
    transaction_count = FreelancerWeb3Transaction.objects.filter(freelancer=freelancer).count()
    
    # Get total reputation tokens
    reputation_tokens = FreelancerReputationToken.objects.filter(freelancer=freelancer)
    total_reputation = sum(float(token.token_amount) for token in reputation_tokens)
    
    stats = {
        'freelancer_id': freelancer.freelancer_id,
        'nft_badges_count': nft_count,
        'smart_contracts_count': contract_count,
        'connected_wallets_count': wallet_count,
        'total_transactions_count': transaction_count,
        'total_reputation_tokens': total_reputation,
        'blockchain_verified': freelancer.blockchain_verified,
        'wallet_address': freelancer.wallet_address,
    }
    
    return Response(stats)

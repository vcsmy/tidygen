"""
URL configuration for freelancer_web3 app.
"""
from django.urls import path
from . import views

app_name = 'freelancer_web3'

urlpatterns = [
    # NFT Badges
    path('badges/', views.FreelancerNFTBadgeListView.as_view(), name='nft-badge-list'),
    path('nfts/', views.FreelancerNFTInstanceView.as_view(), name='nft-instance-list-create'),
    
    # Smart Contracts
    path('contracts/', views.FreelancerSmartContractView.as_view(), name='smart-contract-list-create'),
    
    # Reputation Tokens
    path('reputation-tokens/', views.FreelancerReputationTokenView.as_view(), name='reputation-token-list'),
    
    # Wallet Connections
    path('wallets/', views.FreelancerWalletConnectionView.as_view(), name='wallet-connection-list-create'),
    path('wallets/connect/', views.connect_wallet, name='connect-wallet'),
    
    # Web3 Transactions
    path('transactions/', views.FreelancerWeb3TransactionView.as_view(), name='web3-transaction-list'),
    
    # Statistics
    path('freelancers/<int:freelancer_id>/stats/', views.freelancer_web3_stats, name='freelancer-web3-stats'),
]

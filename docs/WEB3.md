# Web3 Integration Guide

## ⛓️ **Overview**

The TidyGen ERP system includes comprehensive Web3 integration, enabling blockchain functionality, cryptocurrency management, and decentralized application features. This guide covers all Web3 capabilities and implementation details.

## 🏗️ **Web3 Architecture**

### **Technology Stack**
- **ethers.js** - Ethereum JavaScript library
- **MetaMask** - Browser wallet integration
- **Web3.py** - Python Web3 library (backend)
- **Ganache** - Local Ethereum testnet
- **IPFS** - Decentralized file storage
- **Smart Contracts** - Solidity contracts for business logic

### **Web3 Components**
```
Web3 Integration/
├── Frontend/
│   ├── Web3Context.tsx      # Web3 state management
│   ├── WalletConnect.tsx    # Wallet connection component
│   ├── TransactionHistory.tsx # Transaction display
│   ├── SmartContractUI.tsx  # Contract interaction UI
│   ├── DeFiDashboard.tsx    # DeFi protocol interface
│   └── NFTGallery.tsx       # NFT management interface
├── Backend/
│   ├── models.py            # Web3 data models
│   ├── views.py             # Web3 API endpoints
│   ├── serializers.py       # Web3 data serialization
│   └── utils.py             # Web3 utility functions
└── Smart Contracts/
    ├── ERC20Token.sol       # Token contract
    ├── ERC721NFT.sol        # NFT contract
    └── DeFiProtocol.sol     # DeFi protocol contract
```

## 🔗 **Wallet Management**

### **Wallet Connection**
```tsx
import { useWeb3 } from '@/contexts/Web3Context'

function WalletConnect() {
  const { 
    account, 
    connectWallet, 
    disconnectWallet, 
    isConnected,
    isLoading 
  } = useWeb3()

  if (isLoading) return <div>Connecting...</div>

  return (
    <div>
      {isConnected ? (
        <div>
          <p>Connected: {account}</p>
          <Button onClick={disconnectWallet}>Disconnect</Button>
        </div>
      ) : (
        <Button onClick={connectWallet}>Connect Wallet</Button>
      )}
    </div>
  )
}
```

### **Web3Context Implementation**
```tsx
// contexts/Web3Context.tsx
import { createContext, useContext, useEffect, useState } from 'react'
import { ethers } from 'ethers'

interface Web3ContextType {
  account: string | null
  provider: ethers.providers.Web3Provider | null
  signer: ethers.Signer | null
  isConnected: boolean
  isLoading: boolean
  connectWallet: () => Promise<void>
  disconnectWallet: () => void
  switchNetwork: (chainId: number) => Promise<void>
  getBalance: (address: string) => Promise<string>
}

const Web3Context = createContext<Web3ContextType | undefined>(undefined)

export function Web3Provider({ children }: { children: React.ReactNode }) {
  const [account, setAccount] = useState<string | null>(null)
  const [provider, setProvider] = useState<ethers.providers.Web3Provider | null>(null)
  const [signer, setSigner] = useState<ethers.Signer | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const connectWallet = async () => {
    if (!window.ethereum) {
      throw new Error('MetaMask not installed')
    }

    setIsLoading(true)
    try {
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      })
      
      const provider = new ethers.providers.Web3Provider(window.ethereum)
      const signer = provider.getSigner()
      
      setAccount(accounts[0])
      setProvider(provider)
      setSigner(signer)
      setIsConnected(true)
    } catch (error) {
      console.error('Failed to connect wallet:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const disconnectWallet = () => {
    setAccount(null)
    setProvider(null)
    setSigner(null)
    setIsConnected(false)
  }

  return (
    <Web3Context.Provider value={{
      account,
      provider,
      signer,
      isConnected,
      isLoading,
      connectWallet,
      disconnectWallet,
      switchNetwork,
      getBalance
    }}>
      {children}
    </Web3Context.Provider>
  )
}

export const useWeb3 = () => {
  const context = useContext(Web3Context)
  if (!context) {
    throw new Error('useWeb3 must be used within Web3Provider')
  }
  return context
}
```

## 💰 **Cryptocurrency Management**

### **Token Management**
```tsx
// components/web3/TokenManager.tsx
import { useState, useEffect } from 'react'
import { useWeb3 } from '@/contexts/Web3Context'
import { ethers } from 'ethers'

interface Token {
  address: string
  symbol: string
  name: string
  decimals: number
  balance: string
}

function TokenManager() {
  const { account, provider } = useWeb3()
  const [tokens, setTokens] = useState<Token[]>([])
  const [loading, setLoading] = useState(false)

  const loadTokens = async () => {
    if (!account || !provider) return

    setLoading(true)
    try {
      // Load ERC20 tokens
      const tokenAddresses = [
        '0xA0b86a33E6441b8C4C8C0C4C4C4C4C4C4C4C4C4', // USDC
        '0x514910771AF9Ca656af840dff83E8264EcF986CA'  // LINK
      ]

      const tokenPromises = tokenAddresses.map(async (address) => {
        const contract = new ethers.Contract(
          address,
          ERC20_ABI,
          provider
        )

        const [symbol, name, decimals, balance] = await Promise.all([
          contract.symbol(),
          contract.name(),
          contract.decimals(),
          contract.balanceOf(account)
        ])

        return {
          address,
          symbol,
          name,
          decimals,
          balance: ethers.utils.formatUnits(balance, decimals)
        }
      })

      const tokenData = await Promise.all(tokenPromises)
      setTokens(tokenData)
    } catch (error) {
      console.error('Failed to load tokens:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTokens()
  }, [account, provider])

  return (
    <div>
      <h2>Token Balances</h2>
      {loading ? (
        <div>Loading tokens...</div>
      ) : (
        <div className="space-y-4">
          {tokens.map((token) => (
            <div key={token.address} className="flex justify-between items-center p-4 border rounded">
              <div>
                <h3 className="font-semibold">{token.name}</h3>
                <p className="text-sm text-gray-600">{token.symbol}</p>
              </div>
              <div className="text-right">
                <p className="font-mono">{token.balance}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

### **Transaction History**
```tsx
// components/web3/TransactionHistory.tsx
import { useState, useEffect } from 'react'
import { useWeb3 } from '@/contexts/Web3Context'
import { ApiService } from '@/lib/api'

interface Transaction {
  id: number
  tx_hash: string
  wallet: string
  transaction_type: 'send' | 'receive' | 'contract_interaction'
  amount: string
  status: 'pending' | 'confirmed' | 'failed'
  gas_used: number
  gas_price: string
  created_at: string
}

function TransactionHistory() {
  const { account } = useWeb3()
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(false)

  const loadTransactions = async () => {
    if (!account) return

    setLoading(true)
    try {
      const response = await ApiService.get('/web3/transactions/')
      setTransactions(response.results || response)
    } catch (error) {
      console.error('Failed to load transactions:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTransactions()
  }, [account])

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'send': return '📤'
      case 'receive': return '📥'
      case 'contract_interaction': return '🔗'
      default: return '❓'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'text-green-600'
      case 'pending': return 'text-yellow-600'
      case 'failed': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div>
      <h2>Transaction History</h2>
      {loading ? (
        <div>Loading transactions...</div>
      ) : (
        <div className="space-y-2">
          {transactions.map((tx) => (
            <div key={tx.id} className="flex items-center justify-between p-3 border rounded">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{getTransactionIcon(tx.transaction_type)}</span>
                <div>
                  <p className="font-mono text-sm">{tx.tx_hash.slice(0, 10)}...</p>
                  <p className="text-sm text-gray-600">{tx.transaction_type}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold">{tx.amount} ETH</p>
                <p className={`text-sm ${getStatusColor(tx.status)}`}>
                  {tx.status}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

## 🔗 **Smart Contract Integration**

### **Contract Interaction**
```tsx
// components/web3/SmartContractInterface.tsx
import { useState } from 'react'
import { useWeb3 } from '@/contexts/Web3Context'
import { ethers } from 'ethers'

interface ContractMethod {
  name: string
  inputs: any[]
  outputs: any[]
  stateMutability: string
}

function SmartContractInterface() {
  const { signer, account } = useWeb3()
  const [contractAddress, setContractAddress] = useState('')
  const [contract, setContract] = useState<ethers.Contract | null>(null)
  const [methods, setMethods] = useState<ContractMethod[]>([])
  const [loading, setLoading] = useState(false)

  const loadContract = async () => {
    if (!contractAddress || !signer) return

    setLoading(true)
    try {
      // Load contract ABI (you would typically fetch this from IPFS or a registry)
      const contract = new ethers.Contract(
        contractAddress,
        CONTRACT_ABI,
        signer
      )

      setContract(contract)
      
      // Extract readable methods
      const contractMethods = CONTRACT_ABI.filter(
        (item: any) => item.type === 'function' && 
        (item.stateMutability === 'view' || item.stateMutability === 'pure')
      )
      setMethods(contractMethods)
    } catch (error) {
      console.error('Failed to load contract:', error)
    } finally {
      setLoading(false)
    }
  }

  const callMethod = async (method: ContractMethod) => {
    if (!contract) return

    try {
      const result = await contract[method.name]()
      console.log(`Result of ${method.name}:`, result)
    } catch (error) {
      console.error(`Failed to call ${method.name}:`, error)
    }
  }

  return (
    <div>
      <h2>Smart Contract Interface</h2>
      
      <div className="mb-4">
        <input
          type="text"
          placeholder="Contract Address"
          value={contractAddress}
          onChange={(e) => setContractAddress(e.target.value)}
          className="w-full p-2 border rounded"
        />
        <Button onClick={loadContract} disabled={loading}>
          Load Contract
        </Button>
      </div>

      {contract && (
        <div>
          <h3>Contract Methods</h3>
          <div className="space-y-2">
            {methods.map((method, index) => (
              <div key={index} className="flex items-center justify-between p-2 border rounded">
                <div>
                  <p className="font-semibold">{method.name}</p>
                  <p className="text-sm text-gray-600">
                    {method.inputs.map(input => input.type).join(', ')}
                  </p>
                </div>
                <Button onClick={() => callMethod(method)}>
                  Call
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
```

## 🏦 **DeFi Protocol Integration**

### **DeFi Dashboard**
```tsx
// components/web3/DeFiDashboard.tsx
import { useState, useEffect } from 'react'
import { useWeb3 } from '@/contexts/Web3Context'
import { ApiService } from '@/lib/api'

interface DeFiPosition {
  id: number
  protocol: string
  position_type: 'lending' | 'borrowing' | 'liquidity' | 'staking'
  asset: string
  amount: string
  apy: number
  value_usd: string
  created_at: string
}

function DeFiDashboard() {
  const { account } = useWeb3()
  const [positions, setPositions] = useState<DeFiPosition[]>([])
  const [loading, setLoading] = useState(false)

  const loadPositions = async () => {
    if (!account) return

    setLoading(true)
    try {
      const response = await ApiService.get('/web3/defi-positions/')
      setPositions(response.results || response)
    } catch (error) {
      console.error('Failed to load DeFi positions:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPositions()
  }, [account])

  const getPositionIcon = (type: string) => {
    switch (type) {
      case 'lending': return '💰'
      case 'borrowing': return '📊'
      case 'liquidity': return '💧'
      case 'staking': return '🔒'
      default: return '❓'
    }
  }

  const getProtocolColor = (protocol: string) => {
    switch (protocol.toLowerCase()) {
      case 'compound': return 'bg-blue-100 text-blue-800'
      case 'aave': return 'bg-purple-100 text-purple-800'
      case 'uniswap': return 'bg-pink-100 text-pink-800'
      case 'yearn': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div>
      <h2>DeFi Positions</h2>
      {loading ? (
        <div>Loading DeFi positions...</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {positions.map((position) => (
            <div key={position.id} className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">{getPositionIcon(position.position_type)}</span>
                <Badge className={getProtocolColor(position.protocol)}>
                  {position.protocol}
                </Badge>
              </div>
              
              <div className="space-y-1">
                <p className="font-semibold">{position.asset}</p>
                <p className="text-sm text-gray-600">{position.position_type}</p>
                <p className="font-mono">{position.amount}</p>
                <p className="text-sm">${position.value_usd}</p>
                <p className="text-sm text-green-600">{position.apy}% APY</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

## 🎨 **NFT Management**

### **NFT Gallery**
```tsx
// components/web3/NFTGallery.tsx
import { useState, useEffect } from 'react'
import { useWeb3 } from '@/contexts/Web3Context'
import { ApiService } from '@/lib/api'

interface NFT {
  id: number
  token_id: string
  contract_address: string
  name: string
  description: string
  image_url: string
  collection: string
  owner: string
  created_at: string
}

function NFTGallery() {
  const { account } = useWeb3()
  const [nfts, setNfts] = useState<NFT[]>([])
  const [loading, setLoading] = useState(false)

  const loadNFTs = async () => {
    if (!account) return

    setLoading(true)
    try {
      const response = await ApiService.get('/web3/nfts/')
      setNfts(response.results || response)
    } catch (error) {
      console.error('Failed to load NFTs:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadNFTs()
  }, [account])

  return (
    <div>
      <h2>NFT Collection</h2>
      {loading ? (
        <div>Loading NFTs...</div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {nfts.map((nft) => (
            <div key={nft.id} className="border rounded-lg overflow-hidden">
              <img
                src={nft.image_url}
                alt={nft.name}
                className="w-full h-48 object-cover"
              />
              <div className="p-4">
                <h3 className="font-semibold truncate">{nft.name}</h3>
                <p className="text-sm text-gray-600 truncate">{nft.description}</p>
                <p className="text-sm text-blue-600">{nft.collection}</p>
                <p className="text-xs text-gray-500 font-mono">
                  #{nft.token_id}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

## 🔧 **Backend Web3 Integration**

### **Web3 Models**
```python
# apps/web3/models.py
from django.db import models
from apps.organizations.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()

class Wallet(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=42, unique=True)
    blockchain = models.CharField(max_length=20, default='ethereum')
    wallet_type = models.CharField(max_length=20, choices=[
        ('external', 'External'),
        ('internal', 'Internal'),
        ('contract', 'Contract')
    ])
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BlockchainTransaction(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    tx_hash = models.CharField(max_length=66, unique=True)
    transaction_type = models.CharField(max_length=20, choices=[
        ('send', 'Send'),
        ('receive', 'Receive'),
        ('contract_interaction', 'Contract Interaction')
    ])
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed')
    ])
    gas_used = models.BigIntegerField()
    gas_price = models.DecimalField(max_digits=20, decimal_places=8)
    block_number = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SmartContract(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=42, unique=True)
    abi = models.JSONField()
    blockchain = models.CharField(max_length=20, default='ethereum')
    contract_type = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Token(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    contract_address = models.CharField(max_length=42)
    decimals = models.IntegerField()
    total_supply = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    blockchain = models.CharField(max_length=20, default='ethereum')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DeFiPosition(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    protocol = models.CharField(max_length=50)
    position_type = models.CharField(max_length=20, choices=[
        ('lending', 'Lending'),
        ('borrowing', 'Borrowing'),
        ('liquidity', 'Liquidity'),
        ('staking', 'Staking')
    ])
    asset = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    apy = models.DecimalField(max_digits=5, decimal_places=2)
    value_usd = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class NFT(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    token_id = models.CharField(max_length=100)
    contract_address = models.CharField(max_length=42)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    collection = models.CharField(max_length=100)
    owner = models.CharField(max_length=42)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### **Web3 API Views**
```python
# apps/web3/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Wallet, BlockchainTransaction, SmartContract, Token, DeFiPosition, NFT
from .serializers import (
    WalletSerializer, TransactionSerializer, SmartContractSerializer,
    TokenSerializer, DeFiPositionSerializer, NFTSerializer
)

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['blockchain', 'wallet_type', 'is_active']
    search_fields = ['name', 'address']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    @action(detail=True, methods=['post'])
    def sync_balance(self, request, pk=None):
        wallet = self.get_object()
        # Implement balance synchronization logic
        return Response({'status': 'Balance synced'})

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = BlockchainTransaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['wallet', 'transaction_type', 'status']
    search_fields = ['tx_hash']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

class SmartContractViewSet(viewsets.ModelViewSet):
    queryset = SmartContract.objects.all()
    serializer_class = SmartContractSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['blockchain', 'contract_type', 'is_verified']
    search_fields = ['name', 'address']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)

    @action(detail=True, methods=['post'])
    def call_method(self, request, pk=None):
        contract = self.get_object()
        method_name = request.data.get('method_name')
        params = request.data.get('params', [])
        
        # Implement contract method calling logic
        return Response({'result': 'Method called successfully'})
```

## 🚀 **Deployment and Configuration**

### **Environment Variables**
```bash
# Web3 Configuration
WEB3_PROVIDER_URL=http://localhost:8545
WEB3_NETWORK_ID=1337
WEB3_PRIVATE_KEY=your-private-key
IPFS_GATEWAY_URL=https://ipfs.io/ipfs/
```

### **Docker Configuration**
```yaml
# docker-compose.yml
services:
  ganache:
    image: trufflesuite/ganache-cli:latest
    container_name: tidygen_ganache
    command: ganache-cli --host 0.0.0.0 --port 8545 --networkId 1337 --gasLimit 10000000 --gasPrice 20000000000 --accounts 10 --defaultBalanceEther 1000 --deterministic
    ports:
      - "8545:8545"
    restart: unless-stopped
```

## 🔒 **Security Considerations**

### **Wallet Security**
- Never store private keys in the database
- Use hardware wallets for high-value transactions
- Implement proper access controls
- Audit smart contract interactions

### **Smart Contract Security**
- Verify contract source code
- Use established libraries and patterns
- Implement proper access controls
- Test thoroughly before deployment

### **API Security**
- Validate all inputs
- Implement rate limiting
- Use HTTPS for all communications
- Monitor for suspicious activity

## 📚 **Best Practices**

### **Frontend Development**
- Always check wallet connection before Web3 operations
- Handle network switching gracefully
- Provide clear error messages
- Implement proper loading states

### **Backend Development**
- Validate all blockchain data
- Implement proper error handling
- Use database transactions for consistency
- Monitor gas usage and costs

### **Smart Contract Development**
- Follow established security patterns
- Use OpenZeppelin libraries
- Implement proper access controls
- Test with multiple scenarios

## 🔗 **Useful Resources**

- [ethers.js Documentation](https://docs.ethers.io/)
- [MetaMask Developer Guide](https://docs.metamask.io/guide/)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)

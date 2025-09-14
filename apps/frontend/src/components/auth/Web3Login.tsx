import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/enhanced-button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Wallet, 
  Shield, 
  Key, 
  Globe, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  ExternalLink,
  Info
} from 'lucide-react';
import { toast } from '@/components/ui/enhanced-notifications';

// Web3 Provider Types
interface Web3Provider {
  id: string;
  name: string;
  icon: string;
  description: string;
  supported: boolean;
  installUrl?: string;
}

interface DIDDocument {
  id: string;
  publicKey: string[];
  service: Array<{
    id: string;
    type: string;
    serviceEndpoint: string;
  }>;
}

interface Web3AuthResult {
  did: string;
  publicKey: string;
  signature: string;
  provider: string;
  timestamp: number;
}

// Mock Web3 providers (in real implementation, these would be actual wallet connections)
const web3Providers: Web3Provider[] = [
  {
    id: 'polkadot-js',
    name: 'Polkadot.js',
    icon: '🔗',
    description: 'Connect with Polkadot.js wallet',
    supported: true,
  },
  {
    id: 'metamask',
    name: 'MetaMask',
    icon: '🦊',
    description: 'Connect with MetaMask wallet',
    supported: true,
  },
  {
    id: 'substrate-connect',
    name: 'Substrate Connect',
    icon: '⚡',
    description: 'Light client connection',
    supported: true,
  },
  {
    id: 'ledger',
    name: 'Ledger',
    icon: '🔒',
    description: 'Hardware wallet support',
    supported: false,
  },
];

interface Web3LoginProps {
  onSuccess: (result: Web3AuthResult) => void;
  onError: (error: Error) => void;
  className?: string;
}

export function Web3Login({ onSuccess, onError, className }: Web3LoginProps) {
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectedProvider, setConnectedProvider] = useState<string | null>(null);
  const [didDocument, setDidDocument] = useState<DIDDocument | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Check if Web3 is available
  const [isWeb3Available, setIsWeb3Available] = useState(false);

  useEffect(() => {
    // Check for Web3 availability
    const checkWeb3Availability = () => {
      const hasPolkadot = !!(window as any).injectedWeb3;
      const hasMetaMask = !!(window as any).ethereum;
      const hasSubstrateConnect = !!(window as any).SubstrateConnect;
      
      setIsWeb3Available(hasPolkadot || hasMetaMask || hasSubstrateConnect);
    };

    checkWeb3Availability();
    
    // Listen for wallet installation
    const handleWalletInstall = () => {
      checkWeb3Availability();
    };

    window.addEventListener('wallet-installed', handleWalletInstall);
    return () => window.removeEventListener('wallet-installed', handleWalletInstall);
  }, []);

  const connectWallet = async (providerId: string) => {
    setIsConnecting(true);
    setError(null);

    try {
      let result: Web3AuthResult;

      switch (providerId) {
        case 'polkadot-js':
          result = await connectPolkadotJS();
          break;
        case 'metamask':
          result = await connectMetaMask();
          break;
        case 'substrate-connect':
          result = await connectSubstrateConnect();
          break;
        default:
          throw new Error(`Unsupported provider: ${providerId}`);
      }

      setConnectedProvider(providerId);
      onSuccess(result);
      toast.success('Web3 Connected', 'Successfully connected with Web3 wallet');
      
    } catch (err: any) {
      setError(err.message);
      onError(err);
      toast.error('Connection Failed', err.message || 'Failed to connect wallet');
    } finally {
      setIsConnecting(false);
    }
  };

  const connectPolkadotJS = async (): Promise<Web3AuthResult> => {
    const injectedWeb3 = (window as any).injectedWeb3;
    
    if (!injectedWeb3) {
      throw new Error('Polkadot.js wallet not found. Please install it first.');
    }

    // Get the first available provider
    const provider = Object.values(injectedWeb3)[0] as any;
    
    if (!provider) {
      throw new Error('No Polkadot.js provider available');
    }

    // Enable the provider
    const extension = await provider.enable('TidyGen');
    
    if (!extension) {
      throw new Error('Failed to enable Polkadot.js extension');
    }

    // Get accounts
    const accounts = await extension.accounts.get();
    
    if (accounts.length === 0) {
      throw new Error('No accounts found in Polkadot.js wallet');
    }

    const account = accounts[0];
    
    // Create DID document
    const did = `did:substrate:${account.address}`;
    const didDoc: DIDDocument = {
      id: did,
      publicKey: [{
        id: `${did}#key-1`,
        type: 'Ed25519VerificationKey2018',
        controller: did,
        publicKeyHex: account.publicKey,
      }],
      service: [{
        id: `${did}#substrate`,
        type: 'SubstrateAccount',
        serviceEndpoint: `substrate://${account.address}`,
      }],
    };

    setDidDocument(didDoc);

    // Sign a message to prove ownership
    const message = `TidyGen Login: ${Date.now()}`;
    const signature = await extension.signer.signRaw({
      address: account.address,
      data: message,
      type: 'bytes',
    });

    return {
      did,
      publicKey: account.publicKey,
      signature: signature.signature,
      provider: 'polkadot-js',
      timestamp: Date.now(),
    };
  };

  const connectMetaMask = async (): Promise<Web3AuthResult> => {
    const ethereum = (window as any).ethereum;
    
    if (!ethereum) {
      throw new Error('MetaMask not found. Please install it first.');
    }

    // Request account access
    const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
    
    if (accounts.length === 0) {
      throw new Error('No accounts found in MetaMask');
    }

    const account = accounts[0];
    
    // Create DID document
    const did = `did:ethr:${account}`;
    const didDoc: DIDDocument = {
      id: did,
      publicKey: [{
        id: `${did}#key-1`,
        type: 'Secp256k1VerificationKey2018',
        controller: did,
        publicKeyHex: account,
      }],
      service: [{
        id: `${did}#ethereum`,
        type: 'EthereumAccount',
        serviceEndpoint: `ethereum://${account}`,
      }],
    };

    setDidDocument(didDoc);

    // Sign a message
    const message = `TidyGen Login: ${Date.now()}`;
    const signature = await ethereum.request({
      method: 'personal_sign',
      params: [message, account],
    });

    return {
      did,
      publicKey: account,
      signature,
      provider: 'metamask',
      timestamp: Date.now(),
    };
  };

  const connectSubstrateConnect = async (): Promise<Web3AuthResult> => {
    const SubstrateConnect = (window as any).SubstrateConnect;
    
    if (!SubstrateConnect) {
      throw new Error('Substrate Connect not available');
    }

    // This is a simplified implementation
    // In reality, you'd connect to a specific chain and get account info
    const mockAccount = {
      address: '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY',
      publicKey: '0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48',
    };

    const did = `did:substrate:connect:${mockAccount.address}`;
    const didDoc: DIDDocument = {
      id: did,
      publicKey: [{
        id: `${did}#key-1`,
        type: 'Ed25519VerificationKey2018',
        controller: did,
        publicKeyHex: mockAccount.publicKey,
      }],
      service: [{
        id: `${did}#substrate-connect`,
        type: 'SubstrateConnect',
        serviceEndpoint: 'substrate-connect://light-client',
      }],
    };

    setDidDocument(didDoc);

    return {
      did,
      publicKey: mockAccount.publicKey,
      signature: 'mock-signature',
      provider: 'substrate-connect',
      timestamp: Date.now(),
    };
  };

  const installWallet = (provider: Web3Provider) => {
    if (provider.installUrl) {
      window.open(provider.installUrl, '_blank');
    }
  };

  if (!isWeb3Available) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Wallet className="h-5 w-5 mr-2" />
            Web3 Login
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              Web3 wallets are not detected. Please install a compatible wallet to use Web3 login.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Wallet className="h-5 w-5 mr-2" />
          Web3 Login
          <Badge variant="secondary" className="ml-2">
            <Shield className="h-3 w-3 mr-1" />
            Decentralized
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {connectedProvider && didDocument && (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              Connected with {web3Providers.find(p => p.id === connectedProvider)?.name}
              <br />
              <span className="text-sm text-muted-foreground">
                DID: {didDocument.id}
              </span>
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          {web3Providers.map((provider) => (
            <Button
              key={provider.id}
              variant={provider.supported ? "outline" : "secondary"}
              className="w-full justify-start"
              disabled={!provider.supported || isConnecting}
              onClick={() => {
                if (provider.supported) {
                  connectWallet(provider.id);
                } else {
                  installWallet(provider);
                }
              }}
            >
              {isConnecting && connectedProvider === provider.id ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <span className="mr-2">{provider.icon}</span>
              )}
              <div className="flex-1 text-left">
                <div className="font-medium">{provider.name}</div>
                <div className="text-sm text-muted-foreground">
                  {provider.description}
                </div>
              </div>
              {!provider.supported && (
                <ExternalLink className="h-4 w-4" />
              )}
            </Button>
          ))}
        </div>

        <div className="text-xs text-muted-foreground space-y-1">
          <div className="flex items-center">
            <Key className="h-3 w-3 mr-1" />
            Your private keys never leave your wallet
          </div>
          <div className="flex items-center">
            <Globe className="h-3 w-3 mr-1" />
            Decentralized identity verification
          </div>
          <div className="flex items-center">
            <Shield className="h-3 w-3 mr-1" />
            Enhanced security with blockchain
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default Web3Login;

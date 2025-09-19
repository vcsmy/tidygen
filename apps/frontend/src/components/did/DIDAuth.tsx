/**
 * DID Authentication Component
 * 
 * Provides UI for DID-based authentication using wallet signatures.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, Key, Shield, CheckCircle, XCircle, ExternalLink } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface DIDAuthProps {
  onAuthSuccess?: (session: any) => void;
  onAuthError?: (error: string) => void;
}

interface DIDSession {
  id: number;
  session_token: string;
  created_at: string;
  expires_at: string;
  is_active: boolean;
  did: {
    did: string;
    status: string;
  };
}

const DIDAuth: React.FC<DIDAuthProps> = ({ onAuthSuccess, onAuthError }) => {
  const [did, setDid] = useState('');
  const [signature, setSignature] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState<DIDSession | null>(null);
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');
  const { toast } = useToast();

  // Check if wallet is available
  useEffect(() => {
    const checkWallet = async () => {
      if (typeof window !== 'undefined' && (window as any).ethereum) {
        try {
          const accounts = await (window as any).ethereum.request({ method: 'eth_accounts' });
          if (accounts.length > 0) {
            setWalletConnected(true);
            setWalletAddress(accounts[0]);
          }
        } catch (error) {
          console.error('Error checking wallet:', error);
        }
      }
    };

    checkWallet();
  }, []);

  // Connect wallet
  const connectWallet = async () => {
    if (typeof window !== 'undefined' && (window as any).ethereum) {
      try {
        const accounts = await (window as any).ethereum.request({ 
          method: 'eth_requestAccounts' 
        });
        if (accounts.length > 0) {
          setWalletConnected(true);
          setWalletAddress(accounts[0]);
          toast({
            title: "Wallet Connected",
            description: `Connected to ${accounts[0]}`,
          });
        }
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to connect wallet",
          variant: "destructive",
        });
      }
    } else {
      toast({
        title: "Error",
        description: "MetaMask not found. Please install MetaMask.",
        variant: "destructive",
      });
    }
  };

  // Generate DID from wallet address
  const generateDID = () => {
    if (walletAddress) {
      const didString = `did:ethr:${walletAddress}`;
      setDid(didString);
      toast({
        title: "DID Generated",
        description: `Generated DID: ${didString}`,
      });
    }
  };

  // Sign message with wallet
  const signMessage = async () => {
    if (!walletAddress || !message) {
      toast({
        title: "Error",
        description: "Please connect wallet and enter a message",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      const signature = await (window as any).ethereum.request({
        method: 'personal_sign',
        params: [message, walletAddress],
      });
      setSignature(signature);
      toast({
        title: "Message Signed",
        description: "Message signed successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to sign message",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Authenticate with DID
  const authenticateWithDID = async () => {
    if (!did || !signature || !message) {
      toast({
        title: "Error",
        description: "Please provide DID, signature, and message",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('/api/v1/did-auth/sessions/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          did,
          signature,
          message,
          ip_address: await getClientIP(),
          user_agent: navigator.userAgent,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setSession(result.session);
        toast({
          title: "Authentication Successful",
          description: "Successfully authenticated with DID",
        });
        onAuthSuccess?.(result.session);
      } else {
        const error = await response.json();
        const errorMessage = error.error || "Authentication failed";
        toast({
          title: "Authentication Failed",
          description: errorMessage,
          variant: "destructive",
        });
        onAuthError?.(errorMessage);
      }
    } catch (error) {
      const errorMessage = "Failed to authenticate with DID";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
      onAuthError?.(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Logout
  const logout = async () => {
    if (!session) return;

    try {
      setLoading(true);
      const response = await fetch('/api/v1/did-auth/sessions/logout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_token: session.session_token,
        }),
      });

      if (response.ok) {
        setSession(null);
        setSignature('');
        toast({
          title: "Logged Out",
          description: "Successfully logged out",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to logout",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Get client IP (simplified)
  const getClientIP = async (): Promise<string> => {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch {
      return '127.0.0.1';
    }
  };

  // Generate random message for signing
  const generateRandomMessage = () => {
    const timestamp = Date.now();
    const randomString = Math.random().toString(36).substring(7);
    const message = `TidyGen DID Authentication\nTimestamp: ${timestamp}\nNonce: ${randomString}`;
    setMessage(message);
  };

  if (session) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            DID Authentication - Active Session
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="font-medium">Authenticated</span>
            </div>
            <div className="text-sm text-muted-foreground">
              <div>DID: <code className="bg-muted px-1 rounded">{session.did.did}</code></div>
              <div>Status: <Badge variant="default">{session.did.status}</Badge></div>
              <div>Session Token: <code className="bg-muted px-1 rounded">{session.session_token.substring(0, 20)}...</code></div>
              <div>Expires: {new Date(session.expires_at).toLocaleString()}</div>
            </div>
          </div>
          <Button onClick={logout} disabled={loading} variant="outline">
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Logout
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Key className="h-5 w-5" />
          DID Authentication
        </CardTitle>
        <CardDescription>
          Authenticate using your Decentralized Identity and wallet signature
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!walletConnected ? (
          <Alert>
            <AlertDescription>
              Connect your wallet to start DID authentication
            </AlertDescription>
          </Alert>
        ) : (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm">Wallet Connected: {walletAddress}</span>
            </div>
          </div>
        )}

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="wallet-connect">Wallet Connection</Label>
            <Button 
              onClick={connectWallet} 
              disabled={walletConnected}
              variant={walletConnected ? "outline" : "default"}
            >
              {walletConnected ? "Wallet Connected" : "Connect Wallet"}
            </Button>
          </div>

          {walletConnected && (
            <>
              <div className="space-y-2">
                <Label htmlFor="did">DID (Decentralized Identifier)</Label>
                <div className="flex gap-2">
                  <Input
                    id="did"
                    value={did}
                    onChange={(e) => setDid(e.target.value)}
                    placeholder="did:ethr:0x..."
                    className="font-mono"
                  />
                  <Button onClick={generateDID} variant="outline" size="sm">
                    Generate
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="message">Message to Sign</Label>
                <div className="flex gap-2">
                  <Input
                    id="message"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Enter message to sign"
                  />
                  <Button onClick={generateRandomMessage} variant="outline" size="sm">
                    Generate
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="signature">Signature</Label>
                <div className="flex gap-2">
                  <Input
                    id="signature"
                    value={signature}
                    onChange={(e) => setSignature(e.target.value)}
                    placeholder="0x..."
                    className="font-mono"
                  />
                  <Button 
                    onClick={signMessage} 
                    disabled={loading || !message}
                    variant="outline" 
                    size="sm"
                  >
                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Sign
                  </Button>
                </div>
              </div>

              <Button 
                onClick={authenticateWithDID} 
                disabled={loading || !did || !signature || !message}
                className="w-full"
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Authenticate with DID
              </Button>
            </>
          )}
        </div>

        <Alert>
          <AlertDescription>
            <div className="space-y-1">
              <div className="font-medium">How it works:</div>
              <ol className="list-decimal list-inside space-y-1 text-sm">
                <li>Connect your MetaMask wallet</li>
                <li>Generate or enter your DID</li>
                <li>Sign a message with your wallet</li>
                <li>Authenticate using your DID and signature</li>
              </ol>
            </div>
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
};

export default DIDAuth;

/**
 * DAOProposal Component
 * 
 * Component for creating and voting on DAO proposals
 */

import React, { useState, useEffect } from 'react';
import { Vote, CheckCircle, XCircle, Loader2, Plus } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { toast } from 'sonner';
import { createProposal, voteOnProposal, queryProposal } from '../../web3/substrateTransactions';
import type { InjectedAccountWithMeta } from '@polkadot/extension-dapp/types';

interface DAOProposalProps {
  selectedAccount?: InjectedAccountWithMeta | null;
}

interface Proposal {
  id: number;
  proposer: string;
  title: string;
  description: string;
  votesFor: number;
  votesAgainst: number;
  totalVotes: number;
  status: string;
  votingEnd: number;
}

export function DAOProposal({ selectedAccount }: DAOProposalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [votingPeriod, setVotingPeriod] = useState('100');
  const [isCreating, setIsCreating] = useState(false);
  const [isVoting, setIsVoting] = useState(false);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [isLoadingProposals, setIsLoadingProposals] = useState(false);

  // Load proposals
  const loadProposals = async () => {
    setIsLoadingProposals(true);
    try {
      const proposalsList: Proposal[] = [];
      
      // Try to load first 10 proposals
      for (let i = 0; i < 10; i++) {
        const proposal = await queryProposal(i);
        if (proposal) {
          proposalsList.push({
            id: proposal.id,
            proposer: proposal.proposer,
            title: new TextDecoder().decode(new Uint8Array(proposal.title)),
            description: new TextDecoder().decode(new Uint8Array(proposal.description)),
            votesFor: proposal.votesFor,
            votesAgainst: proposal.votesAgainst,
            totalVotes: proposal.totalVotes,
            status: proposal.status,
            votingEnd: proposal.votingEnd,
          });
        }
      }
      
      setProposals(proposalsList);
    } catch (error) {
      console.error('Error loading proposals:', error);
    } finally {
      setIsLoadingProposals(false);
    }
  };

  useEffect(() => {
    loadProposals();
  }, []);

  const handleCreateProposal = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title || !description) {
      toast.error('Please fill in all fields');
      return;
    }

    if (!selectedAccount) {
      toast.error('Please connect your wallet first');
      return;
    }

    setIsCreating(true);

    try {
      const result = await createProposal(
        {
          title,
          description,
          votingPeriod: parseInt(votingPeriod) || undefined,
        },
        selectedAccount
      );

      if (result.success) {
        toast.success('Proposal created on blockchain!', {
          description: `Transaction: ${result.txHash?.slice(0, 10)}...`,
        });
        
        // Reset form
        setTitle('');
        setDescription('');
        setVotingPeriod('100');
        
        // Reload proposals
        setTimeout(loadProposals, 2000);
      } else {
        toast.error('Failed to create proposal', {
          description: result.error,
        });
      }
    } catch (error) {
      console.error('Proposal creation error:', error);
      toast.error('Transaction failed');
    } finally {
      setIsCreating(false);
    }
  };

  const handleVote = async (proposalId: number, inFavor: boolean) => {
    if (!selectedAccount) {
      toast.error('Please connect your wallet first');
      return;
    }

    setIsVoting(true);

    try {
      const result = await voteOnProposal(proposalId, inFavor, selectedAccount);

      if (result.success) {
        toast.success(`Vote cast: ${inFavor ? 'YES' : 'NO'}`, {
          description: `Transaction: ${result.txHash?.slice(0, 10)}...`,
        });
        
        // Reload proposals
        setTimeout(loadProposals, 2000);
      } else {
        toast.error('Vote failed', {
          description: result.error,
        });
      }
    } catch (error) {
      console.error('Vote error:', error);
      toast.error('Vote transaction failed');
    } finally {
      setIsVoting(false);
    }
  };

  const getApprovalPercentage = (proposal: Proposal) => {
    if (proposal.totalVotes === 0) return 0;
    return Math.round((proposal.votesFor / proposal.totalVotes) * 100);
  };

  const getStatusBadge = (status: string) => {
    const statusLower = status.toLowerCase();
    
    if (statusLower === 'active') {
      return <Badge variant="default">Active</Badge>;
    } else if (statusLower === 'approved') {
      return <Badge className="bg-green-600">Approved</Badge>;
    } else if (statusLower === 'rejected') {
      return <Badge variant="destructive">Rejected</Badge>;
    } else if (statusLower === 'executed') {
      return <Badge className="bg-blue-600">Executed</Badge>;
    }
    
    return <Badge variant="secondary">{status}</Badge>;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Vote className="h-5 w-5" />
          DAO Governance
        </CardTitle>
        <CardDescription>
          Create proposals and vote on governance decisions
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="create" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="create">Create Proposal</TabsTrigger>
            <TabsTrigger value="vote">Vote on Proposals</TabsTrigger>
          </TabsList>

          {/* Create Proposal Tab */}
          <TabsContent value="create" className="space-y-4">
            <form onSubmit={handleCreateProposal} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">
                  Proposal Title <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="title"
                  placeholder="Approve Q4 Budget"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                  disabled={isCreating}
                  maxLength={256}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">
                  Description <span className="text-destructive">*</span>
                </Label>
                <Textarea
                  id="description"
                  placeholder="Detailed description of the proposal..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                  disabled={isCreating}
                  rows={4}
                  maxLength={2048}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="votingPeriod">Voting Period (blocks)</Label>
                <Input
                  id="votingPeriod"
                  type="number"
                  min="10"
                  max="1000"
                  value={votingPeriod}
                  onChange={(e) => setVotingPeriod(e.target.value)}
                  disabled={isCreating}
                />
                <p className="text-xs text-muted-foreground">
                  Number of blocks for voting (approx. {Math.round(parseInt(votingPeriod) * 6 / 60)} minutes at 6s per block)
                </p>
              </div>

              <Button
                type="submit"
                disabled={isCreating || !selectedAccount}
                className="w-full"
              >
                {isCreating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Proposal...
                  </>
                ) : (
                  <>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Proposal on Blockchain
                  </>
                )}
              </Button>

              {!selectedAccount && (
                <p className="text-sm text-muted-foreground text-center">
                  Please connect your wallet to create proposals
                </p>
              )}
            </form>
          </TabsContent>

          {/* Vote on Proposals Tab */}
          <TabsContent value="vote" className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-sm font-medium">Active Proposals ({proposals.length})</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={loadProposals}
                disabled={isLoadingProposals}
              >
                {isLoadingProposals ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  'Refresh'
                )}
              </Button>
            </div>

            {proposals.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Vote className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No proposals found</p>
                <p className="text-xs">Create the first proposal to get started</p>
              </div>
            ) : (
              <div className="space-y-4">
                {proposals.map((proposal) => {
                  const approvalPct = getApprovalPercentage(proposal);
                  
                  return (
                    <Card key={proposal.id} className="border-2">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <CardTitle className="text-lg">{proposal.title}</CardTitle>
                            <CardDescription className="mt-1">
                              Proposal #{proposal.id} · {getStatusBadge(proposal.status)}
                            </CardDescription>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-muted-foreground">
                          {proposal.description}
                        </p>

                        {/* Voting Progress */}
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-green-600 font-medium">
                              For: {proposal.votesFor}
                            </span>
                            <span className="text-muted-foreground">
                              {approvalPct}% approval
                            </span>
                            <span className="text-destructive font-medium">
                              Against: {proposal.votesAgainst}
                            </span>
                          </div>
                          <Progress value={approvalPct} className="h-2" />
                          <p className="text-xs text-muted-foreground">
                            Total votes: {proposal.totalVotes}
                          </p>
                        </div>

                        {/* Voting Buttons */}
                        {proposal.status.toLowerCase() === 'active' && selectedAccount && (
                          <div className="flex gap-2 pt-2">
                            <Button
                              onClick={() => handleVote(proposal.id, true)}
                              disabled={isVoting}
                              className="flex-1 bg-green-600 hover:bg-green-700"
                            >
                              <CheckCircle className="mr-2 h-4 w-4" />
                              Vote Yes
                            </Button>
                            <Button
                              onClick={() => handleVote(proposal.id, false)}
                              disabled={isVoting}
                              variant="destructive"
                              className="flex-1"
                            >
                              <XCircle className="mr-2 h-4 w-4" />
                              Vote No
                            </Button>
                          </div>
                        )}

                        {proposal.status.toLowerCase() !== 'active' && (
                          <p className="text-sm text-center text-muted-foreground py-2">
                            Voting is closed for this proposal
                          </p>
                        )}

                        {!selectedAccount && (
                          <p className="text-sm text-center text-muted-foreground py-2">
                            Connect wallet to vote
                          </p>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

export default DAOProposal;


use crate::{mock::*, Error, Event, ProposalStatus};
use frame_support::{assert_noop, assert_ok};

#[test]
fn create_proposal_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let title = b"Approve Q4 Budget".to_vec();
        let description = b"Proposal to approve the Q4 2025 budget allocation of $50,000".to_vec();

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            title.clone(),
            description,
            None // Use default voting period
        ));

        // Verify proposal count
        assert_eq!(Dao::proposal_count(), 1);

        // Verify proposal stored
        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.id, 0);
        assert_eq!(proposal.proposer, proposer);
        assert_eq!(proposal.title.to_vec(), title);
        assert_eq!(proposal.status, ProposalStatus::Active);
        assert_eq!(proposal.votes_for, 0);
        assert_eq!(proposal.votes_against, 0);
        assert_eq!(proposal.total_votes, 0);
        assert!(!proposal.executed);

        // Verify event
        System::assert_has_event(
            Event::ProposalCreated {
                proposal_id: 0,
                proposer,
                title,
            }
            .into(),
        );
    });
}

#[test]
fn vote_in_favor_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let voter = 2u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test Proposal".to_vec(),
            b"Test Description".to_vec(),
            None
        ));

        // Vote in favor
        assert_ok!(Dao::vote(RuntimeOrigin::signed(voter), 0, true));

        // Verify vote recorded
        assert_eq!(Dao::get_vote(0, &voter), Some(true));
        assert!(Dao::has_account_voted(0, &voter));

        // Verify vote counts
        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.votes_for, 1);
        assert_eq!(proposal.votes_against, 0);
        assert_eq!(proposal.total_votes, 1);

        // Verify event
        System::assert_has_event(
            Event::VoteCast {
                proposal_id: 0,
                voter,
                in_favor: true,
            }
            .into(),
        );
    });
}

#[test]
fn vote_against_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let voter = 2u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test Proposal".to_vec(),
            b"Test Description".to_vec(),
            None
        ));

        // Vote against
        assert_ok!(Dao::vote(RuntimeOrigin::signed(voter), 0, false));

        // Verify vote recorded
        assert_eq!(Dao::get_vote(0, &voter), Some(false));

        // Verify vote counts
        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.votes_for, 0);
        assert_eq!(proposal.votes_against, 1);
        assert_eq!(proposal.total_votes, 1);
    });
}

#[test]
fn multiple_votes_work() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test Proposal".to_vec(),
            b"Test Description".to_vec(),
            None
        ));

        // Multiple voters
        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(3), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(4), 0, false));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(5), 0, true));

        // Verify vote counts
        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.votes_for, 3);
        assert_eq!(proposal.votes_against, 1);
        assert_eq!(proposal.total_votes, 4);
        assert!(proposal.is_approved());
    });
}

#[test]
fn cannot_vote_twice() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let voter = 2u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test Proposal".to_vec(),
            b"Test Description".to_vec(),
            None
        ));

        // First vote
        assert_ok!(Dao::vote(RuntimeOrigin::signed(voter), 0, true));

        // Second vote should fail
        assert_noop!(
            Dao::vote(RuntimeOrigin::signed(voter), 0, false),
            Error::<Test>::AlreadyVoted
        );
    });
}

#[test]
fn execute_approved_proposal_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let executor = 6u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test Proposal".to_vec(),
            b"Test Description".to_vec(),
            Some(10) // 10 block voting period
        ));

        // Cast votes (3 for, 1 against)
        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(3), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(4), 0, false));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(5), 0, true));

        // Advance blocks past voting period
        System::set_block_number(11);

        // Execute proposal
        assert_ok!(Dao::execute_proposal(RuntimeOrigin::signed(executor), 0));

        // Verify proposal executed
        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Executed);
        assert!(proposal.executed);
        assert_eq!(proposal.executed_at, Some(11));

        // Verify event
        System::assert_has_event(
            Event::ProposalExecuted {
                proposal_id: 0,
                executor,
            }
            .into(),
        );
    });
}

#[test]
fn cannot_execute_before_voting_ends() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create proposal with 10 block voting period
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test Proposal".to_vec(),
            b"Test Description".to_vec(),
            Some(10)
        ));

        // Vote
        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, true));

        // Try to execute before voting ends (current block = 1)
        assert_noop!(
            Dao::execute_proposal(RuntimeOrigin::signed(proposer), 0),
            Error::<Test>::VotingPeriodNotEnded
        );
    });
}

#[test]
fn cannot_execute_rejected_proposal() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test Proposal".to_vec(),
            b"Test Description".to_vec(),
            Some(10)
        ));

        // Vote against (2 against, 1 for)
        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, false));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(3), 0, false));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(4), 0, true));

        // Advance blocks
        System::set_block_number(11);

        // Try to execute rejected proposal
        assert_noop!(
            Dao::execute_proposal(RuntimeOrigin::signed(proposer), 0),
            Error::<Test>::ProposalNotApproved
        );
    });
}

#[test]
fn close_proposal_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test Proposal".to_vec(),
            b"Test Description".to_vec(),
            Some(10)
        ));

        // Vote (2 for, 1 against = approved)
        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(3), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(4), 0, false));

        // Advance blocks
        System::set_block_number(11);

        // Close proposal
        assert_ok!(Dao::close_proposal(RuntimeOrigin::signed(5), 0));

        // Verify status
        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Approved);

        // Verify events
        System::assert_has_event(
            Event::VotingEnded {
                proposal_id: 0,
                approved: true,
            }
            .into(),
        );

        System::assert_has_event(
            Event::ProposalClosed {
                proposal_id: 0,
                final_status: ProposalStatus::Approved,
            }
            .into(),
        );
    });
}

#[test]
fn close_rejected_proposal_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test Proposal".to_vec(),
            b"Test Description".to_vec(),
            Some(10)
        ));

        // Vote (1 for, 2 against = rejected)
        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(3), 0, false));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(4), 0, false));

        // Advance blocks
        System::set_block_number(11);

        // Close proposal
        assert_ok!(Dao::close_proposal(RuntimeOrigin::signed(5), 0));

        // Verify status
        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Rejected);
    });
}

#[test]
fn full_proposal_lifecycle_approved() {
    new_test_ext().execute_with(|| {
        // Phase 1: Create proposal
        let proposer = 1u64;
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Increase Budget".to_vec(),
            b"Proposal to increase engineering budget by 20%".to_vec(),
            Some(20)
        ));

        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Active);

        // Phase 2: Voting
        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(3), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(4), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(5), 0, false));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(6), 0, true));

        // Verify votes (4 for, 1 against)
        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.votes_for, 4);
        assert_eq!(proposal.votes_against, 1);
        assert_eq!(proposal.approval_percentage(), 80);

        // Phase 3: Close voting
        System::set_block_number(21);
        assert_ok!(Dao::close_proposal(RuntimeOrigin::signed(7), 0));

        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Approved);

        // Phase 4: Execute
        assert_ok!(Dao::execute_proposal(RuntimeOrigin::signed(8), 0));

        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Executed);
        assert!(proposal.executed);
    });
}

#[test]
fn full_proposal_lifecycle_rejected() {
    new_test_ext().execute_with(|| {
        // Create proposal
        let proposer = 1u64;
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Bad Proposal".to_vec(),
            b"This proposal will be rejected".to_vec(),
            Some(15)
        ));

        // Voting (1 for, 3 against = rejected)
        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(3), 0, false));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(4), 0, false));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(5), 0, false));

        // Close voting
        System::set_block_number(16);
        assert_ok!(Dao::close_proposal(RuntimeOrigin::signed(6), 0));

        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Rejected);
        assert!(!proposal.is_approved());

        // Cannot execute rejected proposal
        assert_noop!(
            Dao::execute_proposal(RuntimeOrigin::signed(proposer), 0),
            Error::<Test>::ProposalNotApproved
        );
    });
}

#[test]
fn multiple_proposals_work() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create multiple proposals
        for i in 0..5 {
            assert_ok!(Dao::create_proposal(
                RuntimeOrigin::signed(proposer),
                format!("Proposal {}", i).as_bytes().to_vec(),
                format!("Description {}", i).as_bytes().to_vec(),
                None
            ));
        }

        // Verify count
        assert_eq!(Dao::proposal_count(), 5);

        // Verify all stored
        for i in 0..5 {
            let proposal = Dao::get_proposal_details(i).unwrap();
            assert_eq!(proposal.id, i);
            assert_eq!(proposal.status, ProposalStatus::Active);
        }
    });
}

#[test]
fn cannot_vote_on_nonexistent_proposal() {
    new_test_ext().execute_with(|| {
        let voter = 1u64;

        // Try to vote on non-existent proposal
        assert_noop!(
            Dao::vote(RuntimeOrigin::signed(voter), 999, true),
            Error::<Test>::ProposalNotFound
        );
    });
}

#[test]
fn approval_percentage_calculation_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test".to_vec(),
            b"Test".to_vec(),
            None
        ));

        // Cast votes (6 for, 4 against = 60% approval)
        for i in 2..8 {
            assert_ok!(Dao::vote(RuntimeOrigin::signed(i), 0, true));
        }
        for i in 8..12 {
            assert_ok!(Dao::vote(RuntimeOrigin::signed(i), 0, false));
        }

        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.approval_percentage(), 60);
    });
}

#[test]
fn cancel_proposal_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test".to_vec(),
            b"Test".to_vec(),
            None
        ));

        // Cancel proposal
        assert_ok!(Dao::cancel_proposal(RuntimeOrigin::signed(proposer), 0));

        // Verify status
        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.status, ProposalStatus::Cancelled);
    });
}

#[test]
fn only_proposer_can_cancel() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let other = 2u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test".to_vec(),
            b"Test".to_vec(),
            None
        ));

        // Try to cancel from different account
        assert_noop!(
            Dao::cancel_proposal(RuntimeOrigin::signed(other), 0),
            Error::<Test>::ProposalNotActive
        );
    });
}

#[test]
fn cannot_execute_twice() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create and approve proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test".to_vec(),
            b"Test".to_vec(),
            Some(10)
        ));

        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(3), 0, true));

        System::set_block_number(11);

        // Execute once
        assert_ok!(Dao::execute_proposal(RuntimeOrigin::signed(proposer), 0));

        // Try to execute again
        assert_noop!(
            Dao::execute_proposal(RuntimeOrigin::signed(proposer), 0),
            Error::<Test>::AlreadyExecuted
        );
    });
}

#[test]
fn title_too_long_fails() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let long_title = vec![0u8; 257]; // Exceeds MaxTitleLength (256)

        assert_noop!(
            Dao::create_proposal(
                RuntimeOrigin::signed(proposer),
                long_title,
                b"Description".to_vec(),
                None
            ),
            Error::<Test>::TitleTooLong
        );
    });
}

#[test]
fn description_too_long_fails() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let long_desc = vec![0u8; 2049]; // Exceeds MaxDescriptionLength (2048)

        assert_noop!(
            Dao::create_proposal(
                RuntimeOrigin::signed(proposer),
                b"Title".to_vec(),
                long_desc,
                None
            ),
            Error::<Test>::DescriptionTooLong
        );
    });
}

#[test]
fn voting_period_validation_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Too short (< MinVotingPeriod = 10)
        assert_noop!(
            Dao::create_proposal(
                RuntimeOrigin::signed(proposer),
                b"Test".to_vec(),
                b"Test".to_vec(),
                Some(5)
            ),
            Error::<Test>::InvalidVotingPeriod
        );

        // Too long (> MaxVotingPeriod = 1000)
        assert_noop!(
            Dao::create_proposal(
                RuntimeOrigin::signed(proposer),
                b"Test".to_vec(),
                b"Test".to_vec(),
                Some(1001)
            ),
            Error::<Test>::InvalidVotingPeriod
        );

        // Valid period
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Test".to_vec(),
            b"Test".to_vec(),
            Some(50)
        ));
    });
}

#[test]
fn unanimous_approval_works() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Unanimous".to_vec(),
            b"Test".to_vec(),
            Some(10)
        ));

        // All vote in favor
        for i in 2..10 {
            assert_ok!(Dao::vote(RuntimeOrigin::signed(i), 0, true));
        }

        let proposal = Dao::get_proposal_details(0).unwrap();
        assert_eq!(proposal.votes_for, 8);
        assert_eq!(proposal.votes_against, 0);
        assert_eq!(proposal.approval_percentage(), 100);
        assert!(proposal.is_approved());
    });
}

#[test]
fn tie_vote_rejects_proposal() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            b"Tie Vote".to_vec(),
            b"Test".to_vec(),
            Some(10)
        ));

        // Equal votes (2 for, 2 against)
        assert_ok!(Dao::vote(RuntimeOrigin::signed(2), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(3), 0, true));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(4), 0, false));
        assert_ok!(Dao::vote(RuntimeOrigin::signed(5), 0, false));

        let proposal = Dao::get_proposal_details(0).unwrap();
        assert!(!proposal.is_approved()); // Tie means not approved (needs majority)
    });
}

#[test]
fn events_are_emitted_correctly() {
    new_test_ext().execute_with(|| {
        let proposer = 1u64;
        let voter = 2u64;
        let title = b"Test Proposal".to_vec();

        // Create proposal
        assert_ok!(Dao::create_proposal(
            RuntimeOrigin::signed(proposer),
            title.clone(),
            b"Description".to_vec(),
            Some(10)
        ));

        // Check ProposalCreated event
        System::assert_has_event(
            Event::ProposalCreated {
                proposal_id: 0,
                proposer,
                title,
            }
            .into(),
        );

        // Vote
        assert_ok!(Dao::vote(RuntimeOrigin::signed(voter), 0, true));

        // Check VoteCast event
        System::assert_has_event(
            Event::VoteCast {
                proposal_id: 0,
                voter,
                in_favor: true,
            }
            .into(),
        );
    });
}


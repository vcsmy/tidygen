import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import FreelancerProfile from '@/components/freelancers/FreelancerProfile';

// Mock the API fetch
global.fetch = vi.fn();

const mockFreelancer = {
  id: '1',
  freelancer_id: 'FL12345678',
  first_name: 'John',
  last_name: 'Freelancer',
  city: 'New York',
  state: 'NY',
  rating: 4.8,
  total_jobs_completed: 25,
  on_time_percentage: 95,
  completion_rate: 98,
  hourly_rate: 30,
  currency: 'USD',
  cleaning_types: ['residential', 'commercial'],
  special_skills: 'Deep cleaning and eco-friendly products',
  years_of_experience: 5,
  profile_picture: 'https://example.com/profile.jpg',
  wallet_address: '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
  blockchain_verified: true,
  status: 'active',
  bio: 'Experienced cleaner with 5+ years in residential and commercial cleaning.',
  documents: [],
  availability_slots: [],
  skill_assignments: [
    {
      skill: {
        name: 'Deep Cleaning',
        category: 'cleaning'
      },
      proficiency_level: 'advanced',
      years_of_experience: 3
    }
  ],
  reviews: [
    {
      id: '1',
      title: 'Excellent work!',
      comment: 'Very thorough and professional.',
      overall_rating: 5,
      reviewer_name: 'Jane Client',
      created: '2024-01-15T10:00:00Z'
    }
  ]
};

describe('FreelancerProfile', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock successful API response
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockFreelancer),
    });
  });

  it('renders freelancer profile information correctly', async () => {
    render(<FreelancerProfile freelancerId="1" />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    // Check basic information
    expect(screen.getByText('New York, NY')).toBeInTheDocument();
    expect(screen.getByText('$30/USD')).toBeInTheDocument();
    expect(screen.getByText('5 years experience')).toBeInTheDocument();
    
    // Check ratings and stats
    expect(screen.getByText('4.8')).toBeInTheDocument();
    expect(screen.getByText('(1 reviews)')).toBeInTheDocument();
    expect(screen.getByText('25 jobs completed')).toBeInTheDocument();
    expect(screen.getByText('95% on time')).toBeInTheDocument();
    expect(screen.getByText('98% completion rate')).toBeInTheDocument();
  });

  it('displays correct status badge', async () => {
    render(<FreelancerProfile freelancerId="1" />);

    await waitFor(() => {
      expect(screen.getByText('active')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Verified')).toBeInTheDocument();
  });

  it('navigates between tabs correctly', async () => {
    render(<FreelancerProfile freelancerId="1" />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    // Check that Overview tab is active by default
    expect(screen.getByText('About')).toBeInTheDocument();

    // Click Skills tab
    fireEvent.click(screen.getByRole('tab', { name: 'Skills' }));
    expect(screen.getByText('Skills & Certifications')).toBeInTheDocument();

    // Click Availability tab
    fireEvent.click(screen.getByRole('tab', { name: 'Availability' }));
    expect(screen.getByText('Availability Schedule')).toBeInTheDocument();

    // Click Reviews tab
    fireEvent.click(screen.getByRole('tab', { name: 'Reviews' }));
    expect(screen.getByText('Client Reviews')).toBeInTheDocument();

    // Click Web3 tab
    fireEvent.click(screen.getByRole('tab', { name: 'Web3' }));
    expect(screen.getByText('Web3 Integration')).toBeInTheDocument();
  });

  it('displays cleaning types and special skills', async () => {
    render(<FreelancerProfile freelancerId="1" />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    // Check services section
    expect(screen.getByText('Services')).toBeInTheDocument();
    expect(screen.getByText('residential')).toBeInTheDocument();
    expect(screen.getByText('commercial')).toBeInTheDocument();

    // Check special skills
    expect(screen.getByText('Special Skills')).toBeInTheDocument();
    expect(screen.getByText('Deep cleaning and eco-friendly products')).toBeInTheDocument();
  });

  it('displays reviews correctly', async () => {
    render(<FreelancerProfile freelancerId="1" />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    // Navigate to reviews tab
    fireEvent.click(screen.getByRole('tab', { name: 'Reviews' }));

    await waitFor(() => {
      expect(screen.getByText('Client Reviews')).toBeInTheDocument();
    });

    expect(screen.getByText('Excellent work!')).toBeInTheDocument();
    expect(screen.getByText('Very thorough and professional.')).toBeInTheDocument();
    expect(screen.getByText('Jane Client')).toBeInTheDocument();
  });

  it('displays Web3 information correctly', async () => {
    render(<FreelancerProfile freelancerId="1" />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    // Navigate to Web3 tab
    fireEvent.click(screen.getByRole('tab', { name: 'Web3' }));

    await waitFor(() => {
      expect(screen.getByText('Web3 Integration')).toBeInTheDocument();
    });

    expect(screen.getByText('Blockchain Verification:')).toBeInTheDocument();
    expect(screen.getByText('Verified')).toBeInTheDocument();
    expect(screen.getByText('Wallet Address:')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(<FreelancerProfile freelancerId="1" />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows error message when freelancer not found', async () => {
    // Mock API error
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    render(<FreelancerProfile freelancerId="999" />);

    await waitFor(() => {
      expect(screen.getByText('Freelancer profile not found.')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock API error
    (global.fetch as any).mockRejectedValueOnce(new Error('API Error'));

    render(<FreelancerProfile freelancerId="1" />);

    await waitFor(() => {
      expect(screen.getByText('Freelancer profile not found.')).toBeInTheDocument();
    });
  });

  it('displays action buttons', async () => {
    render(<FreelancerProfile freelancerId="1" />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: 'Contact' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'View Reviews' })).toBeInTheDocument();
  });
});

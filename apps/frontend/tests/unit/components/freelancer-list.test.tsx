import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import FreelancerList from '@/components/freelancers/FreelancerList';

// Mock the API fetch
global.fetch = vi.fn();

const mockFreelancers = [
  {
    id: '1',
    freelancer_id: 'FL12345678',
    full_name: 'John Freelancer',
    city_state: 'New York, NY',
    rating: 4.8,
    total_jobs_completed: 25,
    cleaning_types: ['residential', 'commercial'],
    hourly_rate: 30,
    currency: 'USD',
    is_available: true,
    status: 'active',
    profile_picture: 'https://example.com/profile1.jpg'
  },
  {
    id: '2',
    freelancer_id: 'FL87654321',
    full_name: 'Jane Cleaner',
    city_state: 'Los Angeles, CA',
    rating: 4.6,
    total_jobs_completed: 18,
    cleaning_types: ['commercial'],
    hourly_rate: 35,
    currency: 'USD',
    is_available: false,
    status: 'active',
    profile_picture: 'https://example.com/profile2.jpg'
  }
];

describe('FreelancerList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock successful API response
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        results: mockFreelancers,
        count: mockFreelancers.length
      }),
    });
  });

  it('renders freelancer list header correctly', async () => {
    render(<FreelancerList />);

    expect(screen.getByRole('heading', { name: 'Find Freelancers' })).toBeInTheDocument();
    expect(screen.getByText('Browse available domestic cleaners and contractors')).toBeInTheDocument();
  });

  it('renders search and filter components', async () => {
    render(<FreelancerList />);

    expect(screen.getByPlaceholderText(/Search by name, skills, or location/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
    expect(screen.getByLabelText('City')).toBeInTheDocument();
    expect(screen.getByLabelText('Service Type')).toBeInTheDocument();
  });

  it('displays freelancer cards', async () => {
    render(<FreelancerList />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    expect(screen.getByText('New York, NY')).toBeInTheDocument();
    expect(screen.getByText('4.8')).toBeInTheDocument();
    expect(screen.getByText('25 jobs completed')).toBeInTheDocument();
    expect(screen.getByText('Available')).toBeInTheDocument();
  });

  it('displays multiple freelancers correctly', async () => {
    render(<FreelancerList />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    expect(screen.getByText('Jane Cleaner')).toBeInTheDocument();
    expect(screen.getByText('Los Angeles, CA')).toBeInTheDocument();
    expect(screen.getByText('Busy')).toBeInTheDocument();
  });

  it('handles search input correctly', async () => {
    render(<FreelancerList />);

    const searchInput = screen.getByPlaceholderText(/Search by name, skills, or location/i);
    const searchButton = screen.getByRole('button', { name: 'Search' });

    fireEvent.change(searchInput, { target: { value: 'John' } });
    fireEvent.click(searchButton);

    // Should trigger new API call
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('?search=John'),
        expect.any(Object)
      );
    });
  });

  it('handles city filter correctly', async () => {
    render(<FreelancerList />);

    const cityInput = screen.getByLabelText('City');
    const searchButton = screen.getByRole('button', { name: 'Search' });

    fireEvent.change(cityInput, { target: { value: 'New York' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('&city=New York'),
        expect.any(Object)
      );
    });
  });

  it('handles rating filter correctly', async () => {
    render(<FreelancerList />);

    const ratingSelect = screen.getByLabelText('Min Rating');
    fireEvent.change(ratingSelect, { target: { value: '4' } });

    const searchButton = screen.getByRole('button', { name: 'Search' });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('&min_rating=4'),
        expect.any(Object)
      );
    });
  });

  it('handles service type filter correctly', async () => {
    render(<FreelancerList />);

    const serviceTypeSelect = screen.getByLabelText('Service Type');
    fireEvent.change(serviceTypeSelect, { target: { value: 'residential' } });

    const searchButton = screen.getByRole('button', { name: 'Search' });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('&cleaning_type=residential'),
        expect.any(Object)
      );
    });
  });

  it('shows loading state initially', () => {
    render(<FreelancerList />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows no results message when no freelancers found', async () => {
    // Mock empty API response
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ results: [], count: 0 }),
    });

    render(<FreelancerList />);

    await waitFor(() => {
      expect(screen.getByText('No freelancers found')).toBeInTheDocument();
    });
    expect(screen.getByText('Try adjusting your search criteria or filters.')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('API Error'));

    render(<FreelancerList />);

    // Should still show the interface even if API fails
    expect(screen.getByRole('heading', { name: 'Find Freelancers' })).toBeInTheDocument();
  });

  it('displays freelancer service badges correctly', async () => {
    render(<FreelancerList />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    // Check that service badges are displayed
    expect(screen.getByText('residential')).toBeInTheDocument();
    expect(screen.getByText('commercial')).toBeInTheDocument();
  });

  it('shows correct availability status', async () => {
    render(<FreelancerList />);

    await waitFor(() => {
      expect(screen.getByText('Available')).toBeInTheDocument();
    });
    expect(screen.getByText('Busy')).toBeInTheDocument();
  });

  it('has correct action buttons on each card', async () => {
    render(<FreelancerList />);

    await waitFor(() => {
      expect(screen.getByText('John Freelancer')).toBeInTheDocument();
    });

    expect(screen.getAllByRole('button', { name: 'View Profile' })).toHaveLength(2);
    expect(screen.getAllByRole('button', { name: 'Contact' })).toHaveLength(2);
  });
});

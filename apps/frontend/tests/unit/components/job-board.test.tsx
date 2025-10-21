import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import JobBoard from '@/components/gig-management/JobBoard';

// Mock the API fetch
global.fetch = vi.fn();

const mockJobs = [
  {
    id: '1',
    job_id: 'GIG12345678',
    title: 'Weekly House Cleaning',
    description: 'Regular weekly cleaning for 3-bedroom house',
    category_name: 'Residential Cleaning',
    city_state: 'New York, NY',
    service_type: 'regular_cleaning',
    property_type: 'house',
    preferred_start_date: '2024-01-20',
    estimated_duration_hours: 4,
    payment_method: 'hourly',
    hourly_rate: 35,
    currency: 'USD',
    total_cost: 140,
    status: 'published',
    priority: 'medium',
    client_name: 'Jane Client',
    created: '2024-01-15T10:00:00Z'
  },
  {
    id: '2',
    job_id: 'GIG87654321',
    title: 'Office Deep Clean',
    description: 'Deep cleaning for office space',
    category_name: 'Commercial Cleaning',
    city_state: 'Los Angeles, CA',
    service_type: 'deep_cleaning',
    property_type: 'office',
    preferred_start_date: '2024-01-22',
    estimated_duration_hours: 8,
    payment_method: 'fixed',
    fixed_price: 500,
    currency: 'USD',
    total_cost: 500,
    status: 'published',
    priority: 'high',
    client_name: 'ABC Company',
    created: '2024-01-16T09:00:00Z'
  }
];

describe('JobBoard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock successful API response
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        results: mockJobs,
        count: mockJobs.length
      }),
    });
  });

  it('renders job board header correctly', async () => {
    render(<JobBoard />);

    expect(screen.getByRole('heading', { name: 'Job Board' })).toBeInTheDocument();
    expect(screen.getByText('Find cleaning and maintenance jobs in your area')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Post Job' })).toBeInTheDocument();
  });

  it('renders search and filter components', async () => {
    render(<JobBoard />);

    expect(screen.getByPlaceholderText(/Search jobs by title/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Search' })).toBeInTheDocument();
    expect(screen.getByLabelText('Category')).toBeInTheDocument();
    expect(screen.getByLabelText('City')).toBeInTheDocument();
    expect(screen.getByLabelText('Payment Method')).toBeInTheDocument();
    expect(screen.getByLabelText('Status')).toBeInTheDocument();
    expect(screen.getByLabelText('Max Rate')).toBeInTheDocument();
  });

  it('displays job cards correctly', async () => {
    render(<JobBoard />);

    await waitFor(() => {
      expect(screen.getByText('Weekly House Cleaning')).toBeInTheDocument();
    });

    expect(screen.getByText('Regular weekly cleaning for 3-bedroom house')).toBeInTheDocument();
    expect(screen.getByText('Jane Client')).toBeInTheDocument();
    expect(screen.getByText('New York, NY')).toBeInTheDocument();
    expect(screen.getByText('4h estimated')).toBeInTheDocument();
    expect(screen.getByText('Posted Jan 15, 2024')).toBeInTheDocument();
  });

  it('displays multiple jobs correctly', async () => {
    render(<JobBoard />);

    await waitFor(() => {
      expect(screen.getByText('Weekly House Cleaning')).toBeInTheDocument();
    });

    expect(screen.getByText('Office Deep Clean')).toBeInTheDocument();
    expect(screen.getByText('ABC Company')).toBeInTheDocument();
    expect(screen.getByText('Los Angeles, CA')).toBeInTheDocument();
  });

  it('displays correct status and priority badges', async () => {
    render(<JobBoard />);

    await waitFor(() => {
      expect(screen.getByText('published')).toBeInTheDocument();
    });

    expect(screen.getByText('medium priority')).toBeInTheDocument();
    expect(screen.getByText('high priority')).toBeInTheDocument();
  });

  it('displays payment information correctly', async () => {
    render(<JobBoard />);

    await waitFor(() => {
      expect(screen.getByText('$140')).toBeInTheDocument();
    });

    expect(screen.getByText('/hour')).toBeInTheDocument();
    expect(screen.getByText('$500')).toBeInTheDocument();
  });

  it('handles search input correctly', async () => {
    render(<JobBoard />);

    const searchInput = screen.getByPlaceholderText(/Search jobs by title/i);
    const searchButton = screen.getByRole('button', { name: 'Search' });

    fireEvent.change(searchInput, { target: { value: 'cleaning' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('?search=cleaning'),
        expect.any(Object)
      );
    });
  });

  it('handles category filter correctly', async () => {
    render(<JobBoard />);

    const categorySelect = screen.getByLabelText('Category');
    fireEvent.change(categorySelect, { target: { value: 'residential_cleaning' } });

    const searchButton = screen.getByRole('button', { name: 'Search' });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('&category=residential_cleaning'),
        expect.any(Object)
      );
    });
  });

  it('handles city filter correctly', async () => {
    render(<JobBoard />);

    const cityInput = screen.getByLabelText('City');
    fireEvent.change(cityInput, { target: { value: 'New York' } });

    const searchButton = screen.getByRole('button', { name: 'Search' });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('&city=New York'),
        expect.any(Object)
      );
    });
  });

  it('handles payment method filter correctly', async () => {
    render(<JobBoard />);

    const paymentSelect = screen.getByLabelText('Payment Method');
    fireEvent.change(paymentSelect, { target: { value: 'hourly' } });

    const searchButton = screen.getByRole('button', { name: 'Search' });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('&payment_method=hourly'),
        expect.any(Object)
      );
    });
  });

  it('handles status filter correctly', async () => {
    render(<JobBoard />);

    const statusSelect = screen.getByLabelText('Status');
    fireEvent.change(statusSelect, { target: { value: 'published' } });

    const searchButton = screen.getByRole('button', { name: 'Search' });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('&status=published'),
        expect.any(Object)
      );
    });
  });

  it('shows loading state initially', () => {
    render(<JobBoard />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows no results message when no jobs found', async () => {
    // Mock empty API response
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ results: [], count: 0 }),
    });

    render(<JobBoard />);

    await waitFor(() => {
      expect(screen.getByText('No jobs found')).toBeInTheDocument();
    });
    expect(screen.getByText('Try adjusting your search criteria or check back later.')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('API Error'));

    render(<JobBoard />);

    // Should still show the interface even if API fails
    expect(screen.getByRole('heading', { name: 'Job Board' })).toBeInTheDocument();
  });

  it('displays action buttons on job cards', async () => {
    render(<JobBoard />);

    await waitFor(() => {
      expect(screen.getByText('Weekly House Cleaning')).toBeInTheDocument();
    });

    expect(screen.getAllByRole('button', { name: 'View Details' })).toHaveLength(2);
    expect(screen.getAllByRole('button', { name: 'Apply Now' })).toHaveLength(2);
  });

  it('formats dates correctly', async () => {
    render(<JobBoard />);

    await waitFor(() => {
      expect(screen.getByText('Posted Jan 15, 2024')).toBeInTheDocument();
    });
  });
});

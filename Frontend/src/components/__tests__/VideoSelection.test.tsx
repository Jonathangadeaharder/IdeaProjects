import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { VideoSelection } from '../VideoSelection';
import * as api from '@/services/api';

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockVideos = [
  {
    series: 'Superstore',
    season: '01',
    episode: '01',
    title: 'Pilot',
    path: '/videos/superstore/s01e01.mp4',
    has_subtitles: true,
    duration: 1800,
  },
  {
    series: 'Superstore',
    season: '01',
    episode: '02',
    title: 'Magazine Profile',
    path: '/videos/superstore/s01e02.mp4',
    has_subtitles: false,
    duration: 1850,
  },
];

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('VideoSelection Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(api.videoService, 'getVideos').mockResolvedValue(mockVideos as any);
  });

  it('renders hero title', async () => {
    renderWithRouter(<VideoSelection />);
    expect(screen.getByText(/learn german through tv shows/i)).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    renderWithRouter(<VideoSelection />);
    // Loading spinner is a div with className "loading-spinner"
    expect(document.querySelector('.loading-spinner')).toBeTruthy();
  });

  it('displays series after loading', async () => {
    renderWithRouter(<VideoSelection />);
    
    await waitFor(() => {
      // Series card displays the series name
      expect(screen.getByText('Superstore')).toBeInTheDocument();
    });
  });

  it('navigates to episodes page when series clicked', async () => {
    renderWithRouter(<VideoSelection />);
    
    await waitFor(() => {
      expect(screen.getByText('Superstore')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Superstore'));
    expect(mockNavigate).toHaveBeenCalledWith('/episodes/Superstore');
  });

  it('handles API error gracefully', async () => {
    vi.spyOn(api.videoService, 'getVideos').mockRejectedValue(new Error('API Error'));
    
    renderWithRouter(<VideoSelection />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load videos')).toBeInTheDocument();
    });
  });
});
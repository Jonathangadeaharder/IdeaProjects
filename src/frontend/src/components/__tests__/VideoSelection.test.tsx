import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { VideoSelection } from '../VideoSelection';
import * as sdk from '@/client/services.gen';
import { assertLoadingState, assertNavigationCalled } from '@/test/assertion-helpers';

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
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      {component}
    </BrowserRouter>
  );
};

describe('VideoSelection Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(sdk, 'getVideosApiVideosGet').mockResolvedValue(mockVideos as any);
  });

  it('WhenComponentRendered_ThenDisplaysHeroTitle', async () => {
    await act(async () => {
      renderWithRouter(<VideoSelection />);
    });
    expect(screen.getByText(/learn german through tv shows/i)).toBeInTheDocument();
  });

  it('WhenComponentMounts_ThenShowsLoadingState', () => {
    renderWithRouter(<VideoSelection />);
    assertLoadingState();
  });

  it('WhenDataLoaded_ThenDisplaysSeries', async () => {
    await act(async () => {
      renderWithRouter(<VideoSelection />);
    });

    await waitFor(() => {
      expect(screen.getByText('Superstore')).toBeInTheDocument();
    });
  });

  it('WhenSeriesClicked_ThenNavigatesToEpisodes', async () => {
    await act(async () => {
      renderWithRouter(<VideoSelection />);
    });

    await waitFor(() => {
      expect(screen.getByText('Superstore')).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Superstore'));
    });
    assertNavigationCalled(mockNavigate, '/episodes/Superstore');
  });

  it('WhenProfileButtonClicked_ThenNavigatesToProfile', async () => {
    await act(async () => {
      renderWithRouter(<VideoSelection />);
    });

    await waitFor(() => {
      expect(screen.getByTestId('profile-button')).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId('profile-button'));
    });

    assertNavigationCalled(mockNavigate, '/profile');
  });

  it('WhenApiErrorOccurs_ThenHandlesErrorGracefully', async () => {
    vi.spyOn(sdk, 'getVideosApiVideosGet').mockRejectedValueOnce(new Error('API Error'));

    await act(async () => {
      renderWithRouter(<VideoSelection />);
    });

    await waitFor(() => {
      expect(sdk.getVideosApiVideosGet).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText('Failed to load videos')).toBeInTheDocument();
    });
  });
});

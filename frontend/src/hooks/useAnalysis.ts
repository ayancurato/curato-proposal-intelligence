/**
 * Custom hook for polling analysis status and fetching results.
 */

import { useQuery } from '@tanstack/react-query';
import { getAnalysis, getSessionStatus, type DashboardResponse, type UploadResponse } from '../services/api';

export function useAnalysis(sessionId: string | undefined) {
  const statusQuery = useQuery<UploadResponse>({
    queryKey: ['analysis-status', sessionId],
    queryFn: () => getSessionStatus(sessionId!),
    enabled: !!sessionId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      // Stop polling when completed or failed
      if (status === 'completed' || status === 'failed') return false;
      return 2000; // Poll every 2 seconds during processing
    },
  });

  const dashboardQuery = useQuery<DashboardResponse>({
    queryKey: ['dashboard', sessionId],
    queryFn: () => getAnalysis(sessionId!),
    enabled: !!sessionId && statusQuery.data?.status === 'completed',
  });

  return {
    // Status polling
    status: statusQuery.data?.status || null,
    statusMessage: statusQuery.data?.status_message || null,
    isPolling: statusQuery.isFetching && statusQuery.data?.status !== 'completed',

    // Dashboard data
    dashboard: dashboardQuery.data || null,
    isDashboardLoading: dashboardQuery.isLoading,
    dashboardError: dashboardQuery.error,

    // Combined state
    isComplete: statusQuery.data?.status === 'completed',
    isFailed: statusQuery.data?.status === 'failed',
    isProcessing: !['completed', 'failed', 'created'].includes(statusQuery.data?.status || ''),

    refetchDashboard: dashboardQuery.refetch,
  };
}

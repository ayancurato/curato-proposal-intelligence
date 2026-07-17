/**
 * Custom hook for file upload with TanStack Query mutation.
 */

import { useMutation } from '@tanstack/react-query';
import { uploadProposals, startAnalysis, type UploadResponse } from '../services/api';

export function useUpload() {
  const uploadMutation = useMutation({
    mutationFn: (files: File[]) => uploadProposals(files),
  });

  const analyzeMutation = useMutation({
    mutationFn: (sessionId: string) => startAnalysis(sessionId),
  });

  return {
    upload: uploadMutation.mutate,
    uploadAsync: uploadMutation.mutateAsync,
    isUploading: uploadMutation.isPending,
    uploadData: uploadMutation.data,
    uploadError: uploadMutation.error,

    startAnalysis: analyzeMutation.mutate,
    startAnalysisAsync: analyzeMutation.mutateAsync,
    isStartingAnalysis: analyzeMutation.isPending,

    reset: () => {
      uploadMutation.reset();
      analyzeMutation.reset();
    },
  };
}

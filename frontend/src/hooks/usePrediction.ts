import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createPrediction } from "../api/client";
import type { PredictionRequest } from "../types/prediction";

type PredictionMutationInput = PredictionRequest & { authToken: string };

export function usePrediction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ authToken, ...body }: PredictionMutationInput) =>
      createPrediction(body, authToken),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["predictions", "history"] });
    },
  });
}

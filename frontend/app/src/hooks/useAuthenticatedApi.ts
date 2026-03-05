'use client';

import { useCallback } from 'react';
import { useAuth } from './useAuth';

type FetchOptions = Omit<RequestInit, 'body'> & { body?: BodyInit | Record<string, unknown> | null };

export function useAuthenticatedApi() {
  const { token, refresh } = useAuth();

  const authenticatedFetch = useCallback(
    async (url: string, options: FetchOptions = {}): Promise<Response> => {
      const { body, headers: extraHeaders, ...rest } = options;

      const buildHeaders = (currentToken: string | null): HeadersInit => {
        const h: Record<string, string> = {
          ...(extraHeaders as Record<string, string>),
          ...(currentToken ? { Authorization: `Bearer ${currentToken}` } : {}),
        };
        if (body && !(body instanceof FormData) && typeof body === 'object') {
          h['Content-Type'] = 'application/json';
        }
        return h;
      };

      const buildBody = (): BodyInit | null | undefined => {
        if (!body) return undefined;
        if (body instanceof FormData) return body;
        if (typeof body === 'object') return JSON.stringify(body);
        return body as BodyInit;
      };

      let response = await fetch(url, {
        ...rest,
        headers: buildHeaders(token),
        body: buildBody(),
        credentials: 'include',
      });

      if (response.status === 401) {
        try {
          const newToken = await refresh();
          response = await fetch(url, {
            ...rest,
            headers: buildHeaders(newToken),
            body: buildBody(),
            credentials: 'include',
          });
        } catch {
          throw new Error('Session expired. Please log in again.');
        }
      }

      return response;
    },
    [token, refresh],
  );

  return { authenticatedFetch };
}

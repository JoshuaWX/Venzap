'use client';

import { useEffect } from 'react';
import { API_BASE_URL } from '@/lib/api';
import type { VendorOrderStreamEvent } from '@/lib/vendor-types';

type Options = {
  onOrderEvent: (event: VendorOrderStreamEvent) => void;
  onError?: () => void;
};

export function useOrderStream({ onOrderEvent, onError }: Options) {
  useEffect(() => {
    const streamUrl = `${API_BASE_URL}/api/v1/vendor/orders/stream`;
    const source = new EventSource(streamUrl, { withCredentials: true });

    const handler = (event: MessageEvent<string>) => {
      try {
        const parsed = JSON.parse(event.data) as VendorOrderStreamEvent;
        onOrderEvent(parsed);
      } catch {
        // ignore malformed event payloads
      }
    };

    source.addEventListener('vendor_orders', handler as EventListener);
    source.onerror = () => {
      if (onError) {
        onError();
      }
    };

    return () => {
      source.removeEventListener('vendor_orders', handler as EventListener);
      source.close();
    };
  }, [onError, onOrderEvent]);
}

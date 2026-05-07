export type VendorProfile = {
  id: string;
  business_name: string;
  email: string;
  phone: string;
  address: string;
  description?: string | null;
  logo_url?: string | null;
  vendor_type: string;
  delivery_fee: string;
  is_active: boolean;
  is_verified: boolean;
  is_open: boolean;
};

export type VendorDashboardStats = {
  orders_today: number;
  revenue_today: string;
  total_orders: number;
  catalogue_items: number;
};

export type CatalogueItem = {
  id: string;
  vendor_id: string;
  name: string;
  description?: string | null;
  price: string;
  emoji?: string | null;
  category?: string | null;
  is_available: boolean;
};

export type OrderItem = {
  name: string;
  price: string;
  quantity: number;
};

export type Order = {
  id: string;
  status: string;
  vendor_id: string;
  vendor_name: string;
  delivery_address: string;
  delivery_fee: string;
  subtotal: string;
  total: string;
  note?: string | null;
  created_at: string;
  items: OrderItem[];
};

export type OrderListResponse = {
  data: Order[];
  page: number;
  page_size: number;
  total: number;
};

export type VendorEarningsResponse = {
  summary: {
    total_earned: string;
    this_month: string;
    pending_escrow: string;
  };
  history: Array<{
    id: string;
    order_id: string;
    amount: string;
    status: string;
    released_at?: string | null;
    created_at: string;
  }>;
};

export type VendorOrderStreamEvent = {
  latest_order_id: string | null;
  latest_order_status: string | null;
  latest_order_total: string | null;
  latest_order_created_at: string | null;
  pending_count: number;
  total_orders: number;
};

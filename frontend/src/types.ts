export type TicketStatus = 'new' | 'in_progress' | 'done';
export type TicketPriority = 'low' | 'normal' | 'high';

export type SortBy = 'created_at' | 'priority';
export type SortOrder = 'asc' | 'desc';

export interface Ticket {
  id: number;
  title: string;
  description: string | null;
  status: TicketStatus;
  priority: TicketPriority;
  created_at: string;
  updated_at: string;
}

export interface PaginatedTicketsResponse {
  items: Ticket[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface TicketCreatePayload {
  title: string;
  description?: string | null;
  priority: TicketPriority;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
}

export interface AdminUser {
  id: number;
  username: string;
  is_admin: boolean;
}

export interface TicketListParams {
  search?: string;
  status?: TicketStatus | '';
  priority?: TicketPriority | '';
  sort_by: SortBy;
  sort_order: SortOrder;
  page: number;
  page_size: number;
}

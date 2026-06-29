import type {
  AdminUser,
  LoginPayload,
  PaginatedTicketsResponse,
  Ticket,
  TicketCreatePayload,
  TicketListParams,
  TicketStatus,
  TokenResponse,
} from './types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(formatErrorDetail(detail));
    this.status = status;
    this.detail = detail;
  }
}

function formatErrorDetail(detail: unknown): string {
  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (
          typeof item === 'object' &&
          item !== null &&
          'msg' in item &&
          typeof item.msg === 'string'
        ) {
          return item.msg;
        }

        return JSON.stringify(item);
      })
      .join('; ');
  }

  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail);
  }

  return 'Unexpected API error.';
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers);

  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type');
  const isJson = contentType?.includes('application/json');
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const detail =
      data && typeof data === 'object' && 'detail' in data ? data.detail : data;

    throw new ApiError(response.status, detail);
  }

  return data as T;
}

export function loginAdmin(payload: LoginPayload): Promise<TokenResponse> {
  return request<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getCurrentAdmin(token: string): Promise<AdminUser> {
  return request<AdminUser>('/auth/me', {}, token);
}

export function getTickets(
  params: TicketListParams,
): Promise<PaginatedTicketsResponse> {
  const searchParams = new URLSearchParams();

  if (params.search?.trim()) {
    searchParams.set('search', params.search.trim());
  }

  if (params.status) {
    searchParams.set('status', params.status);
  }

  if (params.priority) {
    searchParams.set('priority', params.priority);
  }

  searchParams.set('sort_by', params.sort_by);
  searchParams.set('sort_order', params.sort_order);
  searchParams.set('page', String(params.page));
  searchParams.set('page_size', String(params.page_size));

  return request<PaginatedTicketsResponse>(`/tickets?${searchParams.toString()}`);
}

export function createTicket(payload: TicketCreatePayload): Promise<Ticket> {
  return request<Ticket>('/tickets', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateTicketStatus(
  ticketId: number,
  status: TicketStatus,
): Promise<Ticket> {
  return request<Ticket>(`/tickets/${ticketId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export async function deleteTicket(
  ticketId: number,
  token: string,
): Promise<void> {
  await request<void>(
    `/tickets/${ticketId}`,
    {
      method: 'DELETE',
    },
    token,
  );
}

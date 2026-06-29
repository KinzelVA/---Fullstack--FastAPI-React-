import type { FormEvent } from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import './App.css';
import {
  ApiError,
  createTicket,
  deleteTicket,
  getCurrentAdmin,
  getTickets,
  loginAdmin,
  updateTicketStatus,
} from './api';
import type {
  AdminUser,
  PaginatedTicketsResponse,
  SortBy,
  SortOrder,
  Ticket,
  TicketPriority,
  TicketStatus,
} from './types';

const TOKEN_STORAGE_KEY = 'internal_requests_admin_token';

const statusLabels: Record<TicketStatus, string> = {
  new: 'Новая',
  in_progress: 'В работе',
  done: 'Готово',
};

const priorityLabels: Record<TicketPriority, string> = {
  low: 'Низкий',
  normal: 'Обычный',
  high: 'Высокий',
};

const statusOptions: TicketStatus[] = ['new', 'in_progress', 'done'];
const priorityOptions: TicketPriority[] = ['low', 'normal', 'high'];

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return 'Произошла неизвестная ошибка.';
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value));
}

function App() {
  const [ticketsData, setTicketsData] = useState<PaginatedTicketsResponse>({
    items: [],
    total: 0,
    page: 1,
    page_size: 10,
    pages: 0,
  });

  const [searchDraft, setSearchDraft] = useState('');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<TicketStatus | ''>('');
  const [priorityFilter, setPriorityFilter] = useState<TicketPriority | ''>('');
  const [sortBy, setSortBy] = useState<SortBy>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [createPriority, setCreatePriority] = useState<TicketPriority>('normal');

  const [adminUsername, setAdminUsername] = useState('admin');
  const [adminPassword, setAdminPassword] = useState('admin');
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_STORAGE_KEY),
  );
  const [adminUser, setAdminUser] = useState<AdminUser | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const listParams = useMemo(
    () => ({
      search,
      status: statusFilter,
      priority: priorityFilter,
      sort_by: sortBy,
      sort_order: sortOrder,
      page,
      page_size: pageSize,
    }),
    [page, pageSize, priorityFilter, search, sortBy, sortOrder, statusFilter],
  );

  const loadTickets = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const data = await getTickets(listParams);
      setTicketsData(data);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [listParams]);

  useEffect(() => {
    void loadTickets();
  }, [loadTickets]);

  useEffect(() => {
    if (!token) {
      setAdminUser(null);
      return;
    }

    getCurrentAdmin(token)
      .then(setAdminUser)
      .catch(() => {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        setToken(null);
        setAdminUser(null);
      });
  }, [token]);

  function resetToFirstPage() {
    setPage(1);
  }

  async function handleCreateTicket(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreating(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      await createTicket({
        title,
        description: description.trim() ? description : null,
        priority: createPriority,
      });

      setTitle('');
      setDescription('');
      setCreatePriority('normal');
      setSuccessMessage('Заявка создана.');
      setPage(1);
      await loadTickets();
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsCreating(false);
    }
  }

  async function handleStatusChange(ticket: Ticket, nextStatus: TicketStatus) {
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      await updateTicketStatus(ticket.id, nextStatus);
      setSuccessMessage('Статус заявки обновлён.');
      await loadTickets();
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    }
  }

  async function handleDeleteTicket(ticket: Ticket) {
    if (!token) {
      setErrorMessage('Для удаления заявки нужно войти как админ.');
      return;
    }

    const confirmed = window.confirm(
      `Удалить заявку #${ticket.id}: "${ticket.title}"?`,
    );

    if (!confirmed) return;

    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      await deleteTicket(ticket.id, token);
      setSuccessMessage('Заявка удалена.');
      await loadTickets();
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    }
  }

  async function handleAdminLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoggingIn(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const loginResponse = await loginAdmin({
        username: adminUsername,
        password: adminPassword,
      });

      localStorage.setItem(TOKEN_STORAGE_KEY, loginResponse.access_token);
      setToken(loginResponse.access_token);
      setSuccessMessage('Вход выполнен.');
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoggingIn(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setAdminUser(null);
    setSuccessMessage('Вы вышли из админ-аккаунта.');
  }

  function handleSearchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSearch(searchDraft);
    setPage(1);
  }

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">FastAPI + React</p>
          <h1>Учёт внутренних заявок</h1>
          <p className="subtitle">
            Создание, поиск, фильтрация, сортировка, пагинация и управление
            статусами заявок.
          </p>
        </div>

        <section className="admin-card" aria-label="Админ-панель">
          {adminUser ? (
            <>
              <div>
                <span className="admin-badge">Админ</span>
                <strong>{adminUser.username}</strong>
              </div>
              <button className="secondary-button" onClick={handleLogout}>
                Выйти
              </button>
            </>
          ) : (
            <form className="admin-form" onSubmit={handleAdminLogin}>
              <input
                value={adminUsername}
                onChange={(event) => setAdminUsername(event.target.value)}
                placeholder="Логин"
                aria-label="Логин админа"
              />
              <input
                value={adminPassword}
                onChange={(event) => setAdminPassword(event.target.value)}
                placeholder="Пароль"
                type="password"
                aria-label="Пароль админа"
              />
              <button disabled={isLoggingIn}>
                {isLoggingIn ? 'Вход...' : 'Войти'}
              </button>
            </form>
          )}
        </section>
      </header>

      {errorMessage && <div className="alert alert-error">{errorMessage}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      <section className="layout">
        <aside className="panel">
          <h2>Новая заявка</h2>

          <form className="stack" onSubmit={handleCreateTicket}>
            <label>
              Заголовок
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                minLength={3}
                maxLength={120}
                required
                placeholder="Например: Не работает принтер"
              />
            </label>

            <label>
              Описание
              <textarea
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                maxLength={1000}
                placeholder="Дополнительные детали"
              />
            </label>

            <label>
              Приоритет
              <select
                value={createPriority}
                onChange={(event) =>
                  setCreatePriority(event.target.value as TicketPriority)
                }
              >
                {priorityOptions.map((priority) => (
                  <option key={priority} value={priority}>
                    {priorityLabels[priority]}
                  </option>
                ))}
              </select>
            </label>

            <button disabled={isCreating}>
              {isCreating ? 'Создаём...' : 'Создать заявку'}
            </button>
          </form>
        </aside>

        <section className="panel tickets-panel">
          <div className="panel-heading">
            <div>
              <h2>Заявки</h2>
              <p>Всего: {ticketsData.total}</p>
            </div>
          </div>

          <form className="filters" onSubmit={handleSearchSubmit}>
            <input
              value={searchDraft}
              onChange={(event) => setSearchDraft(event.target.value)}
              placeholder="Поиск по title и description"
            />

            <select
              value={statusFilter}
              onChange={(event) => {
                setStatusFilter(event.target.value as TicketStatus | '');
                resetToFirstPage();
              }}
            >
              <option value="">Все статусы</option>
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {statusLabels[status]}
                </option>
              ))}
            </select>

            <select
              value={priorityFilter}
              onChange={(event) => {
                setPriorityFilter(event.target.value as TicketPriority | '');
                resetToFirstPage();
              }}
            >
              <option value="">Все приоритеты</option>
              {priorityOptions.map((priority) => (
                <option key={priority} value={priority}>
                  {priorityLabels[priority]}
                </option>
              ))}
            </select>

            <select
              value={sortBy}
              onChange={(event) => {
                setSortBy(event.target.value as SortBy);
                resetToFirstPage();
              }}
            >
              <option value="created_at">Дата создания</option>
              <option value="priority">Приоритет</option>
            </select>

            <select
              value={sortOrder}
              onChange={(event) => {
                setSortOrder(event.target.value as SortOrder);
                resetToFirstPage();
              }}
            >
              <option value="desc">По убыванию</option>
              <option value="asc">По возрастанию</option>
            </select>

            <button type="submit">Найти</button>
          </form>

          {isLoading ? (
            <div className="state">Загрузка заявок...</div>
          ) : ticketsData.items.length === 0 ? (
            <div className="state">Заявок пока нет или ничего не найдено.</div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Заявка</th>
                    <th>Статус</th>
                    <th>Приоритет</th>
                    <th>Создана</th>
                    <th>Обновлена</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {ticketsData.items.map((ticket) => (
                    <tr key={ticket.id}>
                      <td>#{ticket.id}</td>
                      <td>
                        <strong>{ticket.title}</strong>
                        {ticket.description && <p>{ticket.description}</p>}
                      </td>
                      <td>
                        <select
                          value={ticket.status}
                          disabled={ticket.status === 'done'}
                          onChange={(event) =>
                            handleStatusChange(
                              ticket,
                              event.target.value as TicketStatus,
                            )
                          }
                        >
                          {statusOptions.map((status) => (
                            <option key={status} value={status}>
                              {statusLabels[status]}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <span className={`priority priority-${ticket.priority}`}>
                          {priorityLabels[ticket.priority]}
                        </span>
                      </td>
                      <td>{formatDate(ticket.created_at)}</td>
                      <td>{formatDate(ticket.updated_at)}</td>
                      <td>
                        <button
                          className="danger-button"
                          disabled={!adminUser || ticket.status === 'done'}
                          title={
                            !adminUser
                              ? 'Удаление доступно только админу'
                              : ticket.status === 'done'
                                ? 'Заявку в done нельзя удалить'
                                : 'Удалить заявку'
                          }
                          onClick={() => handleDeleteTicket(ticket)}
                        >
                          Удалить
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <footer className="pagination">
            <label>
              На странице
              <select
                value={pageSize}
                onChange={(event) => {
                  setPageSize(Number(event.target.value));
                  setPage(1);
                }}
              >
                {[5, 10, 20, 50].map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </label>

            <div className="pagination-controls">
              <button
                disabled={page <= 1}
                onClick={() => setPage((currentPage) => currentPage - 1)}
              >
                Назад
              </button>
              <span>
                Страница {ticketsData.page} из {ticketsData.pages || 1}
              </span>
              <button
                disabled={ticketsData.pages === 0 || page >= ticketsData.pages}
                onClick={() => setPage((currentPage) => currentPage + 1)}
              >
                Вперёд
              </button>
            </div>
          </footer>
        </section>
      </section>
    </main>
  );
}

export default App;

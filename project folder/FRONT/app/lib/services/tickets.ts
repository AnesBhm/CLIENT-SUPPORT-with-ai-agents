import { fetchAPI } from "../api";

export interface TicketCreate {
    subject: string;
    description: string;
    category: string;
}

export interface TicketFeedback {
    is_satisfied: boolean;
    feedback_reason?: string;
}

export interface Ticket {
    id: number;
    subject: string;
    description: string;
    status: string;
    category: string;
    created_at: string;
    customer_id: number;
    ai_confidence_score?: number;
    ai_response?: string;
    // Add other fields as needed from backend schema
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    pages: number;
}

export interface TicketStatusResponse {
    status: string;
    ai_typing: boolean;
    ai_response_body: string | null;
}

export const ticketService = {
    createTicket: async (ticketData: TicketCreate) => {
        return await fetchAPI<Ticket>("/tickets/", {
            method: "POST",
            body: ticketData,
        });
    },

    getTickets: async (skip = 0, limit = 100) => {
        return await fetchAPI<PaginatedResponse<Ticket>>(`/tickets/?skip=${skip}&limit=${limit}`, {
            method: "GET",
        });
    },

    getTicket: async (id: number) => {
        return await fetchAPI<Ticket>(`/tickets/${id}`, {
            method: "GET",
        });
    },

    getTicketStatus: async (id: number) => {
        return await fetchAPI<TicketStatusResponse>(`/tickets/${id}/status`, {
            method: "GET",
        });
    },

    submitFeedback: async (id: number, feedback: TicketFeedback) => {
        return await fetchAPI<Ticket>(`/tickets/${id}/feedback`, {
            method: "POST",
            body: feedback,
        });
    },
};

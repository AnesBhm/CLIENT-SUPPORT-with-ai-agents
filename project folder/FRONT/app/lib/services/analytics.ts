import { fetchAPI } from "../api";

export interface CategorySatisfactionStats {
    satisfied_count: number;
    unsatisfied_count: number;
    total_ai_resolved: number;
    satisfaction_rate: number;
}

export interface DashboardStats {
    total_tickets: number;
    ai_resolved_tickets: number;
    waiting_tickets_count: number;
    average_response_time_hours: number;
    escalation_percentage: number;
    ai_satisfaction_by_category: Record<string, CategorySatisfactionStats>;
    low_satisfaction_alert: boolean;
    total_satisfaction_rate: number;
}

export const analyticsService = {
    getDashboardStats: async () => {
        return await fetchAPI<DashboardStats>("/admin/stats", {
            method: "GET",
        });
    },
};

"use client"
import React, { useState, useEffect } from 'react'
import {
    ArrowDownTrayIcon,
    MagnifyingGlassIcon
} from '@heroicons/react/24/outline'

// ============================================================================
// DONNÉES (MOCK DATA) SPÉCIFIQUES À ALL TICKETS
// ============================================================================
import { ticketService, Ticket } from '../lib/services/tickets'

export default function AllTicket() {
    const [searchTerm, setSearchTerm] = useState('')
    const [tickets, setTickets] = useState<Ticket[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadTickets();
    }, [])

    const loadTickets = async () => {
        try {
            setLoading(true)
            const response = await ticketService.getTickets(0, 1000)
            setTickets(response.items)
        } catch (error) {
            console.error("Failed to load tickets", error)
        } finally {
            setLoading(false)
        }
    }

    const filteredTickets = tickets.filter(t => {
        if (!searchTerm) return true;
        const lower = searchTerm.toLowerCase();
        return (
            String(t.id).includes(lower) ||
            t.subject.toLowerCase().includes(lower) ||
            // Client search fallback since we only have ID
            String(t.customer_id).includes(lower)
        )
    })

    // Basic formatting helper
    const formatDate = (dateStr: string) => {
        if (!dateStr) return '-'
        return new Date(dateStr).toLocaleDateString()
    }

    const getStatusColor = (s: string) => {
        if (s === 'Open' || s === 'Nouveau') return 'bg-blue-50 text-blue-700'
        if (s === 'In Progress' || s === 'En cours') return 'bg-orange-50 text-orange-700'
        if (s === 'Escalated') return 'bg-[#04093D] text-white'
        return 'bg-green-50 text-green-700'
    }

    return (
        <div className="flex flex-col h-full animate-fade-in-up space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <h2 className="text-2xl font-bold text-gray-900">Tous les Tickets</h2>
                <button onClick={loadTickets} className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 font-medium rounded-lg shadow-sm hover:bg-gray-50 transition-colors">
                    <ArrowDownTrayIcon className="w-5 h-5" /> Refresh
                </button>
            </div>

            <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex gap-4">
                <div className="relative flex-1">
                    <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Rechercher par ID ou Sujet..."
                        className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#714BD2] transition-all"
                    />
                </div>
            </div>

            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden flex-1 flex flex-col min-h-0">
                <div className="overflow-auto flex-1">
                    <table className="w-full text-left border-collapse min-w-[800px] md:min-w-full">
                        <thead className="bg-gray-50 border-b border-gray-100 sticky top-0 z-10">
                            <tr>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">ID</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Sujet</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Client</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Statut</th>
                                <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Agent</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {loading ? (
                                <tr><td colSpan={5} className="p-8 text-center text-gray-500">Chargement...</td></tr>
                            ) : filteredTickets.length === 0 ? (
                                <tr><td colSpan={5} className="p-8 text-center text-gray-500">Aucun ticket trouvé.</td></tr>
                            ) : (
                                filteredTickets.map((ticket) => (
                                    <tr key={ticket.id} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 text-xs font-mono text-gray-500">#{ticket.id}</td>
                                        <td className="px-6 py-4 font-bold text-gray-900 text-sm">{ticket.subject}</td>
                                        <td className="px-6 py-4 text-sm text-gray-600">Client #{ticket.customer_id}</td>
                                        <td className="px-6 py-4">
                                            <span className={`px-3 py-1 rounded-full border text-xs font-bold ${getStatusColor(ticket.status)}`}>
                                                {ticket.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-500">
                                            {/* Using a simplified check for agent */}
                                            {ticket.status.includes('AI') ? 'AI Agent' : (ticket.status === 'Resolved By Agent' ? 'Human Agent' : '-')}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
"use client"
import React, { useState } from 'react'
import {
  CheckCircleIcon,
  XCircleIcon,
  PauseCircleIcon,
  ArrowLeftIcon,
  PaperAirplaneIcon,
  FunnelIcon,
  ArrowPathIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'

// ============================================================================
// DONNÉES (MOCK DATA) SPÉCIFIQUES À L'INBOX
// ============================================================================
const initialTicketsData = [
  { id: 1, client: 'Amine Benali', avatar: 'AB', subject: 'Erreur lors du paiement CB', message: 'Je reçois une erreur 404 quand je valide mon panier...', status: 'Nouveau', priority: 'Haute', date: 'Il y a 10 min', unread: true, isAiResolved: false },
  { id: 2, client: 'Sophie Martin', avatar: 'SM', subject: 'Demande de remboursement', message: 'Le produit reçu ne correspond pas à la description...', status: 'En cours', priority: 'Moyenne', date: 'Il y a 1h', unread: false, isAiResolved: false },
  { id: 3, client: 'Karim Ziani', avatar: 'KZ', subject: 'Bug affichage Dashboard', message: 'Les graphiques ne se chargent pas sur Safari...', status: 'En cours', priority: 'Basse', date: 'Il y a 3h', unread: false, isAiResolved: false },
  { id: 4, client: 'Tech Corp', avatar: 'TC', subject: 'Facture manquante Octobre', message: 'Nous avons besoin de la facture pour la comptabilité.', status: 'Résolu', priority: 'Moyenne', date: 'Hier', unread: false, isAiResolved: false },
  { id: 5, client: 'Lina Dou', avatar: 'LD', subject: 'Problème connexion API', message: 'Ma clé API semble invalide depuis ce matin.', status: 'Nouveau', priority: 'Critique', date: 'Hier', unread: true, isAiResolved: false },
  { id: 6, client: 'John Doe', avatar: 'JD', subject: 'Réinitialisation mot de passe', message: 'Fait automatiquement.', status: 'Résolu', priority: 'Basse', date: 'Hier', unread: false, isAiResolved: true },
]

export default function InboxTicket() {
  const [tickets, setTickets] = useState(initialTicketsData)
  const [filter, setFilter] = useState('Tous')
  const [showAiResolved, setShowAiResolved] = useState(false)
  const [selectedTicket, setSelectedTicket] = useState<any>(null)
  const [chatMessage, setChatMessage] = useState('')
  const [showCloseModal, setShowCloseModal] = useState(false)

  const confirmCloseTicket = (status: 'Résolu' | 'Non résolu' | 'En attente') => {
    const updatedTickets = tickets.map(t =>
      t.id === selectedTicket.id
        ? { ...t, status: 'Résolu' } // J'ai retiré la mise à jour de la priorité ici aussi car elle n'est plus affichée
        : t
    )
    setTickets(updatedTickets)
    setShowCloseModal(false)
    setSelectedTicket(null)
  }

  const filteredTickets = tickets.filter(ticket => {
    if (filter === 'Non lus' && !ticket.unread) return false
    if (filter === 'En cours' && ticket.status !== 'En cours' && ticket.status !== 'Nouveau') return false
    if (filter === 'Résolus' && ticket.status !== 'Résolu') return false
    if (filter === 'Résolus' && showAiResolved && !ticket.isAiResolved) return false
    return true
  })

  // MODE CHAT (Détail du ticket)
  if (selectedTicket) {
    return (
      <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden animate-fade-in-up relative">
        {/* MODAL DE CONFIRMATION DE CLÔTURE */}
        {showCloseModal && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
            <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm border border-gray-100 animate-scale-in">
              <h3 className="text-lg font-bold text-gray-900 mb-2">Clôturer le ticket</h3>
              <p className="text-sm text-gray-500 mb-6">Sélectionnez le statut final.</p>
              <div className="space-y-3">
                <button onClick={() => confirmCloseTicket('Résolu')} className="w-full flex items-center justify-between p-4 rounded-xl border border-gray-200 hover:border-green-500 hover:bg-green-50 group transition-all">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-full text-green-600 group-hover:bg-green-200"><CheckCircleIcon className="w-5 h-5" /></div>
                    <span className="font-bold text-gray-700 group-hover:text-green-800">Problème Résolu</span>
                  </div>
                </button>
                <button onClick={() => confirmCloseTicket('Non résolu')} className="w-full flex items-center justify-between p-4 rounded-xl border border-gray-200 hover:border-red-500 hover:bg-red-50 group transition-all">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-red-100 rounded-full text-red-600 group-hover:bg-red-200"><XCircleIcon className="w-5 h-5" /></div>
                    <span className="font-bold text-gray-700 group-hover:text-red-800">Non Résolu</span>
                  </div>
                </button>
                <button onClick={() => confirmCloseTicket('En attente')} className="w-full flex items-center justify-between p-4 rounded-xl border border-gray-200 hover:border-orange-500 hover:bg-orange-50 group transition-all">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-100 rounded-full text-orange-600 group-hover:bg-orange-200"><PauseCircleIcon className="w-5 h-5" /></div>
                    <span className="font-bold text-gray-700 group-hover:text-orange-800">Mettre en attente</span>
                  </div>
                </button>
              </div>
              <button onClick={() => setShowCloseModal(false)} className="mt-6 w-full py-3 text-sm font-bold text-gray-500 hover:text-gray-900">Annuler</button>
            </div>
          </div>
        )}

        {/* HEADER DU CHAT */}
        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <div className="flex items-center gap-4">
            <button onClick={() => setSelectedTicket(null)} className="p-2 hover:bg-white rounded-full border border-transparent hover:border-gray-200 transition-all text-gray-500"><ArrowLeftIcon className="w-5 h-5" /></button>
            <div>
              <h3 className="font-bold text-gray-900">{selectedTicket.subject}</h3>
              {/* Suppression de l'affichage de la priorité ici */}
              <p className="text-xs text-gray-500">Client: {selectedTicket.client}</p>
            </div>
          </div>
          <button onClick={() => setShowCloseModal(true)} className="hidden md:flex items-center gap-2 px-6 py-2.5 bg-[#141516] text-white text-sm font-bold rounded-xl hover:bg-black transition-all shadow-md">Clôturer le ticket</button>
          {/* Bouton mobile pour clôturer (icône seulement) */}
          <button onClick={() => setShowCloseModal(true)} className="md:hidden p-2 bg-[#141516] text-white rounded-lg"><CheckCircleIcon className="w-5 h-5" /></button>
        </div>

        {/* ZONE DE MESSAGES */}
        <div className="flex-1 p-6 overflow-y-auto bg-white space-y-6">
          <div className="flex justify-start"><div className="max-w-[85%] md:max-w-[70%]"><div className="bg-gray-100 p-4 rounded-2xl rounded-tl-none text-sm text-gray-800">{selectedTicket.message}</div><span className="text-[10px] text-gray-400 mt-1 ml-2 block">Client • {selectedTicket.date}</span></div></div>
          <div className="flex justify-end"><div className="max-w-[85%] md:max-w-[70%]"><div className="bg-[#714BD2] p-4 rounded-2xl rounded-tr-none text-sm text-white">Bonjour {selectedTicket.client.split(' ')[0]}, je prends en charge votre demande.</div><span className="text-[10px] text-gray-400 mt-1 mr-2 block text-right">Moi • À l'instant</span></div></div>
        </div>

        {/* INPUT MESSAGE */}
        <div className="p-4 border-t border-gray-100"><div className="flex gap-3"><input type="text" value={chatMessage} onChange={(e) => setChatMessage(e.target.value)} placeholder="Écrire une réponse..." className="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#714BD2]" /><button className="p-3 bg-[#141516] text-white rounded-xl hover:bg-black"><PaperAirplaneIcon className="w-5 h-5 -rotate-45 translate-x-[-1px] translate-y-[1px]" /></button></div></div>
      </div>
    )
  }

  // MODE LISTE (Affichage par défaut)
  return (
    <div className="flex flex-col h-full animate-fade-in-up">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div><h2 className="text-2xl font-bold text-gray-900">Boîte de réception</h2><p className="text-gray-500 text-sm">Gérez les tickets et les demandes clients.</p></div>
        <div className="flex gap-3 w-full md:w-auto">
          <button className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium hover:bg-gray-50 text-gray-700 transition-colors"><FunnelIcon className="w-4 h-4" /> Filtrer</button>
          <button className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium hover:bg-gray-50 text-gray-700 transition-colors"><ArrowPathIcon className="w-4 h-4" /> Actualiser</button>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm flex-1 flex flex-col overflow-hidden">
        <div className="flex items-center justify-between px-6 border-b border-gray-100 overflow-x-auto bg-gray-50/50">
          <div className="flex gap-6">
            {['Tous', 'Non lus', 'En cours', 'Résolus'].map((tab) => (
              <button key={tab} onClick={() => { setFilter(tab); setShowAiResolved(false); }} className={`py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${filter === tab ? 'border-[#714BD2] text-[#714BD2]' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>{tab}</button>
            ))}
          </div>
          {filter === 'Résolus' && (<div className="flex items-center gap-2 py-2"><button onClick={() => setShowAiResolved(!showAiResolved)} className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold border transition-all ${showAiResolved ? 'bg-[#FCEE21] border-[#FCEE21] text-black' : 'bg-white border-gray-300 text-gray-500 hover:border-gray-400'}`}><CpuChipIcon className="w-4 h-4" /> Résolu par AI</button></div>)}
        </div>

        <div className="overflow-y-auto flex-1 p-2">
          {filteredTickets.map((ticket) => (
            <div key={ticket.id} onClick={() => setSelectedTicket(ticket)} className={`group flex items-center gap-4 p-4 rounded-xl cursor-pointer transition-all border border-transparent hover:border-gray-200 hover:bg-gray-50 ${ticket.unread ? 'bg-gray-50/50' : 'bg-white'}`}>
              <input type="checkbox" onClick={(e) => e.stopPropagation()} className="w-4 h-4 rounded border-gray-300 text-[#714BD2] focus:ring-[#714BD2] ml-2" />
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-600 shrink-0 relative">
                {ticket.avatar}
                {ticket.isAiResolved && (<div className="absolute -bottom-1 -right-1 bg-[#FCEE21] rounded-full p-0.5 border border-white" title="Résolu par IA"><CpuChipIcon className="w-3 h-3 text-black" /></div>)}
              </div>
              <div className="flex-1 min-w-0 grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
                <div className="md:col-span-5">
                  <div className="flex items-center gap-2 mb-0.5"><span className={`text-sm font-bold ${ticket.unread ? 'text-gray-900' : 'text-gray-600'}`}>{ticket.subject}</span>{ticket.unread && <span className="w-2 h-2 bg-[#FCEE21] rounded-full"></span>}</div>
                  <p className="text-xs text-gray-500 truncate">{ticket.message}</p>
                </div>
                <div className="md:col-span-3 flex items-center gap-2">
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide ${ticket.status === 'Nouveau' ? 'bg-blue-50 text-blue-600' : ticket.status === 'En cours' ? 'bg-orange-50 text-orange-600' : 'bg-green-50 text-green-600'}`}>{ticket.status}</span>
                  {/* Suppression de l'affichage de la priorité dans la liste */}
                </div>
                <div className="md:col-span-3 text-right hidden md:block"><p className="text-xs font-bold text-gray-900">{ticket.client}</p><p className="text-[10px] text-gray-400">{ticket.date}</p></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
"use client"
import React, { useState, useEffect } from 'react'
import { 
  MagnifyingGlassIcon,
  FunnelIcon, 
  ArrowDownTrayIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline'

// ============================================================================
// DONNÉES (MOCK DATA) SPÉCIFIQUES AUX CLIENTS
// ============================================================================
const clientsData = [
  { id: 'CL-001', prenom: 'Amine', nom: 'Benali', societe: 'Tech Solutions', email: 'amine@tech.com', phone: '0550 12 34 56', date: '2023-10-15', status: 'Actif' },
  { id: 'CL-002', prenom: 'Sophie', nom: 'Martin', societe: 'Design Studio', email: 'sophie@design.com', phone: '0561 22 33 44', date: '2023-11-02', status: 'Actif' },
  { id: 'CL-003', prenom: 'Karim', nom: 'Ziani', societe: 'Freelance', email: 'karim.z@gmail.com', phone: '0770 99 88 77', date: '2023-09-10', status: 'Inactif' },
  { id: 'CL-004', prenom: 'Lina', nom: 'Dou', societe: 'StartUp Inc', email: 'lina@startup.io', phone: '0661 55 66 77', date: '2023-12-01', status: 'Actif' },
  { id: 'CL-005', prenom: 'John', nom: 'Doe', societe: '-', email: 'john.doe@test.com', phone: '0555 00 00 00', date: '2023-08-20', status: 'Suspendu' },
  { id: 'CL-006', prenom: 'Sarah', nom: 'Connor', societe: 'Cyberdyne', email: 'sarah@future.net', phone: '0540 11 22 33', date: '2024-01-05', status: 'Actif' },
]

export default function Clients() {
  const [searchTerm, setSearchTerm] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [filteredClients, setFilteredClients] = useState(clientsData)

  useEffect(() => {
    let results = clientsData
    if (searchTerm) {
      const lowerTerm = searchTerm.toLowerCase()
      results = results.filter(client => 
        client.nom.toLowerCase().includes(lowerTerm) || 
        client.prenom.toLowerCase().includes(lowerTerm) || 
        client.societe.toLowerCase().includes(lowerTerm) || 
        client.id.toLowerCase().includes(lowerTerm) || 
        client.email.toLowerCase().includes(lowerTerm)
      )
    }
    if (startDate) results = results.filter(client => new Date(client.date) >= new Date(startDate))
    if (endDate) results = results.filter(client => new Date(client.date) <= new Date(endDate))
    setFilteredClients(results)
  }, [searchTerm, startDate, endDate])

  const handleReset = () => { setSearchTerm(''); setStartDate(''); setEndDate(''); }

  return (
    <div className="flex flex-col h-full animate-fade-in-up space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <h2 className="text-2xl font-bold text-gray-900">Gestion des Clients</h2>
            <p className="text-gray-500 text-sm">Consultez et gérez la base de données clients.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors shadow-sm">
            <ArrowDownTrayIcon className="w-5 h-5" /> Exporter CSV
        </button>
      </div>

      <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
        <div className="md:col-span-5 space-y-1">
            <label className="text-xs font-bold text-gray-500 ml-1">Rechercher</label>
            <div className="relative">
                <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input 
                    type="text" 
                    value={searchTerm} 
                    onChange={(e) => setSearchTerm(e.target.value)} 
                    placeholder="Nom, Société, ID..." 
                    className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#714BD2] transition-all text-sm" 
                />
            </div>
        </div>
        <div className="md:col-span-3 space-y-1">
            <label className="text-xs font-bold text-gray-500 ml-1">Inscrit après le</label>
            <input 
                type="date" 
                value={startDate} 
                onChange={(e) => setStartDate(e.target.value)} 
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#714BD2] text-sm text-gray-600" 
            />
        </div>
        <div className="md:col-span-3 space-y-1">
            <label className="text-xs font-bold text-gray-500 ml-1">Inscrit avant le</label>
            <input 
                type="date" 
                value={endDate} 
                onChange={(e) => setEndDate(e.target.value)} 
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#714BD2] text-sm text-gray-600" 
            />
        </div>
        <div className="md:col-span-1">
            <button onClick={handleReset} className="w-full py-2.5 bg-gray-100 text-gray-600 rounded-xl hover:bg-gray-200 transition-colors text-sm font-bold flex items-center justify-center">
                <FunnelIcon className="w-5 h-5" />
            </button>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden flex-1">
        <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[900px] md:min-w-full">
                <thead className="bg-gray-50/50 border-b border-gray-100">
                    <tr>
                        <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Client</th>
                        <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Société</th>
                        <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Contact</th>
                        <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Date</th>
                        <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Statut</th>
                        <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase text-right">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {filteredClients.map((client) => (
                        <tr key={client.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-400">
                                        <UserCircleIcon className="w-6 h-6" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold text-gray-900">{client.prenom} {client.nom}</p>
                                        <p className="text-xs text-gray-400 font-mono">{client.id}</p>
                                    </div>
                                </div>
                            </td>
                            <td className="px-6 py-4"><p className="text-sm font-medium text-gray-700">{client.societe}</p></td>
                            <td className="px-6 py-4">
                                <div className="flex flex-col">
                                    <span className="text-sm text-gray-600">{client.email}</span>
                                    <span className="text-xs text-gray-400">{client.phone}</span>
                                </div>
                            </td>
                            <td className="px-6 py-4"><span className="text-sm text-gray-600">{client.date}</span></td>
                            <td className="px-6 py-4">
                                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${client.status === 'Actif' ? 'bg-green-50 text-green-700 border-green-100' : 'bg-gray-50 text-gray-600 border-gray-200'}`}>
                                    {client.status}
                                </span>
                            </td>
                            <td className="px-6 py-4 text-right">
                                <button className="text-xs font-bold text-[#714BD2] hover:underline">Voir profil</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
      </div>
    </div>
  )
}
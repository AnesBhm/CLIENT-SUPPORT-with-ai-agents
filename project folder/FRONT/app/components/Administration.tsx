"use client"
import React, { useState } from 'react'
import { 
  UserPlusIcon, 
  ShieldCheckIcon, 
  PencilSquareIcon, 
  TrashIcon 
} from '@heroicons/react/24/outline'

// ============================================================================
// DONNÉES (MOCK DATA) SPÉCIFIQUES À L'ADMINISTRATION
// ============================================================================
const initialAgents = [
  { id: 1, nom: 'Smith', prenom: 'John', fonction: 'Support N2', identifiant: 'john.s' },
  { id: 2, nom: 'Doe', prenom: 'Jane', fonction: 'Admin', identifiant: 'jane.d' },
  { id: 3, nom: 'Wayne', prenom: 'Bruce', fonction: 'Support N1', identifiant: 'batman' },
]

export default function Administration() {
  const [agents, setAgents] = useState(initialAgents)
  const [formData, setFormData] = useState({ nom: '', prenom: '', fonction: 'Support N1', identifiant: '', mdp: '' })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => { 
      setFormData({ ...formData, [e.target.name]: e.target.value }) 
  }

  const handleSubmit = (e: React.FormEvent) => { 
      e.preventDefault(); 
      if (!formData.nom || !formData.prenom) return; 
      
      const newAgent = { 
          id: Date.now(), 
          ...formData 
      }
      
      // On ignore le mot de passe pour l'affichage, c'est juste une simulation
      setAgents([...agents, newAgent as any]); 
      setFormData({ nom: '', prenom: '', fonction: 'Support N1', identifiant: '', mdp: '' }) 
  }

  const handleDelete = (id: number) => { 
      setAgents(agents.filter(a => a.id !== id)) 
  }

  return (
    <div className="flex flex-col h-full animate-fade-in-up space-y-6">
      <div className="mb-2">
          <h2 className="text-2xl font-bold text-gray-900">Administration</h2>
          <p className="text-gray-500 text-sm">Gérez les comptes employés et les accès.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full">
        
        {/* FORMULAIRE D'AJOUT (Gauche) */}
        <div className="lg:col-span-4 bg-white p-6 rounded-2xl border border-gray-100 shadow-sm h-fit lg:sticky lg:top-6">
            <h3 className="font-bold text-lg text-slate-800 mb-6 flex items-center gap-2">
                <UserPlusIcon className="w-5 h-5" /> Ajouter un agent
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="text-xs font-bold text-gray-500">Prénom</label>
                        <input name="prenom" value={formData.prenom} onChange={handleInputChange} className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#714BD2]" />
                    </div>
                    <div>
                        <label className="text-xs font-bold text-gray-500">Nom</label>
                        <input name="nom" value={formData.nom} onChange={handleInputChange} className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#714BD2]" />
                    </div>
                </div>
                <div>
                    <label className="text-xs font-bold text-gray-500">Fonction</label>
                    <select name="fonction" value={formData.fonction} onChange={handleInputChange} className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#714BD2]">
                        <option>Support N1</option>
                        <option>Support N2</option>
                        <option>Admin</option>
                    </select>
                </div>
                <div>
                    <label className="text-xs font-bold text-gray-500">Identifiant</label>
                    <input name="identifiant" value={formData.identifiant} onChange={handleInputChange} className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#714BD2]" />
                </div>
                <div>
                    <label className="text-xs font-bold text-gray-500">Mot de passe</label>
                    <input name="mdp" type="password" value={formData.mdp} onChange={handleInputChange} className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#714BD2]" />
                </div>
                <button type="submit" className="w-full mt-4 bg-[#141516] text-white font-bold py-3 rounded-xl hover:bg-black transition-all shadow-md">
                    Créer le compte
                </button>
            </form>
        </div>

        {/* LISTE DES AGENTS (Droite) */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
                <h3 className="font-bold text-lg text-slate-800 flex items-center gap-2">
                    <ShieldCheckIcon className="w-5 h-5" /> Liste des agents
                </h3>
                <span className="bg-gray-200 text-gray-600 text-xs font-bold px-2 py-1 rounded-full">{agents.length} users</span>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse min-w-[600px] lg:min-w-full">
                    <thead className="bg-gray-50 border-b border-gray-100">
                        <tr>
                            <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Identité</th>
                            <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Fonction</th>
                            <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">ID Connexion</th>
                            <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {agents.map((agent) => (
                            <tr key={agent.id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-xs">
                                            {agent.prenom.charAt(0)}{agent.nom.charAt(0)}
                                        </div>
                                        <span className="text-sm font-bold text-gray-900">{agent.prenom} {agent.nom}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-600">
                                    <span className="px-2 py-1 rounded text-xs font-bold border bg-gray-50 border-gray-200">
                                        {agent.fonction}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-sm font-mono text-gray-500">{agent.identifiant}</td>
                                <td className="px-6 py-4 text-right flex justify-end gap-2">
                                    <button className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors">
                                        <PencilSquareIcon className="w-4 h-4" />
                                    </button>
                                    <button onClick={() => handleDelete(agent.id)} className="p-1.5 text-gray-400 hover:text-red-600 transition-colors">
                                        <TrashIcon className="w-4 h-4" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
      </div>
    </div>
  )
}
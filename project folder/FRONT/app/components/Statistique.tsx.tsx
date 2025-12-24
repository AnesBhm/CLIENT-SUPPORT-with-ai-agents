"use client"
import React from 'react'
import { 
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline'
import { 
  BarChart, Bar, PieChart, Pie, Cell, Legend, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer 
} from 'recharts'

// ============================================================================
// DONNÉES (MOCK DATA) SPÉCIFIQUES AUX STATISTIQUES
// ============================================================================

const weeklyData = [
  { name: 'Lun', tickets: 40 },
  { name: 'Mar', tickets: 30 },
  { name: 'Mer', tickets: 55 },
  { name: 'Jeu', tickets: 45 },
  { name: 'Ven', tickets: 60 },
  { name: 'Sam', tickets: 20 },
  { name: 'Dim', tickets: 15 },
]

const satisfactionData = [
  { name: 'Satisfait', value: 65, color: '#4ADE80' },
  { name: 'Neutre', value: 25, color: '#FACC15' },
  { name: 'Insatisfait', value: 10, color: '#F87171' },
]

// Sous-composant pour les cartes KPI
function KPICard({ title, value, change, isPositive }: any) {
    return (
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
            <p className="text-gray-500 text-sm font-medium">{title}</p>
            <div className="flex items-end gap-3 mt-2">
                <h3 className="text-3xl font-bold text-slate-900">{value}</h3>
                <span className={`flex items-center text-xs font-bold px-2 py-1 rounded-full ${isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {isPositive ? <ArrowUpIcon className="w-3 h-3 mr-1"/> : <ArrowDownIcon className="w-3 h-3 mr-1"/>}{change}
                </span>
            </div>
        </div>
    )
}

export default function Statistique() {
  return (
    <div className="flex flex-col h-full animate-fade-in-up space-y-8">
      <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Statistiques</h2>
          <select className="bg-white border border-gray-200 text-sm rounded-lg px-4 py-2 font-medium focus:outline-none focus:ring-2 focus:ring-[#714BD2]">
              <option>Ce mois-ci</option>
              <option>Cette semaine</option>
              <option>Aujourd'hui</option>
          </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard title="Temps Moyen Résolution" value="1h 45m" change="-12%" isPositive={true} />
        <KPICard title="Taux de Satisfaction" value="4.8/5" change="+0.2" isPositive={true} />
        <KPICard title="Tickets Réouverts" value="5%" change="+1%" isPositive={false} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* GRAPHIQUE BARRES */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-6">Volume Hebdomadaire</h3>
            <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={weeklyData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#9CA3AF', fontSize: 12}} dy={10} />
                        <YAxis axisLine={false} tickLine={false} tick={{fill: '#9CA3AF', fontSize: 12}} />
                        <Tooltip cursor={{fill: '#F3F4F6'}} contentStyle={{ borderRadius: '12px', border: 'none' }} />
                        <Bar dataKey="tickets" fill="#714BD2" radius={[6, 6, 0, 0]} barSize={40} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>

        {/* GRAPHIQUE CIRCULAIRE (PIE) */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
            <h3 className="font-bold text-slate-800 mb-6">Satisfaction Client</h3>
            <div className="h-[300px] w-full relative">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie 
                            data={satisfactionData} 
                            cx="50%" 
                            cy="50%" 
                            innerRadius={80} 
                            outerRadius={110} 
                            paddingAngle={5} 
                            dataKey="value"
                        >
                            {satisfactionData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                        </Pie>
                        <Tooltip contentStyle={{ borderRadius: '12px', border: 'none' }} />
                        <Legend verticalAlign="bottom" height={36} iconType="circle" />
                    </PieChart>
                </ResponsiveContainer>
                {/* Texte au centre du donut */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center -mt-4 pointer-events-none">
                    <span className="text-3xl font-bold text-slate-800">1,240</span>
                    <p className="text-xs text-gray-400">Avis</p>
                </div>
            </div>
        </div>
      </div>
    </div>
  )
}
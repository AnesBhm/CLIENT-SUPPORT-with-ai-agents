"use client"
import React, { useState } from 'react'
import Link from 'next/link' // Import nécessaire pour le lien
import { 
  UserCircleIcon, 
  EnvelopeIcon, 
  PhoneIcon, 
  MapPinIcon, 
  ArrowLeftIcon // Nouvelle icône pour le retour
} from '@heroicons/react/24/outline'

export default function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false)

  return (
    // pt-32 pour compenser la Navbar fixe
    <div className="min-h-screen bg-[#FAFAFA] pt-32 pb-12 px-6">
      <div className="max-w-4xl mx-auto">

        {/* --- BOUTON RETOUR --- */}
        <Link 
            href="/client" // Remplace par le chemin de ta page client (ex: /client ou /dashboard)
            className="inline-flex items-center gap-2 text-gray-500 hover:text-[#714BD2] mb-8 font-bold transition-colors"
        >
            <ArrowLeftIcon className="w-5 h-5" />
            Retour au Dashboard
        </Link>

        {/* --- EN-TÊTE PAGE --- */}
        <div className="mb-8 flex justify-between items-center">
            <h1 className="text-3xl font-extrabold text-[#141516]">Mon Profil</h1>
            <button 
                onClick={() => setIsEditing(!isEditing)}
                className={`px-6 py-2 rounded-full font-bold text-sm transition-colors ${
                    isEditing 
                        ? 'bg-[#FCEE21] text-black hover:bg-[#e6d91e]' 
                        : 'bg-[#141516] text-white hover:bg-gray-800'
                }`}
            >
                {isEditing ? 'Enregistrer' : 'Modifier'}
            </button>
        </div>

        {/* --- CARTE PROFIL --- */}
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden p-8 md:p-12 animate-fade-in-up">
            
            {/* Header Profil (Avatar + Nom) */}
            <div className="flex flex-col md:flex-row items-center gap-8 mb-12">
                <div className="w-32 h-32 rounded-full bg-gray-100 border-4 border-white shadow-lg flex items-center justify-center text-gray-400 overflow-hidden relative">
                    {/* Placeholder Avatar */}
                    <UserCircleIcon className="w-20 h-20" />
                </div>
                <div className="text-center md:text-left">
                    <h2 className="text-2xl font-bold text-gray-900">Client Doxa</h2>
                    <p className="text-gray-500">client@doxa.com</p>
                    <span className="inline-block mt-2 px-3 py-1 bg-[#FCEE21] text-xs font-bold rounded-full uppercase tracking-wide text-black">Premium</span>
                </div>
            </div>

            {/* Formulaire Informations */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                
                <div className="space-y-2">
                    <label className="text-sm font-bold text-gray-500 flex items-center gap-2">
                        <UserCircleIcon className="w-4 h-4"/> Nom Complet
                    </label>
                    <input 
                        type="text" 
                        defaultValue="Client Doxa" 
                        disabled={!isEditing}
                        className={`w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 font-medium text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#714BD2] transition-all ${!isEditing && 'opacity-60 cursor-not-allowed'}`}
                    />
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-bold text-gray-500 flex items-center gap-2">
                        <EnvelopeIcon className="w-4 h-4"/> Email
                    </label>
                    <input 
                        type="email" 
                        defaultValue="client@doxa.com" 
                        disabled={true} // Email souvent non modifiable pour sécurité
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 font-medium text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#714BD2] cursor-not-allowed opacity-60"
                    />
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-bold text-gray-500 flex items-center gap-2">
                        <PhoneIcon className="w-4 h-4"/> Téléphone
                    </label>
                    <input 
                        type="tel" 
                        defaultValue="+33 6 12 34 56 78" 
                        disabled={!isEditing}
                        className={`w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 font-medium text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#714BD2] transition-all ${!isEditing && 'opacity-60 cursor-not-allowed'}`}
                    />
                </div>

                <div className="space-y-2">
                    <label className="text-sm font-bold text-gray-500 flex items-center gap-2">
                        <MapPinIcon className="w-4 h-4"/> Adresse
                    </label>
                    <input 
                        type="text" 
                        defaultValue="Paris, France" 
                        disabled={!isEditing}
                        className={`w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 font-medium text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#714BD2] transition-all ${!isEditing && 'opacity-60 cursor-not-allowed'}`}
                    />
                </div>

            </div>

        </div>
      </div>
    </div>
  )
}
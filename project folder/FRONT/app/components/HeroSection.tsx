import React from 'react'
import Image from 'next/image'
import Link from 'next/link'

export default function HeroSection() {

  const services = [
    {
      title: "AI Agent",
      description: "Our AI processes your everyday requests instantly.Available day and night",
      icon: (
        <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
      )
    },
    {
      title: "Human Experts",
      description: "Our expert agents take over for complex problems requiring in depth analysis.",
      icon: (
        <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
      )
    },
    {
      title: "Hybrid Gateway",
      description: "Intelligent context transfer between AI and human. No repetition for the client.",
      icon: (
        <svg className="w-8 h-8 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>
      )
    }
  ]

  return (
    <div className="relative bg-[#FCFCFD] text-gray-900">
      
      {/* =========================================
          1. BANDE LATÉRALE GAUCHE (CONTINUE)
      ========================================== */}
      {/* Elle fait toute la hauteur du composant parent (absolute top-0 bottom-0) */}
      <div className="hidden lg:block absolute top-24 bottom-0 -left-20 w-32 xl:w-64 z-0">
        <div className="relative h-full w-full">
          <Image 
            src="/pattern.svg" // Ton image latérale
            alt="Design Pattern"
            fill
            className="object-cover object-left-top" 
            priority 
          />
        </div>
      </div>

      {/* =========================================
          2. CONTENEUR GLOBAL DES SECTIONS
      ========================================== */}
      {/* On décale tout le contenu à droite du pattern */}
      <div className="relative z-10 w-full pl-4 md:pl-10 lg:pl-48 xl:pl-64 pr-6">
        
        {/* --- SECTION 1 : HERO (PREND TOUTE LA PAGE) --- */}
        {/* min-h-screen : Force la hauteur à 100% de l'écran */}
        <section className="min-h-screen flex items-center justify-center py-20">
            <div className="w-full max-w-7xl mx-auto flex flex-col-reverse lg:flex-row items-center justify-between gap-12">
                
                {/* Texte Hero */}
                <div className="flex-1 space-y-8 text-center lg:text-left">
                    <h1 className="text-5xl md:text-6xl lg:text-8xl font-bold tracking-tight text-[#141516] leading-[1.1]">
                        Need client <br />
                        service?
                    </h1>
                    <p className="text-gray-600 font-medium max-w-md text-lg mx-auto lg:mx-0">
                        Doxa client service platform allows you to manage inquiries efficiently.
                    </p>
                    <Link href="/signup" className="inline-block px-10 py-4 rounded-full bg-[#FCEE21] text-black font-bold text-xl hover:bg-[#e6d91e] transition-all shadow-md hover:-translate-y-1">
                        Register Now!
                    </Link>
                </div>

                {/* Image Hero */}
                <div className="flex-1 w-full flex justify-center lg:justify-end">
                    <div className="relative w-full max-w-lg aspect-[4/3]">
                        <Image 
                            src="/at work 2.svg" 
                            alt="Illustration"
                            fill
                            className="object-contain"
                            priority
                        />
                    </div>
                </div>
            </div>
        </section>


{/* --- SECTION 2 : ABOUT US --- */}
        {/* CORRECTION : J'ai enlevé 'min-h-screen' et 'flex items-center'.
            J'ai mis 'py-24' (padding vertical) pour que ce soit aéré mais sans forcer la pleine page.
        */}
        <section className="py-24">
            <div className="max-w-4xl">
                <h2 className="text-5xl md:text-6xl font-bold text-[#141516] mb-8">
                    About us
                </h2>
                <p className="text-xl md:text-2xl text-gray-600 leading-relaxed font-light">
                    A support platform where users can send inquiries and get help with any Doxa related issues. We aim to bridge the gap between automated efficiency and human empathy.
                </p>
            </div>
        </section>


        {/* --- SECTION 3 : SERVICES --- */}
        {/* CORRECTION : J'ai aussi enlevé 'min-h-screen' ici pour que ça remonte directement après About Us.
            Le padding 'py-24' assure l'espacement.
        */}
        <section className="py-24">
            <div className="w-full max-w-7xl">
                <div className="mb-16">
                    <h2 className="text-5xl md:text-6xl font-bold text-[#141516] mb-6">
                        Services
                    </h2>
                    <p className="text-xl text-gray-500 max-w-2xl">
                        Enjoy the best of both worlds: the speed of AI and the empathy of our experts.
                    </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {services.map((service, index) => (
                        <div key={index} className="group flex flex-col items-start p-10 rounded-[2rem] bg-white border border-gray-100 shadow-sm hover:border-[#FCEE21] hover:shadow-xl transition-all duration-300 h-80 justify-between">
                            <div className="w-16 h-16 bg-[#FCEE21] rounded-2xl flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform duration-300">
                                {service.icon}
                            </div>

                            <div>
                                <h3 className="text-2xl font-bold mb-3 text-gray-900">{service.title}</h3>
                                <p className="text-gray-600 leading-relaxed">{service.description}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>

      </div>
    </div>
  )
}
"use client"
import Image from "next/image"
import Link from "next/link"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"

export default function DoxaNavbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const handleScroll = (e: Event) => {
      const target = e.target as HTMLElement
      setIsScrolled(target.scrollTop > 10)
    }

    const mainElement = document.querySelector('main')
    if (mainElement) {
      mainElement.addEventListener("scroll", handleScroll)
      return () => mainElement.removeEventListener("scroll", handleScroll)
    }
  }, [])

  return (
    <>
      <nav 
        className={`fixed top-0 w-full z-50 transition-all duration-300 bg-[#F9FAFB] border-b border-gray-100 h-24 flex items-center ${
          isScrolled ? 'shadow-sm' : ''
        }`}
      >
        
        {/* --- CONTAINER PRINCIPAL --- */}
        {/* justify-between repousse le "Groupe Gauche" tout à gauche et le "Groupe Droite" tout à droite */}
        <div className="w-full max-w-7xl mx-auto px-6 flex items-center justify-between">
          
          {/* ==============================================================
              GROUPE GAUCHE (LOGO + NAVIGATION)
          ============================================================== */}
          <div className="flex items-center gap-10 xl:gap-12">
            
            {/* 1. LOGO */}
            <Link href="/" className="flex items-center gap-3 cursor-pointer group select-none ">
               <div className="relative w-45 h-40 -ml-25">
                  <Image 
                    src="/logo.svg"
                    alt="DOXA Logo"
                    fill
                    className="object-contain"
                    priority
                  />
               </div>
            </Link>

            {/* 2. LIENS DE NAVIGATION (Collés au logo) */}
            <div className="hidden lg:flex items-center gap-6">
               {/* Petite barre de séparation esthétique */}
               <div className="h-6 w-px bg-[#B6BBCC] mr-2"></div>

               <Link href="/#about" className="text-gray-500 font-bold text-base hover:text-[#714BD2] transition-colors">
                 About us
               </Link>
               <Link href="/#services" className="text-gray-500 font-bold text-base hover:text-[#714BD2] transition-colors">
                 Services
               </Link>
               <Link href="/contact" className="text-gray-500 font-bold text-base hover:text-[#714BD2] transition-colors">
                 Contact
               </Link>
            </div>

          </div>


          {/* ==============================================================
              GROUPE DROITE (BOUTONS AUTH)
          ============================================================== */}
          <div className="hidden lg:flex items-center gap-4 -mr-25">
            <Link
              href="/login"
              className="px-8 py-3 rounded-full border border-gray-200 text-gray-900 font-bold hover:border-gray-400 hover:bg-gray-50 transition-all duration-300"
            >
              Log in
            </Link>

            <Link
              href="/signup"
              className="px-8 py-3 rounded-full bg-[#FCEE21] text-black font-bold shadow-xl hover:bg-[#e6d91e] hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300"
            >
              Register
            </Link>
          </div>


          {/* === MENU BURGER (MOBILE) === */}
          <div className="lg:hidden flex items-center">
            <button 
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} 
              className="text-gray-900 focus:outline-none p-2"
            >
              <div className="w-6 h-5 flex flex-col justify-between">
                <span className={`block h-0.5 w-full bg-current rounded-full transition-all duration-300 ${isMobileMenuOpen ? 'rotate-45 translate-y-2.5' : ''}`}></span>
                <span className={`block h-0.5 w-full bg-current rounded-full transition-all duration-300 ${isMobileMenuOpen ? 'opacity-0' : ''}`}></span>
                <span className={`block h-0.5 w-full bg-current rounded-full transition-all duration-300 ${isMobileMenuOpen ? '-rotate-45 -translate-y-2' : ''}`}></span>
              </div>
            </button>
          </div>

        </div>


        {/* === MENU MOBILE DÉROULANT === */}
        <div className={`lg:hidden absolute top-full left-0 w-full bg-white border-b border-gray-100 shadow-xl transition-all duration-300 overflow-hidden ${
          isMobileMenuOpen ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
        }`}>
          <div className="flex flex-col items-center py-8 space-y-6">
            <Link href="/#about" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-900 font-bold text-lg">About us</Link>
            <Link href="/#services" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-900 font-bold text-lg">Services</Link>
            <Link href="/#contact" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-900 font-bold text-lg">Contact</Link>
            
            <div className="h-px w-10 bg-gray-100 my-2"></div>
            
            <Link href="/login" onClick={() => setIsMobileMenuOpen(false)} className="text-gray-600 font-bold text-lg">Log in</Link>
            <Link 
              href="/register" 
              onClick={() => setIsMobileMenuOpen(false)}
              className="bg-[#FCEE21] text-black px-10 py-3 rounded-full font-bold text-lg shadow-sm"
            >
              Register
            </Link>
          </div>
        </div>

      </nav>
    </>
  )
}
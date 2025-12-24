"use client"
import { useState } from 'react'
import Link from 'next/link'

export default function ContactSection() {
  const [language, setLanguage] = useState('English')

  return (
    // CORRECTION : 
    // 1. Suppression de 'mt-15' (c'est ça qui créait l'espace blanc).
    // 2. Suppression de 'z-150' (non standard), remplacé par 'relative z-10' pour s'assurer qu'il est au-dessus des patterns.
    <footer id="contact" className="w-full bg-[#F5F5F5] text-[#1F2937] py-12 px-4 sm:px-6 lg:px-8 relative z-10">
      <div className="max-w-7xl mx-auto">
        
        {/* GRILLE RESPONSIVE : 
            - 1 colonne sur mobile
            - 2 colonnes sur tablette
            - 4 colonnes sur ordinateur 
        */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          
          {/* 1. Logo and Contact */}
          <div className="space-y-6">
            <div className="flex items-center gap-2">
             <Link href="/landingpage">
              <div>
                {/* Ajout de h-auto w-auto pour éviter les déformations */}
                <img  src="./logo.svg" alt="Logo" className="h-10 w-auto" />
              </div>
              </Link>
            </div>

            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-[#1F2937] mb-3">Contact us</h3>
              <a href="mailto:info@doxa.com" className="block text-gray-700 hover:text-[#714BD2] transition-colors text-sm">
                info@doxa.com
              </a>
              <a href="tel:+123456789" className="block text-gray-700 hover:text-[#714BD2] transition-colors text-sm">
                +1-2345-6789
              </a>
            </div>
          </div>

          {/* 2. Social media */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-[#1F2937]">Our social media</h3>
            <div className="flex items-center gap-4 flex-wrap">
              <a href="#" className="text-gray-800 hover:text-[#1877F2] transition-colors" aria-label="Facebook">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
              </a>
              <a href="#" className="text-gray-800 hover:text-[#0A66C2] transition-colors" aria-label="LinkedIn">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
              </a>
              <a href="#" className="text-gray-800 hover:text-[#1DA1F2] transition-colors" aria-label="Twitter">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>
              </a>
              <a href="#" className="text-gray-800 hover:text-[#714BD2] transition-colors" aria-label="Globe">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
              </a>
            </div>
          </div>

          {/* 3. Useful Links */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-[#1F2937]">Useful Links</h3>
            <div className="space-y-2">
              <a href="#" className="block text-gray-700 hover:text-[#714BD2] transition-colors text-sm">Terms & conditions</a>
              <a href="#" className="block text-gray-700 hover:text-[#714BD2] transition-colors text-sm">Privacy policy</a>
            </div>
          </div>

          {/* 4. Get the app */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-[#1F2937]">Get the app</h3>
            <div className="flex flex-col sm:flex-row lg:flex-col gap-3">
              <a href="#" className="inline-block w-full sm:w-auto">
                <div className="flex items-center justify-center sm:justify-start bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">
                  <svg className="w-7 h-7 mr-3 shrink-0" fill="currentColor" viewBox="0 0 24 24"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.74s2.57-.9 3.8-.48c2.61.92 3.65 3.4 3.65 3.4s-2.03 1.14-2.03 3.5c0 2.76 2.38 3.66 2.38 3.66s-1.66 3.96-2.88 5.55zM12.03 7.25c-.15-2.23 1.66-4.04 3.74-4.25.17 2.28-2.13 4.22-3.74 4.25z"/></svg>
                  <div className="text-left">
                    <div className="text-[0.65rem] leading-tight">Download on the</div>
                    <div className="text-sm font-semibold leading-tight">App Store</div>
                  </div>
                </div>
              </a>
              <a href="#" className="inline-block w-full sm:w-auto">
                <div className="flex items-center justify-center sm:justify-start bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">
                  <svg className="w-6 h-6 mr-3 shrink-0" viewBox="0 0 24 24"><path fill="currentColor" d="M3,20.5V3.5C3,2.91 3.34,2.39 3.84,2.15L13.69,12L3.84,21.85C3.34,21.6 3,21.09 3,20.5M16.81,15.12L6.05,21.34L14.54,12.85L16.81,15.12M20.36,13.08L18.81,12.18L15.45,15.54L17.61,16.78C18.1,17.06 18.7,17.06 19.19,16.78C19.68,16.5 19.68,16.05 19.19,15.77C18.7,15.49 19.68,13.47 20.36,13.08M16.81,8.88L14.54,11.15L6.05,2.66L16.81,8.88M19.19,7.22C18.7,6.94 18.1,6.94 17.61,7.22L15.45,8.46L18.81,11.82L20.36,10.92C20.94,10.59 20.94,10 20.36,9.66C19.78,9.33 19.68,7.5 19.19,7.22Z" /></svg>
                  <div className="text-left">
                    <div className="text-[0.65rem] leading-tight uppercase">GET IT ON</div>
                    <div className="text-sm font-semibold leading-tight">Google Play</div>
                  </div>
                </div>
              </a>
            </div>
          </div>
        </div>

        {/* Bottom section */}
        <div className="flex flex-col-reverse md:flex-row justify-between items-center pt-6 border-t border-gray-300 gap-4">
          <p className="text-sm text-gray-600 text-center md:text-left">
            Copyright © 2025. All rights reserved.
          </p>

          <div className="flex items-center gap-2 text-gray-700 hover:text-gray-900 cursor-pointer">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span className="text-sm font-medium">{language}</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
          </div>
        </div>

      </div>
    </footer>
  )
}
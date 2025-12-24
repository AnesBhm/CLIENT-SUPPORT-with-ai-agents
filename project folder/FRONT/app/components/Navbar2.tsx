"use client"
import Image from "next/image"
import Link from "next/link"
import { useState, useEffect, useRef, ChangeEvent } from "react"
import { useRouter } from "next/navigation"
import {
  BellIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  UserIcon,
  CameraIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

// 1. On ajoute un ID à l'utilisateur pour lier les données
interface UserData {
  id: string; // L'identifiant unique
  name: string;
  email: string;
  role: string;
  avatarUrl: string | null;
}

interface Notification {
  id: number;
  title: string;
  message: string;
  time: string;
  isRead: boolean;
}

// 2. Simulation d'une "Base de données" de notifications par utilisateur
const MOCK_NOTIFICATIONS_DB: Record<string, Notification[]> = {
  "user_1": [ // Notifications pour l'Admin (Merouane)
    { id: 1, title: "Nouveau stagiaire", message: "Amine Houmel a rejoint l'équipe Dev.", time: "Il y a 5 min", isRead: false },
    { id: 2, title: "Validation requise", message: "3 rapports de stage en attente.", time: "Il y a 2h", isRead: false },
    { id: 3, title: "Système", message: "Mise à jour réussie.", time: "Hier", isRead: true },
  ],
  "user_2": [ // Notifications pour un Stagiaire (Exemple)
    { id: 10, title: "Tâche assignée", message: "Votre tuteur a ajouté une tâche.", time: "Il y a 10 min", isRead: false },
    { id: 11, title: "Bienvenue", message: "Bienvenue sur Doxa !", time: "Il y a 2 jours", isRead: true },
  ]
};

export default function DoxaNavbar() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false)
  const [isNotifMenuOpen, setIsNotifMenuOpen] = useState(false)

  const [userData, setUserData] = useState<UserData | null>(null)
  const [profileImage, setProfileImage] = useState<string | null>(null)

  // L'état des notifications commence vide, il sera rempli après le chargement de l'user
  const [notifications, setNotifications] = useState<Notification[]>([])

  const menuRef = useRef<HTMLDivElement>(null)
  const notifRef = useRef<HTMLDivElement>(null)

  const router = useRouter()

  // --- SIMULATION DU CHARGEMENT DES DONNÉES ---
  useEffect(() => {
    const loadData = () => {
      // Étape 1 : On récupère l'utilisateur connecté depuis le localStorage
      const method = localStorage.getItem("user");
      if (method) {
        try {
          const storedUser = JSON.parse(method);
          const currentUser = {
            id: storedUser.id ? String(storedUser.id) : "guest",
            name: storedUser.full_name || storedUser.email || "Utilisateur",
            email: storedUser.email || "",
            role: storedUser.role || "Client",
            avatarUrl: null
          };

          setUserData(currentUser);
          if (currentUser.avatarUrl) setProfileImage(currentUser.avatarUrl);

          // Étape 2 : On charge les notifications (simulation basique pour l'instant)
          const userSpecificNotifs = MOCK_NOTIFICATIONS_DB["user_1"] || [];
          setNotifications(userSpecificNotifs);

        } catch (e) {
          console.error("Erreur parsing user", e);
        }
      }
    };

    loadData();
  }, []);

  // Gestion du scroll
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

  // Click Outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsProfileMenuOpen(false)
      }
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setIsNotifMenuOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleImageUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const imageUrl = URL.createObjectURL(file)
      setProfileImage(imageUrl)
    }
  }

  const handleLogout = () => {
    console.log("Déconnexion...")
    setUserData(null)
    setNotifications([]) // On vide les notifs à la déconnexion
    router.push('/landingpage')
  }

  const markAsRead = (id: number) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, isRead: true } : n))
  }

  // Calcul dynamique
  const unreadCount = notifications.filter(n => !n.isRead).length;

  return (
    <>
      <nav
        className={`fixed top-0 w-full z-50 transition-all duration-300 bg-[#F9FAFB] border-b border-gray-100 h-24 flex items-center ${isScrolled ? 'shadow-sm' : ''
          }`}
      >
        <div className="w-full max-w-7xl mx-auto px-6 flex items-center justify-between">

          {/* GROUPE GAUCHE */}
          <div className="flex items-center gap-10 xl:gap-12">
            <Link href="/" className="flex items-center gap-3 cursor-pointer group select-none">
              <div className="relative w-45 h-40 -ml-25">
                <Image src="/logo.svg" alt="DOXA Logo" fill className="object-contain" priority />
              </div>
            </Link>
            <div className="hidden lg:flex items-center gap-6">
              <div className="h-6 w-px bg-[#B6BBCC] mr-2"></div>
              <Link href="/contact" className="text-gray-500 font-bold text-base hover:text-[#714BD2] transition-colors">
                Contact
              </Link>
            </div>
          </div>

          {/* GROUPE DROITE */}
          <div className="hidden lg:flex items-center gap-6 -mr-25">

            {/* --- NOTIFICATIONS --- */}
            <div className="relative" ref={notifRef}>
              <button
                onClick={() => {
                  setIsNotifMenuOpen(!isNotifMenuOpen);
                  setIsProfileMenuOpen(false);
                }}
                className={`relative p-2.5 rounded-full transition-colors group ${isNotifMenuOpen ? 'bg-white shadow-sm' : 'hover:bg-white'}`}
              >
                <BellIcon className={`w-7 h-7 transition-colors ${isNotifMenuOpen ? 'text-[#714BD2]' : 'text-gray-600 group-hover:text-[#714BD2]'}`} />

                {unreadCount > 0 && (
                  <span className="absolute top-2.5 right-3 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-[#E2E5EB] group-hover:border-white animate-pulse"></span>
                )}
              </button>

              {isNotifMenuOpen && (
                <div className="absolute right-0 mt-4 w-80 sm:w-96 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden transform origin-top-right transition-all animate-fade-in-up z-50">
                  <div className="px-6 py-4 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
                    <h3 className="text-sm font-bold text-gray-900">Notifications</h3>
                    {unreadCount > 0 ? (
                      <span className="bg-[#714BD2] text-white text-[10px] px-2 py-0.5 rounded-full font-bold">
                        {unreadCount} nouvelle(s)
                      </span>
                    ) : (
                      <span className="text-gray-400 text-xs">Tout est lu</span>
                    )}
                  </div>

                  <div className="max-h-[350px] overflow-y-auto">
                    {/* AFFICHAGE CONDITIONNEL : Si l'utilisateur n'est pas chargé ou liste vide */}
                    {!userData ? (
                      <div className="p-8 text-center text-gray-400 text-sm">Chargement...</div>
                    ) : notifications.length > 0 ? (
                      notifications.map((notif) => (
                        <div
                          key={notif.id}
                          onClick={() => markAsRead(notif.id)}
                          className={`p-4 border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition-colors ${!notif.isRead ? 'bg-[#F9FAFB]' : ''}`}
                        >
                          <div className="flex gap-3">
                            <div className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${!notif.isRead ? 'bg-[#714BD2]' : 'bg-gray-300'}`}></div>
                            <div className="flex-1">
                              <p className={`text-sm ${!notif.isRead ? 'font-bold text-gray-900' : 'text-gray-600'}`}>
                                {notif.title}
                              </p>
                              <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                                {notif.message}
                              </p>
                              <div className="flex items-center gap-1 mt-2 text-[10px] text-gray-400">
                                <ClockIcon className="w-3 h-3" />
                                {notif.time}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-8 text-center text-gray-400 text-sm flex flex-col items-center gap-2">
                        <BellIcon className="w-8 h-8 text-gray-200" />
                        Aucune notification pour le moment
                      </div>
                    )}
                  </div>

                  <div className="p-2 border-t border-gray-50 bg-gray-50/30 text-center">
                    <button className="text-xs font-bold text-[#714BD2] hover:underline">
                      Voir tout l'historique
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* --- PROFIL --- */}
            <div className="relative" ref={menuRef}>
              <div className="flex items-center gap-2">
                <div
                  onClick={() => {
                    setIsProfileMenuOpen(!isProfileMenuOpen);
                    setIsNotifMenuOpen(false);
                  }}
                  className="w-12 h-12 rounded-full border-2 border-white shadow-md cursor-pointer overflow-hidden relative bg-gray-200 hover:border-[#FCEE21] transition-all"
                >
                  {profileImage ? (
                    <Image src={profileImage} alt="Profile" fill className="object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400">
                      {userData?.name ? (
                        <span className="text-xl font-bold text-gray-500">{userData.name.charAt(0).toUpperCase()}</span>
                      ) : (
                        <UserIcon className="w-6 h-6" />
                      )}
                    </div>
                  )}
                </div>
              </div>

              {isProfileMenuOpen && (
                <div className="absolute right-0 mt-4 w-64 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden transform origin-top-right transition-all animate-fade-in-up z-50">
                  <div className="px-6 py-4 border-b border-gray-50 bg-gray-50/50">
                    <p className="text-sm font-bold text-gray-900">{userData ? userData.name : "..."}</p>
                    <p className="text-xs text-gray-500 truncate">{userData ? userData.email : ""}</p>
                    {userData?.role && (
                      <span className="text-[10px] uppercase tracking-wider text-[#714BD2] font-semibold mt-1 block">
                        {userData.role}
                      </span>
                    )}
                  </div>

                  <div className="p-2">
                    <Link href="/profile" onClick={() => setIsProfileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-700 rounded-xl hover:bg-gray-50 hover:text-[#714BD2] transition-colors">
                      <UserCircleIcon className="w-5 h-5" />
                      Profil
                    </Link>
                  </div>

                  <div className="p-2 border-t border-gray-50">
                    <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 text-sm font-bold text-red-500 rounded-xl hover:bg-red-50 transition-colors">
                      <ArrowRightOnRectangleIcon className="w-5 h-5" />
                      Déconnexion
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* MOBILE BURGER */}
          <div className="lg:hidden flex items-center">
            {/* ... (Reste inchangé) ... */}
            <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-gray-900 focus:outline-none p-2">
              <div className="w-6 h-5 flex flex-col justify-between">
                <span className={`block h-0.5 w-full bg-current rounded-full transition-all duration-300 ${isMobileMenuOpen ? 'rotate-45 translate-y-2.5' : ''}`}></span>
                <span className={`block h-0.5 w-full bg-current rounded-full transition-all duration-300 ${isMobileMenuOpen ? 'opacity-0' : ''}`}></span>
                <span className={`block h-0.5 w-full bg-current rounded-full transition-all duration-300 ${isMobileMenuOpen ? '-rotate-45 -translate-y-2' : ''}`}></span>
              </div>
            </button>
          </div>
        </div>

        {/* MOBILE MENU */}
        <div className={`lg:hidden absolute top-full left-0 w-full bg-white border-b border-gray-100 shadow-xl transition-all duration-300 overflow-hidden ${isMobileMenuOpen ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
          }`}>
          <div className="flex flex-col items-center py-8 space-y-6">
            <Link href="/contact" className="text-gray-900 font-bold text-lg">Contact</Link>
            <div className="h-px w-10 bg-gray-100 my-2"></div>

            {userData && (
              <div className="text-center">
                <p className="text-gray-900 font-bold">{userData.name}</p>
                <p className="text-sm text-gray-500 mb-2">{userData.email}</p>

                {/* Lien Notifs pour Mobile */}
                <div className="flex items-center justify-center gap-2 text-sm text-[#714BD2] font-bold">
                  <BellIcon className="w-5 h-5" />
                  {unreadCount} Notif(s)
                </div>
              </div>
            )}

            <Link href="/profile" className="text-gray-900 font-bold text-lg">Mon Profil</Link>
            <button onClick={handleLogout} className="text-red-500 font-bold text-lg">Déconnexion</button>
          </div>
        </div>
      </nav>
    </>
  )
}
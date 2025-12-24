"use client"
import React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { authService } from '../lib/services/auth'

export default function LoginPage() {
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState("")
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      // 1. On tente la connexion
      // Note : Vérifie si ton API attend 'username' ou 'email'
      const data = await authService.login({
        username: email, // Si l'API attend "email", change cette clé en email: email
        password: password
      })

      console.log("Réponse API reçue:", data)

      // 2. Vérification du token
      // Si ton API renvoie { token: "..." } au lieu de { access_token: "..." }
      const token = data.access_token || data.token

      if (token) {
        localStorage.setItem("token", token)

        try {
          const user = await authService.getCurrentUser()
          localStorage.setItem("user", JSON.stringify(user))
        } catch (uErr) {
          console.error("Failed to fetch user info", uErr)
        }

        // Redirection vers le client (demande utilisateur)
        router.push("/client")
      } else {
        throw new Error("Le serveur n'a pas renvoyé de jeton (token).")
      }

    } catch (err: any) {
      console.error("Erreur de connexion détaillée:", err)

      // Récupère le message d'erreur du backend s'il existe
      const errorMessage = err.response?.data?.message || err.message || "Login failed"
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative flex flex-col items-center justify-center bg-white text-gray-900 overflow-hidden min-h-screen">

      <div className="mt-40 mb-20 relative z-10 w-full max-w-xl px-6 pt-12 pb-6 backdrop-blur-sm bg-gray-200 rounded-3xl p-8 md:p-12 shadow-lg">

        <div className="relative flex items-center justify-between mb-10">
          <div className="text-left">
            <h2 className="text-4xl font-bold tracking-tight text-gray-900">
              Log in
            </h2>
          </div>

          <div className="absolute w-[200px] -top-[100px] -right-[20px]">
            <img src="/safe 2.svg" alt="Safe icon" />
          </div>
        </div>

        <form onSubmit={handleLogin}>
          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 border border-red-200 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Mail
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Type your mail"
              required
              className="mb-5 block w-full rounded-lg bg-gray-100 px-4 py-3 text-gray-900 placeholder:text-gray-400 focus:ring-2 focus:ring-[#714BD2] focus:outline-none transition-all"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Type your password"
              required
              className="mb-5 block w-full rounded-lg bg-gray-100 px-4 py-3 text-gray-900 placeholder:text-gray-400 focus:ring-2 focus:ring-[#714BD2] focus:outline-none transition-all"
            />
          </div>

          <div className="flex flex-col items-center justify-between gap-2 text-sm">
            <Link href="/forgot-password" className="font-medium text-[#714BD2] hover:text-indigo-500">
              Forgot Password?
            </Link>
            <div className="text-gray-500">
              Don’t have an account?{' '}
              <Link href="/signup" className="font-medium text-[#714BD2] hover:text-indigo-500">
                Sign up
              </Link>
            </div>
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex w-full justify-center rounded-full bg-[#FCEE21] px-3 py-3 text-sm font-bold text-black shadow-sm hover:bg-[#e6d91e] transition-colors disabled:opacity-50"
            >
              {loading ? "Logging in..." : "Submit"}
            </button>
          </div>
        </form>
      </div>

      <div className="relative flex w-full mb-40 justify-center">
        <div className="relative w-full h-24 md:h-32">
          <img
            src="/Group 359.svg"
            alt="Decorative background"
            className="w-full object-cover"
          />
        </div>
      </div>
    </div>
  )
}
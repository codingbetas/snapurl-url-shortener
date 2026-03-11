"use client"

import { useState } from "react"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000"

console.log("API:", API_BASE)
export default function Home() {
  const [url, setUrl] = useState("")
  const [customCode, setCustomCode] = useState("")
  const [expiry, setExpiry] = useState("")
  const [shortUrl, setShortUrl] = useState("")
  const [stats, setStats] = useState<any>(null)


  const shorten = async () => {
    const res = await fetch(`${API_BASE}/shorten`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        original_url: url,
        custom_code: customCode || null,
        expires_in_days: expiry ? parseInt(expiry) : null
      })
    })

    const data = await res.json()
    if (!res.ok) {
      alert(data.detail)
      return
    }

    setShortUrl(data.short_url)
    setStats(null)
  }

  const copyLink = () => {
    navigator.clipboard.writeText(shortUrl)
    // You could replace this alert with a toast notification for a better feel
    alert("Copied to clipboard!")
  }

  const getStats = async () => {
    const code = shortUrl.split("/").pop()
    const res = await fetch(`${API_BASE}/stats/${code}`)
    const data = await res.json()
    setStats(data)
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-purple-900 to-slate-900 p-4">
      
      {/* Glassmorphism Card */}
      <div className="backdrop-blur-xl bg-white/10 border border-white/20 p-8 rounded-3xl shadow-2xl w-full max-w-[440px] transition-all duration-500">
        
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 text-center mb-8 tracking-tight">
          SnapURL
        </h1>

        <div className="space-y-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Paste long URL..."
              className="w-full bg-white/5 border border-white/10 p-3 px-4 rounded-2xl text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="Custom alias"
              className="bg-white/5 border border-white/10 p-3 rounded-2xl text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
              value={customCode}
              onChange={(e) => setCustomCode(e.target.value)}
            />
            <input
              type="number"
              placeholder="Days until expiry"
              className="bg-white/5 border border-white/10 p-3 rounded-2xl text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
              value={expiry}
              onChange={(e) => setExpiry(e.target.value)}
            />
          </div>

          <button
            onClick={shorten}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold p-3.5 rounded-2xl shadow-lg shadow-purple-500/20 transform transition active:scale-95"
          >
            Generate Link
          </button>
        </div>

        {/* Result Section (Bento Style) */}
        {shortUrl && (
          <div className="mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="p-5 bg-white/5 border border-white/10 rounded-2xl space-y-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-purple-400 mb-1">Your Short Link</p>
                <a
                  href={shortUrl}
                  target="_blank"
                  className="text-lg text-white font-medium hover:text-blue-400 break-all transition-colors"
                >
                  {shortUrl}
                </a>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={copyLink}
                  className="flex-1 bg-white/10 hover:bg-white/20 text-white p-2.5 rounded-xl border border-white/10 transition-all"
                >
                  Copy
                </button>
                <button
                  onClick={getStats}
                  className="flex-1 bg-purple-600/20 hover:bg-purple-600/40 text-purple-300 p-2.5 rounded-xl border border-purple-500/30 transition-all"
                >
                  View Stats
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Stats Section (Bento Detail) */}
        {stats && (
          <div className="mt-4 p-5 bg-slate-900/50 border border-white/5 rounded-2xl text-sm text-slate-300 space-y-2 animate-in fade-in zoom-in-95 duration-300">
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-slate-500">Clicks</span>
              <span className="text-white font-mono">{stats.clicks}</span>
            </div>
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-slate-500">Created</span>
              <span className="text-white font-mono">{new Date(stats.created_at).toLocaleDateString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">IP Logged</span>
              <span className="text-white font-mono">{stats.ip_address || "None"}</span>
            </div>
          </div>
        )}

      </div>
    </main>
  )
}

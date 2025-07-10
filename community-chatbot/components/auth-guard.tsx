"use client"

import type React from "react"

import { useSession } from "next-auth/react"
import { useRouter, usePathname } from "next/navigation"
import { useEffect } from "react"
import { Loader2 } from "lucide-react"

const PUBLIC_ROUTES = ["/auth/signin", "/auth/signup"]

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession()
  const router = useRouter()
  const pathname = usePathname()

  const isPublicRoute = PUBLIC_ROUTES.includes(pathname)

  useEffect(() => {
    if (status === "loading") return // Still loading

    if (!session && !isPublicRoute) {
      router.push("/auth/signin")
    }
  }, [session, status, router, isPublicRoute])

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (!session && !isPublicRoute) {
    return null
  }

  return <>{children}</>
}

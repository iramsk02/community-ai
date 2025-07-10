import type { NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"
import bcrypt from "bcryptjs"

// This would typically connect to your database
// For now, we'll use a simple in-memory store
const users: Array<{
  id: string
  name: string
  email: string
  password: string
  image?: string
}> = []

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        // Find user in our simple store
        const user = users.find((u) => u.email === credentials.email)

        if (!user) {
          return null
        }

        // Verify password
        const isPasswordValid = await bcrypt.compare(credentials.password, user.password)

        if (!isPasswordValid) {
          return null
        }

        return {
          id: user.id,
          name: user.name,
          email: user.email,
          image: user.image,
        }
      },
    }),
  ],
  pages: {
    signIn: "/auth/signin",
    signUp: "/auth/signup",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
      }
      return session
    },
    async signIn({ user, account, profile }) {
      if (account?.provider === "google") {
        // Auto-create user for Google sign-in
        const existingUser = users.find((u) => u.email === user.email)
        if (!existingUser) {
          users.push({
            id: crypto.randomUUID(),
            name: user.name || "",
            email: user.email || "",
            password: "", // No password for Google users
            image: user.image,
          })
        }
      }
      return true
    },
  },
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET,
}

// Helper function to create a new user
export async function createUser(name: string, email: string, password: string) {
  // Check if user already exists
  const existingUser = users.find((u) => u.email === email)
  if (existingUser) {
    throw new Error("User already exists")
  }

  // Hash password
  const hashedPassword = await bcrypt.hash(password, 12)

  // Create new user
  const newUser = {
    id: crypto.randomUUID(),
    name,
    email,
    password: hashedPassword,
  }

  users.push(newUser)
  return newUser
}

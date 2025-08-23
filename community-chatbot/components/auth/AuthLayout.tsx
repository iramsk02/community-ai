"use client"

import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"

export function AuthLayout({
    title,
    description,
    children,
}: LayoutProps) {
    return (
        <div className="flex justify-center items-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4 min-h-screen">
            <Card className="w-full max-w-md">
                <CardHeader className="space-y-1 text-center">
                    <div className="flex justify-center items-center mb-4">
                        <div className="bg-blue-600 p-3 rounded-full text-white">
                            <span className="font-bold text-2xl">MC</span>
                        </div>
                    </div>
                    <CardTitle className="font-bold text-2xl">
                        {title}
                    </CardTitle>
                    <CardDescription>
                        {description}
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {children}
                </CardContent>
            </Card>
        </div>
    )
}

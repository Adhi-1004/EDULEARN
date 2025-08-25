import * as React from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { FancyButton } from "./fancy-button"

export function AuthModal({
  isOpen = false,
  onClose = () => {},
  initialMode = "login",
  onLogin = () => {},
}: {
  isOpen?: boolean
  onClose?: () => void
  initialMode?: "login" | "register"
  onLogin?: (user: { email: string; role: "student" | "teacher" }) => void
}) {
  const [mode, setMode] = React.useState<"login" | "register">(initialMode)
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [role, setRole] = React.useState<"student" | "teacher">("student")

  React.useEffect(() => {
    setMode(initialMode)
  }, [initialMode])

  return (
    <Dialog open={isOpen} onOpenChange={(o) => (!o ? onClose() : null)}>
      <DialogContent className="bg-[#0b0f1a] text-white border-white/10">
        <DialogHeader>
          <DialogTitle>{mode === "login" ? "Sign in to EduLearn" : "Create your account"}</DialogTitle>
          <DialogDescription className="text-white/70">
            {mode === "login" ? "Welcome back! Enter your details below." : "Join the next generation of learners."}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 pt-2">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-white">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-white/5 border-white/10 text-white placeholder:text-white/40"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-white">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="********"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-white/5 border-white/10 text-white placeholder:text-white/40"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-white">Role</Label>
            <div className="flex gap-2">
              <FancyButton variant={role === "student" ? "default" : "outline"} onClick={() => setRole("student")}>
                Student
              </FancyButton>
              <FancyButton variant={role === "teacher" ? "default" : "outline"} onClick={() => setRole("teacher")}>
                Teacher
              </FancyButton>
            </div>
          </div>

          <FancyButton
            className="w-full"
            onClick={() => {
              // Demo: return the "logged in" user
              onLogin({ email, role })
            }}
          >
            {mode === "login" ? "Sign In" : "Create Account"}
          </FancyButton>

          <p className="text-center text-sm text-white/70">
            {mode === "login" ? (
              <>
                Don&apos;t have an account?{" "}
                <button onClick={() => setMode("register")} className="underline underline-offset-4 hover:text-white">
                  Create one
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button onClick={() => setMode("login")} className="underline underline-offset-4 hover:text-white">
                  Sign in
                </button>
              </>
            )}
          </p>
        </div>
      </DialogContent>
    </Dialog>
  )
}

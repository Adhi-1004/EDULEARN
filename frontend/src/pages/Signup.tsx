import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useToast } from "../contexts/ToastContext";
import Card from "../components/ui/Card";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import AnimatedBackground from "../components/AnimatedBackground";
import api from "../utils/api";
import { ANIMATION_VARIANTS } from "../utils/constants";

interface SignupProps {
  setUser: (user: any) => void;
}

const Signup: React.FC<SignupProps> = ({ setUser }) => {
  const { error, success } = useToast();
  const navigate = useNavigate();
  
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [role, setRole] = useState<"student" | "teacher" | "admin">("student");

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      error("Signup Failed", "Passwords do not match");
      return;
    }
    
    if (password.length < 6) {
      error("Signup Failed", "Password must be at least 6 characters");
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await api.post("/auth/register", {
        username: name, // Backend expects 'username' field
        email,
        password,
        role,
        name // Also include name as optional field
      });
      
      if (response.data.success) {
        const userData = {
          ...response.data.user,
          role: response.data.user.role || "student"
        };
        
        // Store user data and token
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("access_token", response.data.access_token);
        
        // Set user in context
        setUser(userData);
        
        // Redirect based on role
        switch (userData.role) {
          case "teacher":
            navigate("/teacher-dashboard");
            break;
          case "admin":
            navigate("/admin-dashboard");
            break;
          default:
            navigate("/dashboard");
            break;
        }
        
        success("Signup Successful!", `Welcome to LearnAI, ${userData.name || userData.email}!`);
      } else {
        error("Signup Failed", response.data.message || "Registration failed");
      }
    } catch (err: any) {
      console.error("Signup error:", err);
      const errorMessage = err.response?.data?.detail || "Registration failed";
      // Ensure error message is a string, not an object
      const message = typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage);
      error("Signup Failed", message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <AnimatedBackground />
      <div className="min-h-screen pt-20 px-4 flex items-center justify-center relative z-10">
        <motion.div
          variants={ANIMATION_VARIANTS.fadeIn}
          initial="initial"
          animate="animate"
          className="w-full max-w-md"
        >
          <Card className="p-8">
            <motion.div
              variants={ANIMATION_VARIANTS.slideDown}
              className="text-center mb-8"
            >
              <h1 className="text-3xl font-bold text-purple-200 mb-2">
                Create Account
              </h1>
              <p className="text-purple-300">
                Join our learning platform
              </p>
            </motion.div>

            <form onSubmit={handleSignup} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-purple-300 mb-2">
                  I am a:
                </label>
                <div className="grid grid-cols-3 gap-2 mb-4">
                  <Button
                    type="button"
                    variant={role === "student" ? "primary" : "outline"}
                    onClick={() => setRole("student")}
                    className="py-2"
                  >
                    Student
                  </Button>
                  <Button
                    type="button"
                    variant={role === "teacher" ? "primary" : "outline"}
                    onClick={() => setRole("teacher")}
                    className="py-2"
                  >
                    Teacher
                  </Button>
                  <Button
                    type="button"
                    variant={role === "admin" ? "primary" : "outline"}
                    onClick={() => setRole("admin")}
                    className="py-2"
                  >
                    Admin
                  </Button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-purple-300 mb-2">
                  Full Name
                </label>
                <Input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your full name"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-purple-300 mb-2">
                  Email
                </label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-purple-300 mb-2">
                  Password
                </label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-purple-300 mb-2">
                  Confirm Password
                </label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full py-3"
                variant="primary"
              >
                {loading ? "Creating Account..." : "Create Account"}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-purple-300">
                Already have an account?{" "}
                <Link to="/login" className="text-purple-400 hover:text-purple-300 font-medium">
                  Sign in
                </Link>
              </p>
            </div>
          </Card>
        </motion.div>
      </div>
    </>
  );
};

export default Signup;
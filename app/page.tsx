"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function Home() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const endpoint = isLogin ? "/api/auth/login" : "/api/auth/register";
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        router.push("/dashboard");
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert("An error occurred during authentication");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center p-4">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 w-full max-w-md shadow-xl border border-white/20">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            {isLogin ? "Welcome Back!" : "Create Account"}
          </h1>
          <p className="text-gray-200">
            {isLogin ? "Login to continue" : "Sign up to get started"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-gray-200 text-sm font-medium">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:border-white/30 transition duration-200"
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-gray-200 text-sm font-medium">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:border-white/30 transition duration-200"
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-lg bg-white text-purple-600 font-semibold hover:bg-gray-100 transition duration-200"
          >
            {isLogin ? "Login" : "Sign Up"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-gray-200 hover:text-white transition duration-200"
          >
            {isLogin
              ? "Don't have an account? Sign up"
              : "Already have an account? Login"}
          </button>
        </div>
      </div>
    </div>
  );
}

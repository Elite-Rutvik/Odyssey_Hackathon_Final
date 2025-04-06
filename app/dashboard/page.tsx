"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  HomeIcon,
  ChartBarIcon,
  CheckBadgeIcon,
  ChatBubbleLeftRightIcon,
  BellIcon,
  UserCircleIcon,
  DocumentChartBarIcon,
  ClipboardDocumentCheckIcon,
  ShieldExclamationIcon,
} from "@heroicons/react/24/outline";
import DashboardScreen from "../components/screens/DashboardScreen";
import AnalyticsScreen from "../components/screens/AnalyticsScreen";
import VerifyScreen from "../components/screens/VerifyScreen";
import ChatScreen from "../components/screens/ChatScreen";
import SettingsScreen from "../components/screens/SettingsScreen";
import SummaryScreen from "../components/screens/SummaryScreen";
import GeneratingChecklistScreen from "../components/screens/GeneratingChecklistScreen";
import ContractRisksScreen from "../components/screens/ContractRisksScreen";

export default function Dashboard() {
  const router = useRouter();
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState("Dashboard");

  const menuItems = [
    { name: "Dashboard", icon: HomeIcon, href: "#dashboard" },
    { name: "Analytics", icon: ChartBarIcon, href: "#analytics" },
    { name: "Verify", icon: CheckBadgeIcon, href: "#verify" },
    { name: "Chat", icon: ChatBubbleLeftRightIcon, href: "#chat" },
    { name: "Summary", icon: DocumentChartBarIcon, href: "#summary" },
    {
      name: "Generating Checklist",
      icon: ClipboardDocumentCheckIcon,
      href: "#checklist",
    },
    { name: "Contract Risks", icon: ShieldExclamationIcon, href: "#risks" },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case "Dashboard":
        return <DashboardScreen />;
      case "Analytics":
        return <AnalyticsScreen />;
      case "Verify":
        return <VerifyScreen />;
      case "Chat":
        return <ChatScreen />;
      case "Summary":
        return <SummaryScreen />;
      case "Settings":
        return <SettingsScreen />;
      case "Generating Checklist":
        return <GeneratingChecklistScreen />;
      case "Contract Risks":
        return <ContractRisksScreen />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-red-50 to-white flex">
      {/* Sidebar */}
      <div
        className={`${
          isSidebarOpen ? "w-64" : "w-20"
        } bg-red-50/30 backdrop-blur-sm border-r border-red-100 transition-all duration-300 shadow-lg`}
      >
        <div className="p-4">
          <div className="flex items-center justify-between">
            {isSidebarOpen && (
              <span className="text-xl font-bold text-black">Odyssey</span>
            )}
            <button
              onClick={() => setSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-lg bg-gray-100 text-black hover:bg-red-50 transition-all duration-300"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          </div>
        </div>
        <nav className="mt-8">
          {menuItems.map((item) => (
            <a
              key={item.name}
              href={item.href}
              onClick={(e) => {
                e.preventDefault();
                setActiveTab(item.name);
              }}
              className={`flex items-center px-4 py-3 text-black hover:bg-red-50 transition-colors ${
                activeTab === item.name ? "bg-red-50" : ""
              }`}
            >
              <item.icon className="w-6 h-6 text-red-500" />
              {isSidebarOpen && <span className="ml-3">{item.name}</span>}
            </a>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1">
        {/* Top Navbar */}
        <nav className="bg-white border-b border-gray-200 shadow-sm">
          <div className="px-4 h-16">
            <div className="flex items-center justify-between h-full">
              <div className="flex items-center space-x-4">
                <span className="text-xl font-bold text-black">
                  Welcome Back
                </span>
              </div>
              <div className="flex items-center space-x-4">
                <button className="p-2 rounded-lg bg-gray-100 hover:bg-red-50 transition-all duration-300">
                  <BellIcon className="w-6 h-6 text-red-500" />
                </button>
                <button className="p-2 rounded-lg bg-gray-100 hover:bg-red-50 transition-all duration-300">
                  <UserCircleIcon className="w-6 h-6 text-red-500" />
                </button>
                <button
                  onClick={() => router.push("/")}
                  className="px-4 py-2 rounded-lg bg-red-100 text-black hover:bg-red-200 transition-all duration-300 shadow-sm hover:shadow-md"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="p-8">{renderContent()}</main>
      </div>
    </div>
  );
}

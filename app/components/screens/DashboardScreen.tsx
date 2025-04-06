import { ArrowTrendingUpIcon, BoltIcon } from "@heroicons/react/24/outline";

export default function DashboardScreen() {
  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-12">
        <h1 className="text-5xl font-extrabold text-gray-900 mb-4 tracking-tight">
          RFP Analysis Platform
        </h1>
        <p className="text-xl text-gray-600 font-light">
          Automating government contract proposal analysis with AI
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
        <div className="bg-gradient-to-br from-red-50 via-red-100 to-red-50 p-8 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 border border-red-200">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Current Process
          </h2>
          <div className="flex justify-center mb-6">
            <ArrowTrendingUpIcon className="w-16 h-16 text-red-500" />
          </div>
          <p className="text-lg text-gray-600">Manual RFP Analysis</p>
        </div>

        <div className="bg-gradient-to-br from-green-50 via-green-100 to-green-50 p-8 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 border border-green-200">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Our Solution
          </h2>
          <div className="flex justify-center mb-6">
            <BoltIcon className="w-16 h-16 text-green-500" />
          </div>
          <p className="text-lg text-gray-600">AI-Powered Automation</p>
        </div>
      </div>

      <div className="mt-12 text-left">
        <p className="text-sm text-gray-500">
          Get started by selecting a menu option from the sidebar
        </p>
      </div>
    </div>
  );
}

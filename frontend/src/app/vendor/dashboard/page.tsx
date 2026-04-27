export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-slate-500">Store Status:</span>
          <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-green-500">
            <span className="inline-block h-4 w-4 transform translate-x-6 rounded-full bg-white transition" />
          </button>
        </div>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">Orders Today</h3>
          <div className="mt-2 text-3xl font-bold">12</div>
          <p className="text-xs text-slate-400 mt-1">+2 from yesterday</p>
        </div>
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">Revenue Today</h3>
          <div className="mt-2 text-3xl font-bold">₦45,000</div>
        </div>
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">Total Orders</h3>
          <div className="mt-2 text-3xl font-bold">1,245</div>
        </div>
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">Catalogue Items</h3>
          <div className="mt-2 text-3xl font-bold">34</div>
        </div>
      </div>
      
      <div className="rounded-xl border bg-white shadow-sm mt-8">
        <div className="border-b px-6 py-4">
          <h3 className="text-lg font-medium">Recent Orders</h3>
        </div>
        <div className="p-6">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 rounded-t-lg">
              <tr>
                <th className="px-4 py-3">Order ID</th>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Items</th>
                <th className="px-4 py-3">Total</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {/* Dummy rows */}
              <tr>
                <td className="px-4 py-4 font-medium">#VNZ-1045</td>
                <td className="px-4 py-4 text-slate-500">10 mins ago</td>
                <td className="px-4 py-4">2x Jollof Rice, 1x Coke</td>
                <td className="px-4 py-4">₦4,500</td>
                <td className="px-4 py-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    Preparing
                  </span>
                </td>
              </tr>
              <tr>
                <td className="px-4 py-4 font-medium">#VNZ-1044</td>
                <td className="px-4 py-4 text-slate-500">45 mins ago</td>
                <td className="px-4 py-4">1x Fried Rice</td>
                <td className="px-4 py-4">₦2,500</td>
                <td className="px-4 py-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Out for delivery
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
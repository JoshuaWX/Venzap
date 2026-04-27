export default function EarningsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Earnings</h1>
        <select className="border rounded-md px-3 py-1.5 text-sm bg-white">
          <option>This Month</option>
          <option>Last Month</option>
          <option>All Time</option>
        </select>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">Total Earned</h3>
          <div className="mt-2 text-3xl font-bold text-green-600">₦450,000</div>
        </div>
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">This Month</h3>
          <div className="mt-2 text-3xl font-bold">₦120,500</div>
        </div>
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-500">Pending Escrow</h3>
          <div className="mt-2 text-3xl font-bold text-orange-500">₦12,500</div>
          <p className="text-xs text-slate-400 mt-1">Releases on delivery</p>
        </div>
      </div>

      <div className="rounded-xl border bg-white shadow-sm mt-8">
        <div className="border-b px-6 py-4">
          <h3 className="text-lg font-medium">Transaction History</h3>
        </div>
        <div className="p-6">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 rounded-t-lg">
              <tr>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Description</th>
                <th className="px-4 py-3">Order Ref</th>
                <th className="px-4 py-3 text-right">Amount</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              <tr>
                <td className="px-4 py-4 text-slate-500">Today, 2:30 PM</td>
                <td className="px-4 py-4">Order Payout</td>
                <td className="px-4 py-4 font-mono text-xs">VNZ-2846</td>
                <td className="px-4 py-4 text-right text-green-600 font-medium">+₦4,500</td>
                <td className="px-4 py-4">
                  <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-md">Released</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
export default function OrdersPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Orders</h1>
        <div className="bg-slate-100 p-1 rounded-lg flex text-sm font-medium">
          <button className="px-4 py-1.5 rounded-md bg-white shadow-sm text-slate-900">All</button>
          <button className="px-4 py-1.5 text-slate-500 hover:text-slate-900">Pending</button>
          <button className="px-4 py-1.5 text-slate-500 hover:text-slate-900">Preparing</button>
          <button className="px-4 py-1.5 text-slate-500 hover:text-slate-900">Delivered</button>
        </div>
      </div>

      <div className="grid gap-4">
        <div className="rounded-xl border bg-white shadow-sm p-6 flex flex-col md:flex-row md:items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg">#VNZ-2847</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                Pending
              </span>
            </div>
            <p className="text-sm text-slate-500">12 Lagos Street, Yaba • 5 mins ago</p>
            <div className="text-sm font-medium pt-2">
              1x Jollof Rice, 1x Coke (₦2,000) + ₦500 Delivery = ₦2,500 Total
            </div>
          </div>
          <div className="mt-4 md:mt-0 flex space-x-2">
            <button className="px-4 py-2 border rounded-md text-sm font-medium hover:bg-slate-50">Cancel</button>
            <button className="px-4 py-2 bg-slate-900 text-white rounded-md text-sm font-medium hover:bg-slate-800">
              Accept & Prepare
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
export default function ProfilePage() {
  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Profile & Settings</h1>
      
      <div className="rounded-xl border bg-white shadow-sm overflow-hidden">
        <div className="p-6 space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-medium border-b pb-2">Business Details</h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Business Name</label>
                <input type="text" className="w-full border rounded-md px-3 py-2 text-sm" defaultValue="Mama Tunde's Kitchen" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Vendor Type</label>
                <select className="w-full border rounded-md px-3 py-2 text-sm bg-white">
                  <option value="food">Food</option>
                  <option value="grocery">Grocery</option>
                  <option value="pharmacy">Pharmacy</option>
                  <option value="fashion">Fashion</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Phone Number</label>
                <input type="text" className="w-full border rounded-md px-3 py-2 text-sm" defaultValue="08012345678" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-700">Email Address</label>
                <input type="email" disabled className="w-full border rounded-md px-3 py-2 text-sm bg-slate-50 text-slate-500" defaultValue="vendor@venzap.ng" />
              </div>
            </div>
            <div className="space-y-1.5 mt-4">
              <label className="text-sm font-medium text-slate-700">Business Address</label>
              <textarea className="w-full border rounded-md px-3 py-2 text-sm" rows={3} defaultValue="12 Vendor Street, Ikeja, Lagos"></textarea>
            </div>
          </div>
          
          <div className="space-y-4 mt-6">
            <h3 className="text-lg font-medium border-b pb-2">Delivery Settings</h3>
            <div className="space-y-1.5 w-1/2">
              <label className="text-sm font-medium text-slate-700">Default Delivery Fee (₦)</label>
              <input type="number" className="w-full border rounded-md px-3 py-2 text-sm" defaultValue="500" />
            </div>
          </div>
          
          <div className="pt-4 border-t flex justify-end">
            <button className="bg-slate-900 text-white px-5 py-2.5 rounded-md text-sm font-medium hover:bg-slate-800">
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
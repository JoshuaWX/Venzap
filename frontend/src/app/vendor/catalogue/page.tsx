export default function CataloguePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Catalogue</h1>
        <button className="bg-slate-900 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-slate-800">
          + Add Item
        </button>
      </div>

      <div className="rounded-xl border bg-white shadow-sm">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b">
            <tr>
              <th className="px-6 py-4">Item</th>
              <th className="px-6 py-4">Category</th>
              <th className="px-6 py-4">Price</th>
              <th className="px-6 py-4">Available</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            <tr>
              <td className="px-6 py-4">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">🍛</span>
                  <div>
                    <div className="font-medium">Jollof Rice & Chicken</div>
                    <div className="text-xs text-slate-500">Classic Nigerian Jollof</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">Food</td>
              <td className="px-6 py-4 font-medium">₦2,500</td>
              <td className="px-6 py-4">
                <button className="relative inline-flex h-5 w-9 items-center rounded-full bg-green-500 transition-colors">
                  <span className="inline-block h-3 w-3 transform translate-x-5 rounded-full bg-white transition" />
                </button>
              </td>
              <td className="px-6 py-4 text-right">
                <button className="text-blue-600 hover:text-blue-800 mr-3 text-sm font-medium">Edit</button>
                <button className="text-red-600 hover:text-red-800 text-sm font-medium">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center bg-white text-slate-900">
      {/* Header */}
      <header className="w-full flex justify-between items-center px-10 py-6 border-b">
        <h1 className="text-2xl font-bold tracking-tighter text-blue-600">Venzap</h1>
        <div className="space-x-4">
          <Link href="/vendor/login" className="text-sm font-medium hover:text-blue-600">Login</Link>
          <Link href="/vendor/register" className="px-5 py-2.5 rounded-full bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition">
            Register Business
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="w-full max-w-4xl mt-24 text-center px-6 flex flex-col items-center">
        <h2 className="text-5xl md:text-6xl font-extrabold tracking-tight leading-tight">
          Get Any Local Business <br /><span className="text-blue-600">Online in Minutes</span>
        </h2>
        <p className="mt-6 text-xl text-slate-500 max-w-2xl">
          Venzap connects your customers through Telegram. No app download required. Seamless payments. Start free.
        </p>
        
        <div className="mt-10 flex space-x-4">
          <Link href="/vendor/register" className="px-8 py-3.5 rounded-full bg-blue-600 text-white text-lg font-semibold shadow-lg shadow-blue-200 hover:bg-blue-700 transition transform hover:-translate-y-1">
            Register for Free
          </Link>
        </div>
      </section>

      {/* How it works */}
      <section className="w-full max-w-6xl mt-32 px-6 grid md:grid-cols-3 gap-12 text-center pb-24">
        <div>
          <div className="w-16 h-16 mx-auto bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center text-2xl font-bold mb-6">1</div>
          <h3 className="text-xl font-bold">Create Account</h3>
          <p className="mt-3 text-slate-500">Sign up and build your catalogue in 5 minutes. Food, grocery, pharmacy & more supported.</p>
        </div>
        <div>
          <div className="w-16 h-16 mx-auto bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center text-2xl font-bold mb-6">2</div>
          <h3 className="text-xl font-bold">Share Your Link</h3>
          <p className="mt-3 text-slate-500">Customers chat with our AI over Telegram to place orders seamlessly. No app needed.</p>
        </div>
        <div>
          <div className="w-16 h-16 mx-auto bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center text-2xl font-bold mb-6">3</div>
          <h3 className="text-xl font-bold">Get Paid Instantly</h3>
          <p className="mt-3 text-slate-500">Receive orders in real-time on your dashboard. Payments hit escrow immediately upon order.</p>
        </div>
      </section>
    </main>
  );
}
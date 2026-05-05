'use client';

import { motion } from 'framer-motion';
import { Calendar, Clock, User, Mail, Phone } from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';

export default function ScheduleDemo() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    userType: 'vendor',
    date: '',
    time: '',
  });

  const [submitted, setSubmitted] = useState(false);

  const availableTimes = ['9:00 AM', '10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM', '4:00 PM'];
  
  const upcomingDates = Array.from({ length: 14 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() + i + 1);
    return date;
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    // Here you would normally send data to your backend
    console.log('Form submitted:', formData);
    setTimeout(() => {
      setSubmitted(false);
      setFormData({ name: '', email: '', phone: '', company: '', userType: 'vendor', date: '', time: '' });
    }, 3000);
  };

  return (
    <main className="bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-background/80 border-b border-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-primary">VENZAP</Link>
          <Link href="/" className="text-foreground/60 hover:text-foreground transition">← Back</Link>
        </div>
      </nav>

      <div className="pt-24 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              <span className="bg-gradient-to-r from-orange-400 to-orange-600 bg-clip-text text-transparent">
                Schedule Your Demo
              </span>
            </h1>
            <p className="text-xl text-foreground/60">
              Let our team show you how VENZAP can transform your business. It&apos;s free and takes just 30 minutes.
            </p>
          </motion.div>

          {/* Main Form Container */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid md:grid-cols-3 gap-8"
          >
            {/* Form */}
            <div className="md:col-span-2">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Name */}
                <div>
                  <label className="block text-sm font-bold mb-2">Full Name</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Your name"
                    required
                    className="w-full px-4 py-3 rounded-lg border border-border bg-input text-foreground placeholder-foreground/40 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-bold mb-2">Email Address</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="your@email.com"
                    required
                    className="w-full px-4 py-3 rounded-lg border border-border bg-input text-foreground placeholder-foreground/40 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                  />
                </div>

                {/* Phone */}
                <div>
                  <label className="block text-sm font-bold mb-2">Phone Number</label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="+234 (0)8..."
                    required
                    className="w-full px-4 py-3 rounded-lg border border-border bg-input text-foreground placeholder-foreground/40 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                  />
                </div>

                {/* Company */}
                <div>
                  <label className="block text-sm font-bold mb-2">Business/Shop Name</label>
                  <input
                    type="text"
                    name="company"
                    value={formData.company}
                    onChange={handleInputChange}
                    placeholder="Your business name"
                    className="w-full px-4 py-3 rounded-lg border border-border bg-input text-foreground placeholder-foreground/40 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                  />
                </div>

                {/* User Type */}
                <div>
                  <label className="block text-sm font-bold mb-2">I am a...</label>
                  <select
                    name="userType"
                    value={formData.userType}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                  >
                    <option value="vendor">Vendor / Seller</option>
                    <option value="partner">Partner / Influencer</option>
                    <option value="investor">Investor</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                {/* Date */}
                <div>
                  <label className="block text-sm font-bold mb-2">Preferred Date</label>
                  <select
                    name="date"
                    value={formData.date}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                  >
                    <option value="">Select a date</option>
                    {upcomingDates.map((date) => (
                      <option key={date.toISOString()} value={date.toISOString().split('T')[0]}>
                        {date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Time */}
                <div>
                  <label className="block text-sm font-bold mb-2">Preferred Time (WAT)</label>
                  <select
                    name="time"
                    value={formData.time}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all"
                  >
                    <option value="">Select a time</option>
                    {availableTimes.map((time) => (
                      <option key={time} value={time}>{time}</option>
                    ))}
                  </select>
                </div>

                {/* Submit Button */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="submit"
                  className="w-full px-6 py-4 bg-primary text-primary-foreground rounded-lg font-bold text-lg hover:bg-primary/90 transition-all shadow-lg shadow-primary/20"
                >
                  {submitted ? 'Demo Scheduled! ✓' : 'Schedule My Demo'}
                </motion.button>
              </form>
            </div>

            {/* Sidebar Info */}
            <div className="space-y-6">
              {/* What to Expect */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="p-6 rounded-xl bg-card border border-border"
              >
                <h3 className="font-bold text-lg mb-4">What to Expect</h3>
                <ul className="space-y-3 text-sm text-foreground/70">
                  <li className="flex gap-3">
                    <Clock className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                    <span>30-minute call with our team</span>
                  </li>
                  <li className="flex gap-3">
                    <Calendar className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                    <span>Platform walkthrough & Q&A</span>
                  </li>
                  <li className="flex gap-3">
                    <User className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                    <span>Personalized business recommendations</span>
                  </li>
                </ul>
              </motion.div>

              {/* Why VENZAP */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="p-6 rounded-xl bg-gradient-to-br from-orange-500/10 to-orange-600/10 border border-orange-500/20"
              >
                <h3 className="font-bold text-lg mb-4">Why VENZAP?</h3>
                <ul className="space-y-2 text-sm text-foreground/70">
                  <li>✓ Zero commission during launch</li>
                  <li>✓ 10-minute seller onboarding</li>
                  <li>✓ Multi-channel from day one</li>
                  <li>✓ Instant bank payouts</li>
                  <li>✓ Nigerian-first approach</li>
                </ul>
              </motion.div>

              {/* Contact */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                className="p-6 rounded-xl bg-card border border-border"
              >
                <h3 className="font-bold text-lg mb-4">Need Help?</h3>
                <p className="text-sm text-foreground/70 mb-3">
                  Prefer to chat? Reach us on Telegram or email.
                </p>
                <div className="space-y-2 text-sm">
                  <a href="mailto:demo@venzap.com" className="text-primary hover:underline flex items-center gap-2">
                    <Mail className="w-4 h-4" /> demo@venzap.com
                  </a>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </main>
  );
}

'use client';

import { motion } from 'framer-motion';
import { Check, Zap, TrendingUp, Users, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

export default function VendorSignup() {
  const steps = [
    { number: 1, title: 'Sign Up', description: 'Your email and basic info. 2 minutes.' },
    { number: 2, title: 'Add Products', description: 'Upload your catalog. 5 minutes.' },
    { number: 3, title: 'Go Live', description: 'Start selling on Telegram. 1 minute.' },
  ];

  const benefits = [
    {
      icon: Zap,
      title: 'Zero Commission',
      description: 'Keep 100% earnings during launch phase',
    },
    {
      icon: TrendingUp,
      title: 'Instant Payouts',
      description: 'Direct to your bank via Payaza DVA',
    },
    {
      icon: Users,
      title: 'Multi-Channel',
      description: 'Start on Telegram, expand to WhatsApp & more',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
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
        <div className="max-w-6xl mx-auto">
          {/* Header with Image */}
          <div className="grid md:grid-cols-2 gap-8 lg:gap-12 items-center mb-20">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center md:text-left"
            >
              <h1 className="text-5xl md:text-6xl font-bold mb-4 text-balance">
                <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">
                  Start Selling in 10 Minutes
                </span>
              </h1>
              <p className="text-xl text-foreground/70 max-w-2xl mb-8">
                No paperwork. No waiting. No commission. Just you, your products, and thousands of Nigerian customers.
              </p>
              <Link href="/vendor-signup#form">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="btn-primary inline-flex items-center gap-2 text-lg py-4 px-8"
                >
                  Get Started <ArrowRight className="w-5 h-5" />
                </motion.button>
              </Link>
            </motion.div>

            {/* Dashboard Image */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
              className="relative h-96 md:h-full min-h-96 hidden md:block"
            >
              <motion.div
                animate={{ y: [0, -20, 0] }}
                transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
                className="relative w-full h-full"
              >
                <Image
                  src="/vendor-dashboard-mockup.jpg"
                  alt="VENZAP Vendor Dashboard"
                  fill
                  className="object-contain drop-shadow-2xl rounded-xl"
                />
              </motion.div>
            </motion.div>
          </div>

          {/* Three Step Process */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid md:grid-cols-3 gap-8 mb-16"
          >
            {steps.map((step, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="text-center"
              >
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center mx-auto mb-4 text-white text-2xl font-bold">
                  {step.number}
                </div>
                <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                <p className="text-foreground/60">{step.description}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center mb-20"
          >
            <button className="px-8 py-4 bg-primary text-primary-foreground rounded-lg font-bold text-lg hover:bg-primary/90 transition-all shadow-lg shadow-primary/20">
              Start Your Store Now
            </button>
            <p className="text-foreground/60 text-sm mt-4">Takes less time than making coffee ☕</p>
          </motion.div>

          {/* Benefits Grid */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid md:grid-cols-3 gap-6 mb-16"
          >
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <motion.div
                  key={index}
                  variants={itemVariants}
                  className="p-6 rounded-xl border border-border bg-card/50 hover:border-primary/50 transition-all"
                >
                  <Icon className="w-8 h-8 text-primary mb-3" />
                  <h3 className="font-bold mb-2">{benefit.title}</h3>
                  <p className="text-foreground/60 text-sm">{benefit.description}</p>
                </motion.div>
              );
            })}
          </motion.div>

          {/* Payaza Section */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="bg-card border border-border rounded-xl p-8 mb-16"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-orange-500/20 flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">🏦</span>
              </div>
              <div>
                <h3 className="text-2xl font-bold mb-2">Powered by Payaza DVA</h3>
                <p className="text-foreground/60 mb-4">
                  Your earnings land directly in your bank account. No middleman. No delays. Payaza handles the heavy lifting with their innovative Dedicated Virtual Account (DVA) system.
                </p>
                <ul className="space-y-2 text-foreground/70">
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-500" />
                    Instant settlements to your bank
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-500" />
                    No transaction fees during launch
                  </li>
                  <li className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-500" />
                    Bank-grade security
                  </li>
                </ul>
              </div>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="bg-gradient-to-r from-orange-500/10 to-orange-600/10 border border-orange-500/20 rounded-xl p-8 text-center mb-16"
          >
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-3xl font-bold text-orange-500">5K+</div>
                <p className="text-foreground/60">Active Vendors</p>
              </div>
              <div>
                <div className="text-3xl font-bold text-orange-500">₦2B+</div>
                <p className="text-foreground/60">GMV Processed</p>
              </div>
              <div>
                <div className="text-3xl font-bold text-orange-500">0%</div>
                <p className="text-foreground/60">Commission</p>
              </div>
            </div>
          </motion.div>

          {/* FAQ */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="space-y-4"
          >
            <h2 className="text-3xl font-bold mb-8">Common Questions</h2>
            
            <details className="group border border-border rounded-lg p-4 cursor-pointer hover:border-primary/50 transition-all">
              <summary className="font-bold flex items-center justify-between">
                Do I need experience to sell?
                <span className="group-open:rotate-180 transition-transform">↓</span>
              </summary>
              <p className="text-foreground/60 mt-4">Not at all. We handle everything. You just add your products and chat with customers naturally.</p>
            </details>

            <details className="group border border-border rounded-lg p-4 cursor-pointer hover:border-primary/50 transition-all">
              <summary className="font-bold flex items-center justify-between">
                When will I get paid?
                <span className="group-open:rotate-180 transition-transform">↓</span>
              </summary>
              <p className="text-foreground/60 mt-4">Instantly! Your money goes straight to your bank via Payaza DVA the moment a customer pays.</p>
            </details>

            <details className="group border border-border rounded-lg p-4 cursor-pointer hover:border-primary/50 transition-all">
              <summary className="font-bold flex items-center justify-between">
                Can I sell from my phone?
                <span className="group-open:rotate-180 transition-transform">↓</span>
              </summary>
              <p className="text-foreground/60 mt-4">Yes! Set up your store on your phone in 10 minutes and manage everything from chat.</p>
            </details>
          </motion.div>

          {/* Final CTA */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center mt-16"
          >
            <button className="px-12 py-4 bg-primary text-primary-foreground rounded-lg font-bold text-lg hover:bg-primary/90 transition-all shadow-lg shadow-primary/20 mb-4">
              Create Your Store Now
            </button>
            <p className="text-foreground/60">
              Questions? <Link href="/schedule-demo" className="text-primary hover:underline">Schedule a demo</Link> with our team
            </p>
          </motion.div>
        </div>
      </div>
    </main>
  );
}

'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export function CustomerSection() {
  return (
    <section className="relative py-16 px-4 sm:px-6 lg:px-8">
      <div className="absolute inset-0 bg-gradient-to-r from-orange-500/10 via-transparent to-orange-600/10 pointer-events-none" />
      <div className="relative max-w-5xl mx-auto rounded-3xl border border-border glass p-8 md:p-10">
        <div className="grid md:grid-cols-2 gap-6 items-center">
          <div>
            <p className="text-orange-300 font-semibold">For Customers</p>
            <h3 className="mt-2 text-3xl md:text-4xl font-bold text-foreground text-balance">
              Order on Telegram in under 60 seconds
            </h3>
            <p className="mt-3 text-foreground/70 leading-relaxed">
              Skip app downloads. Chat with Venzap Bot, discover vendors, fund your wallet, and place your order directly in Telegram.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row md:flex-col gap-3 md:items-end">
            <Link href="https://t.me/VenZapBot" target="_blank" rel="noopener noreferrer">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.96 }}
                className="btn-primary w-full sm:w-auto"
              >
                Open Telegram Bot
              </motion.button>
            </Link>
            <p className="text-xs text-foreground/60 md:text-right">
              Bot link: t.me/VenZapBot
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

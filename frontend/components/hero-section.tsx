'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';

export function HeroSection() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: 'easeOut' },
    },
  };

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20 md:pt-0">
      {/* Animated background gradients */}
      <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 via-transparent to-transparent pointer-events-none" />
      <div className="absolute top-0 right-0 w-96 h-96 bg-primary/8 rounded-full blur-3xl animate-pulse-subtle" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-pulse-subtle" style={{ animationDelay: '1s' }} />

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full"
      >
        <div className="grid md:grid-cols-2 gap-8 lg:gap-16 items-center">
          {/* Left Content */}
          <motion.div variants={itemVariants} className="space-y-6">
            <motion.h1
              variants={itemVariants}
              className="text-5xl md:text-7xl font-bold leading-tight text-balance"
            >
              <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">
                Shop Anywhere
              </span>
              <br />
              <span className="text-foreground">You Chat</span>
            </motion.h1>

            <motion.p
              variants={itemVariants}
              className="text-lg md:text-xl text-foreground/70 leading-relaxed max-w-lg"
              >
              VENZAP is a chat-commerce demo for vendors and customers. Start in Telegram, keep the flow simple, and show how the platform works end to end.
            </motion.p>

            <motion.div
              variants={itemVariants}
              className="flex flex-col sm:flex-row gap-4 pt-6"
            >
              <Link href="/vendor/register">
                <motion.button
                  whileHover={{ scale: 1.08, boxShadow: '0 0 40px rgba(249, 115, 22, 0.4)' }}
                  whileTap={{ scale: 0.96 }}
                  className="btn-primary w-full sm:w-auto"
                >
                  Start Selling
                </motion.button>
              </Link>
              <Link href="/schedule-demo">
                <motion.button
                  whileHover={{ scale: 1.08 }}
                  whileTap={{ scale: 0.96 }}
                  className="btn-secondary w-full sm:w-auto"
                >
                  Schedule Demo
                </motion.button>
              </Link>
            </motion.div>

            {/* Social Proof */}
            <motion.div variants={itemVariants} className="pt-8 flex items-center gap-4">
              <div className="flex -space-x-3">
                {[1, 2, 3].map((i) => (
                  <motion.div
                    key={i}
                    whileHover={{ scale: 1.1 }}
                    className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 border-2 border-background flex items-center justify-center text-white font-bold text-sm"
                  >
                    {i}
                  </motion.div>
                ))}
              </div>
              <span className="text-foreground/70 text-sm">Built for a hackathon-friendly vendor demo</span>
            </motion.div>
          </motion.div>

          {/* Right - Chat Interface Image */}
          <motion.div
            variants={itemVariants}
            className="relative h-96 md:h-full min-h-96 flex items-center justify-center"
          >
            <motion.div
              animate={{ y: [0, -15, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
              className="relative w-full h-full"
            >
              <Image
                src="/chat-interface-mockup.jpg"
                alt="VENZAP Chat Commerce Interface"
                fill
                className="object-contain drop-shadow-2xl"
                priority
              />
            </motion.div>

            {/* Floating accent cards */}
            <motion.div
              animate={{ rotate: [0, 5, 0] }}
              transition={{ duration: 6, repeat: Infinity }}
              className="absolute top-10 right-0 glass rounded-2xl p-4 w-32 h-32 flex flex-col items-center justify-center gap-2 text-center"
            >
              <div className="text-2xl">💬</div>
              <p className="text-xs text-foreground/70">Chat to Buy</p>
            </motion.div>

            <motion.div
              animate={{ rotate: [0, -5, 0] }}
              transition={{ duration: 7, repeat: Infinity, delay: 0.5 }}
              className="absolute bottom-10 left-0 glass rounded-2xl p-4 w-32 h-32 flex flex-col items-center justify-center gap-2 text-center"
            >
              <div className="text-2xl">🏦</div>
              <p className="text-xs text-foreground/70">Instant Payout</p>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
}

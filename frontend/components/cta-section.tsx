'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import Link from 'next/link';

export function CTASection() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.3,
  });

  return (
    <section ref={ref} className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-r from-primary/15 via-transparent to-primary/10 pointer-events-none" />
      <div className="absolute top-0 right-0 w-96 h-96 bg-primary/8 rounded-full blur-3xl animate-pulse-subtle" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-pulse-subtle" style={{ animationDelay: '1s' }} />

      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 max-w-4xl mx-auto text-center"
      >
        <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight text-balance">
          Ready to Join the <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">Chat Commerce</span> Revolution?
        </h2>

        <p className="text-lg md:text-xl text-foreground/70 mb-10 max-w-2xl mx-auto leading-relaxed">
          Start selling today with VENZAP. No credit card required. No setup fees. Just pure commerce innovation.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-4">
          <Link href="/vendor-signup">
            <motion.button
              whileHover={{ scale: 1.08, boxShadow: '0 0 50px rgba(249, 115, 22, 0.5)' }}
              whileTap={{ scale: 0.96 }}
              className="btn-primary w-full sm:w-auto text-lg py-4 px-10 animate-glow"
            >
              Start Selling Now
            </motion.button>
          </Link>

          <Link href="/schedule-demo">
            <motion.button
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.96 }}
              className="btn-secondary w-full sm:w-auto text-lg py-4 px-10"
            >
              Schedule a Demo
            </motion.button>
          </Link>
        </div>

        {/* Social Proof */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-12 pt-8 border-t border-border"
        >
          <p className="text-foreground/50 text-sm mb-4">Trusted by leading merchants and entrepreneurs</p>
          <div className="flex flex-wrap items-center justify-center gap-6 md:gap-8">
            {['Payaza', 'Stripe', 'AWS', 'Vercel'].map((partner, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
                transition={{ delay: 0.4 + idx * 0.1 }}
                className="text-foreground/40 font-medium text-sm hover:text-foreground/60 transition-colors cursor-pointer"
              >
                {partner}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
}

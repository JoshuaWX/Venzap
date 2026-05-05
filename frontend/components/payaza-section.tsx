'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

export function PayazaIntegrationSection() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

  return (
    <section ref={ref} className="py-20 md:py-32 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          className="relative rounded-2xl overflow-hidden border border-border"
        >
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-transparent to-transparent pointer-events-none" />
          
          <div className="relative p-8 md:p-12 backdrop-blur-xl bg-gradient-to-br from-background/50 to-secondary/50">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              {/* Left: Text Content */}
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={inView ? { opacity: 1, x: 0 } : { opacity: 0, x: -30 }}
                transition={{ duration: 0.6 }}
              >
                <h2 className="text-4xl font-bold mb-4">
                  Powered by <span className="bg-gradient-to-r from-orange-400 to-orange-500 bg-clip-text text-transparent">Payaza</span>
                </h2>
                <p className="text-foreground/70 mb-6 leading-relaxed">
                  We&apos;ve partnered with Payaza, Africa&apos;s leading fintech platform, to bring you secure, instant payments. Your money arrives in your account immediately—no delays, no hassles.
                </p>
                
                <ul className="space-y-3 mb-8">
                  {[
                    'Instant settlement to your bank account',
                    'Support for all major Nigerian banks',
                    'Enterprise-grade security and encryption',
                    '24/7 customer support',
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-primary" />
                      <span className="text-foreground/80">{feature}</span>
                    </li>
                  ))}
                </ul>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-3 border border-primary text-primary rounded-lg font-medium hover:bg-primary/10 transition-all"
                >
                  Learn More About Payaza
                </motion.button>
              </motion.div>

              {/* Right: Visual */}
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={inView ? { opacity: 1, x: 0 } : { opacity: 0, x: 30 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="relative h-64 md:h-80 flex items-center justify-center"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-primary/5 rounded-xl blur-2xl" />
                <div className="relative z-10 text-center">
                  <div className="text-7xl font-bold bg-gradient-to-r from-orange-400 to-orange-500 bg-clip-text text-transparent mb-4">
                    ⚡
                  </div>
                  <p className="text-foreground/60 font-medium">Instant Payments</p>
                  <p className="text-2xl font-bold text-primary mt-2">100% Secure</p>
                </div>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

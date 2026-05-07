'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { useEffect, useState } from 'react';

export function StatsSection() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.3,
  });

  const stats = [
    { value: 'Live', label: 'Demo-ready flows', delay: 0 },
    { value: 'Async', label: 'Order processing', delay: 0.2 },
    { value: 'Payaza', label: 'Wallet funding', delay: 0.4 },
    { value: 'Secure', label: 'Cookie auth + guards', delay: 0.6 },
  ];

  return (
    <section ref={ref} className="py-16 md:py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-secondary/20 to-transparent border-t border-b border-border">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : { opacity: 0 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-8"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30, scale: 0.8 }}
              animate={inView ? { opacity: 1, y: 0, scale: 1 } : { opacity: 0, y: 30, scale: 0.8 }}
              transition={{ delay: stat.delay, duration: 0.6, ease: 'easeOut' }}
              className="text-center p-4 rounded-lg glass-hover"
            >
              <motion.div
                initial={{ opacity: 0 }}
                animate={inView ? { opacity: 1 } : { opacity: 0 }}
                transition={{ delay: stat.delay + 0.3, duration: 0.8 }}
              >
                <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent mb-2">
                  {stat.value}
                </div>
              </motion.div>
              <p className="text-foreground/70 font-medium text-sm md:text-base">{stat.label}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

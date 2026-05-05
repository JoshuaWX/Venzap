'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { ArrowRight } from 'lucide-react';

export function HowItWorksSection() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

  const steps = [
    {
      number: '01',
      title: 'Create Your Store',
      description: 'Sign up and set up your store in minutes. No coding required.',
    },
    {
      number: '02',
      title: 'Add Your Products',
      description: 'Upload your inventory with beautiful photos and descriptions.',
    },
    {
      number: '03',
      title: 'Share Your Link',
      description: 'Get a unique store link and share it on WhatsApp, Telegram, or social media.',
    },
    {
      number: '04',
      title: 'Start Selling',
      description: 'Customers browse, chat, and buy. You get paid instantly.',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.15 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 },
    },
  };

  return (
    <section ref={ref} id="how-it-works" className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-orange-500/5 via-transparent to-transparent pointer-events-none" />
      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-balance">How VENZAP <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">Works</span></h2>
          <p className="text-lg text-foreground/70 max-w-2xl mx-auto">
            Start selling in just 4 steps. No delays. No complicated processes.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
          className="grid md:grid-cols-4 gap-4 md:gap-2 relative"
        >
          {/* Connection line */}
          <div className="hidden md:block absolute top-1/4 left-0 right-0 h-1 bg-gradient-to-r from-orange-500/20 via-orange-500/50 to-orange-500/20" style={{ transform: 'translateY(-8px)' }} />

          {steps.map((step, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="relative"
            >
              <motion.div
                whileHover={{ scale: 1.05, y: -8 }}
                className="p-6 rounded-2xl glass-hover border border-border/50 hover:border-primary/40 text-center group relative z-10"
              >
                <motion.div
                  whileHover={{ scale: 1.2, rotate: 360 }}
                  transition={{ duration: 0.6 }}
                  className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center text-2xl font-bold text-white mx-auto mb-4"
                >
                  {step.number}
                </motion.div>
                <h3 className="text-lg font-bold mb-2 text-foreground">{step.title}</h3>
                <p className="text-foreground/70 text-sm leading-relaxed">{step.description}</p>
                
                {index < steps.length - 1 && (
                  <ArrowRight className="w-5 h-5 text-primary mx-auto mt-4 md:hidden" />
                )}
              </motion.div>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
          transition={{ delay: 0.6 }}
          className="text-center mt-16"
        >
          <p className="text-foreground/70 mb-6">Ready to start? It takes just 10 minutes.</p>
          <a href="/vendor-signup">
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: '0 0 40px rgba(249, 115, 22, 0.5)' }}
              whileTap={{ scale: 0.96 }}
              className="btn-primary"
            >
              Get Started Now
            </motion.button>
          </a>
        </motion.div>
      </div>
    </section>
  );
}

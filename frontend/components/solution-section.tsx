'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { CheckCircle2 } from 'lucide-react';
import Image from 'next/image';

export function SolutionSection() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

  const solutions = [
    {
      title: 'Zero Commission + Direct Bank Transfer',
      description: 'Keep 100% of your earnings. Payaza DVA sends money straight to your bank account instantly.',
      icon: '🏦',
      features: ['100% commission-free', 'Instant payouts', 'Direct bank transfer'],
    },
    {
      title: 'Chat-Native Selling',
      description: 'Customers shop naturally. No app downloads, no learning curve. Just conversation.',
      icon: '💬',
      features: ['Shop in Telegram/WhatsApp', 'Natural language AI', 'One-click checkout'],
    },
    {
      title: '10-Minute Onboarding',
      description: 'Sign up, add products, start selling. Really that simple.',
      icon: '⚡',
      features: ['No paperwork', 'Instant approval', 'Unified dashboard'],
    },
    {
      title: 'Accessible to All',
      description: 'Whether you&apos;re offline or online, formal or informal. VENZAP is for every seller.',
      icon: '🌍',
      features: ['No eligibility barriers', 'Inclusive by design', 'Nigerian-first approach'],
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
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 },
    },
  };

  return (
    <section ref={ref} id="solution" className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 bg-gradient-to-l from-orange-500/5 to-transparent pointer-events-none" />
      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-balance">
            The VENZAP <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">Solution</span>
          </h2>
          <p className="text-lg text-foreground/70 max-w-2xl mx-auto">
            Everything your business needs to thrive in the age of chat commerce.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
          className="grid md:grid-cols-2 gap-6 mb-16"
        >
          {solutions.map((solution, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ scale: 1.03, y: -5 }}
              className="p-8 rounded-2xl glass-hover border border-border/50 hover:border-primary/40 group"
            >
              <motion.div
                whileHover={{ scale: 1.1 }}
                className="text-5xl mb-4 inline-block"
              >
                {solution.icon}
              </motion.div>
              <h3 className="text-2xl font-bold mb-2 text-foreground">{solution.title}</h3>
              <p className="text-foreground/70 mb-6 leading-relaxed">{solution.description}</p>
              
              <ul className="space-y-3">
                {solution.features.map((feature, idx) => (
                  <li key={idx} className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                    <span className="text-foreground/80 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </motion.div>

        {/* Commission Comparison Image */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={inView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="relative rounded-2xl overflow-hidden border border-primary/30 glass p-1"
        >
          <div className="relative w-full h-96 rounded-xl overflow-hidden">
            <Image
              src="/commission-comparison.jpg"
              alt="Commission Comparison - VENZAP vs Others"
              fill
              className="object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
          </div>
        </motion.div>
      </div>
    </section>
  );
}

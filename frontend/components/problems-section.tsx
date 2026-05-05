'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

export function ProblemsSection() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

  const problems = [
    {
      title: 'Platform Fees Are Killing Margins',
      description: 'Marketplaces charge 20-30% commission. Vendors barely break even.',
      gradient: 'from-red-500/20 to-red-600/20',
      borderColor: 'border-red-500/30',
    },
    {
      title: 'Complex Vendor Onboarding',
      description: 'Traditional e-commerce takes days of paperwork. Small vendors give up.',
      gradient: 'from-orange-500/20 to-orange-600/20',
      borderColor: 'border-orange-500/30',
    },
    {
      title: 'Millions of Sellers Are Excluded',
      description: 'Offline vendors, informal traders, and small businesses can&apos;t access digital tools.',
      gradient: 'from-yellow-500/20 to-yellow-600/20',
      borderColor: 'border-yellow-500/30',
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
    hidden: { opacity: 0, x: -30 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.6 },
    },
  };

  return (
    <section ref={ref} className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 bg-secondary/20">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : { opacity: 0 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">The Old Way Was Broken</h2>
          <p className="text-lg text-foreground/60 max-w-2xl mx-auto">
            E-commerce hasn't evolved. Let's fix that together.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
          className="space-y-4"
        >
          {problems.map((problem, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className={`p-6 md:p-8 rounded-xl border ${problem.borderColor} bg-gradient-to-r ${problem.gradient} backdrop-blur-sm hover:border-primary/50 transition-all`}
            >
              <h3 className="text-xl md:text-2xl font-bold mb-2">{problem.title}</h3>
              <p className="text-foreground/70">{problem.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

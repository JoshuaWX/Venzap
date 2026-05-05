'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Zap, TrendingUp, Lock, Users } from 'lucide-react';

export function FeaturesSection() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

  const features = [
    {
      icon: Zap,
      title: 'Multi-Channel',
      description: 'Start on Telegram, WhatsApp, Discord, Slack. One vendor dashboard, every platform.',
      color: 'from-blue-400 to-blue-600',
    },
    {
      icon: Users,
      title: 'Zero Commission',
      description: 'Keep 100% during launch phase. Direct payments via Payaza DVA to your bank account.',
      color: 'from-green-400 to-green-600',
    },
    {
      icon: Lock,
      title: '10-Min Setup',
      description: 'From signup to live selling in 10 minutes. No paperwork, no delays.',
      color: 'from-orange-400 to-orange-600',
    },
    {
      icon: TrendingUp,
      title: 'Pidgin-Fluent AI',
      description: 'Our AI understands Nigerian Pidgin naturally. "Abeg, wetin be your price?" works perfectly.',
      color: 'from-purple-400 to-purple-600',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
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
    <section ref={ref} id="features" className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 bg-gradient-to-r from-orange-500/5 to-transparent pointer-events-none" />
      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-balance">
            Why Choose <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">VENZAP</span>
          </h2>
          <p className="text-lg text-foreground/70 max-w-2xl mx-auto">
            Everything you need to sell, scale, and succeed in the chat-commerce revolution.
          </p>
        </motion.div>

        <motion.div
          ref={ref}
          variants={containerVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
          className="grid md:grid-cols-2 gap-6"
        >
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                variants={itemVariants}
                whileHover={{ scale: 1.03, y: -5 }}
                className="group p-8 rounded-2xl glass-hover border border-border/50 hover:border-primary/40"
              >
                <motion.div
                  whileHover={{ scale: 1.15, rotate: 5 }}
                  className={`w-14 h-14 rounded-lg bg-gradient-to-br ${feature.color} p-3 mb-4 transition-transform flex items-center justify-center`}
                >
                  <Icon className="w-7 h-7 text-white" />
                </motion.div>
                <h3 className="text-xl font-bold mb-2 text-foreground">{feature.title}</h3>
                <p className="text-foreground/70 leading-relaxed">{feature.description}</p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}

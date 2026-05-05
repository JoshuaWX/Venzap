'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { Check } from 'lucide-react';

export function PricingSection() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

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

  const plans = [
    {
      name: 'Starter',
      price: 'Free',
      period: 'Forever free',
      description: 'Perfect for testing the waters',
      features: [
        '1 store',
        'Up to 100 products',
        'Basic analytics',
        'Email support',
        'Standard commission',
      ],
      cta: 'Get Started',
      highlighted: false,
    },
    {
      name: 'Professional',
      price: '₦4,999',
      period: '/month',
      description: 'For growing merchants',
      features: [
        'Up to 3 stores',
        'Unlimited products',
        'Advanced analytics',
        'Priority support',
        'Reduced commission',
        'Custom branding',
        'API access',
      ],
      cta: 'Start Free Trial',
      highlighted: true,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: 'For large teams',
      description: 'Tailored for your needs',
      features: [
        'Unlimited stores',
        'Unlimited products',
        'White-label solution',
        '24/7 dedicated support',
        'Custom integration',
        'Advanced security',
        'SLA guarantee',
      ],
      cta: 'Contact Sales',
      highlighted: false,
    },
  ];

  return (
    <section ref={ref} id="pricing" className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-orange-500/5 to-transparent pointer-events-none" />
      <div className="max-w-6xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-balance">
            Simple, <span className="bg-gradient-to-r from-orange-400 via-orange-500 to-orange-600 bg-clip-text text-transparent">Transparent</span> Pricing
          </h2>
          <p className="text-lg text-foreground/70 max-w-2xl mx-auto">
            No hidden fees. Scale as you grow. Plus 1.5% transaction fee on all sales.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
          className="grid md:grid-cols-3 gap-6"
        >
          {plans.map((plan, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ scale: 1.02, y: -8 }}
              className={`p-8 rounded-2xl relative group transition-all duration-300 ${
                plan.highlighted
                  ? 'glass border border-primary/50 ring-2 ring-primary/30 md:scale-105'
                  : 'glass-hover border border-border/50 hover:border-primary/40'
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 px-4 py-1 bg-primary text-primary-foreground text-sm font-bold rounded-full">
                  Most Popular
                </div>
              )}

              <h3 className="text-2xl font-bold mb-2 text-foreground">{plan.name}</h3>
              <div className="mb-2">
                <span className="text-4xl font-bold text-primary">{plan.price}</span>
                <span className="text-foreground/70 text-sm ml-2">{plan.period}</span>
              </div>
              <p className="text-foreground/70 mb-6 text-sm">{plan.description}</p>

              {/* Features */}
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-primary flex-shrink-0" />
                    <span className="text-foreground/80 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`w-full py-3 px-6 rounded-lg font-bold transition-all duration-200 ${
                  plan.highlighted
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20'
                    : 'border border-primary text-primary hover:bg-primary/10'
                }`}
              >
                {plan.cta}
              </motion.button>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

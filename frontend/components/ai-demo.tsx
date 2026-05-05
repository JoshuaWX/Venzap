'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { MessageCircle, Send } from 'lucide-react';

export function AIDemo() {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.2,
  });

  const chatMessages = [
    { type: 'user', text: 'Hi! What do you have in stock?' },
    { type: 'ai', text: 'Welcome! 👋 We have amazing products in stock. What are you looking for?' },
    { type: 'user', text: 'Show me summer dresses' },
    { type: 'ai', text: 'Perfect! I found 15 summer dresses. Here are the top picks... 🌞' },
    { type: 'user', text: 'How much is the blue one?' },
    { type: 'ai', text: 'The blue sundress is ₦12,500. Ready to checkout? 🛒' },
  ];

  return (
    <section ref={ref} className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 bg-secondary/20">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : { opacity: 0 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">Experience AI-Powered Shopping</h2>
          <p className="text-lg text-foreground/60">
            See how our intelligent chat assistant transforms shopping into a conversation.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          className="rounded-2xl border border-border bg-gradient-to-b from-background to-secondary/30 p-6 md:p-8 backdrop-blur-xl max-w-2xl mx-auto"
        >
          {/* Chat Header */}
          <div className="flex items-center gap-3 pb-4 border-b border-border mb-6">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-bold text-sm">VENZAP Shop Assistant</p>
              <p className="text-xs text-foreground/50">Always online</p>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
            {chatMessages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
                transition={{ delay: index * 0.1 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-primary text-primary-foreground rounded-br-none'
                      : 'bg-card text-foreground rounded-bl-none border border-border'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Input Area */}
          <div className="flex items-center gap-3 pt-4 border-t border-border">
            <input
              type="text"
              placeholder="Type your message..."
              className="flex-1 bg-input border border-border rounded-lg px-4 py-2 text-sm text-foreground placeholder:text-foreground/40 outline-none focus:border-primary transition-colors"
            />
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <Send className="w-4 h-4" />
            </motion.button>
          </div>
        </motion.div>

        {/* Benefits Below Chat */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ delay: 0.4 }}
          className="grid md:grid-cols-3 gap-6 mt-12"
        >
          {[
            { icon: '💬', title: 'Natural Conversation', desc: 'Shop like you&apos;re talking to a friend' },
            { icon: '⚡', title: 'Instant Answers', desc: 'Get recommendations in seconds' },
            { icon: '✓', title: 'One-Click Checkout', desc: 'Buy without leaving chat' },
          ].map((benefit, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0 }}
              animate={inView ? { opacity: 1 } : { opacity: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              className="text-center p-4"
            >
              <div className="text-3xl mb-2">{benefit.icon}</div>
              <h3 className="font-bold mb-1">{benefit.title}</h3>
              <p className="text-sm text-foreground/60">{benefit.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

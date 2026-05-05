'use client';

import { motion } from 'framer-motion';

export function VenzapLogo() {
  return (
    <motion.div 
      className="flex items-center gap-2"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center">
        <span className="text-white font-bold text-sm">V</span>
      </div>
      <span className="text-xl font-bold bg-gradient-to-r from-orange-400 to-orange-500 bg-clip-text text-transparent">
        VENZAP
      </span>
    </motion.div>
  );
}

import { Navbar } from '@/components/navbar';
import { CustomCursor } from '@/components/custom-cursor';
import { HeroSection } from '@/components/hero-section';
import { StatsSection } from '@/components/stats-section';
import { FeaturesSection } from '@/components/features-section';
import { ProblemsSection } from '@/components/problems-section';
import { SolutionSection } from '@/components/solution-section';
import { HowItWorksSection } from '@/components/how-it-works-section';
import { PayazaIntegrationSection } from '@/components/payaza-section';
import { AIDemo } from '@/components/ai-demo';
import { TestimonialsSection } from '@/components/testimonials-section';
import { PricingSection } from '@/components/pricing-section';
import { CTASection } from '@/components/cta-section';
import { Footer } from '@/components/footer';
import { CustomerSection } from '@/components/customer-section';

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <CustomCursor />
      <Navbar />
      <HeroSection />
      <CustomerSection />
      <StatsSection />
      <FeaturesSection />
      <ProblemsSection />
      <SolutionSection />
      <HowItWorksSection />
      <PayazaIntegrationSection />
      <AIDemo />
      <TestimonialsSection />
      <PricingSection />
      <CTASection />
      <Footer />
    </main>
  );
}

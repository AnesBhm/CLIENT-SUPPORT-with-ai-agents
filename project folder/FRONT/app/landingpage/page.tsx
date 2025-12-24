import Navbar from "../components/Navbar";
import HeroSection from "../components/HeroSection";
import ContactSection from "../components/ContactSection";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col bg-white">
      <Navbar />
      <HeroSection />
      

      <ContactSection />
    </main>
  );
}
import Navbar2 from "../components/Navbar2";
import ContactSection from "../components/ContactSection";
import Dashboard from "../components/Dashboard";

export default function DashboardPage() {
  return (
    <main className="min-h-screen flex flex-col bg-white">
      {/* Ta Navbar existante */}
      <Navbar2 />
      
      {/* Le composant Dashboard (Shell) qui contient la Sidebar et gère l'affichage des autres composants */}
      <Dashboard />

      {/* Ta section contact existante */}
      <ContactSection />
    </main>
  );
}
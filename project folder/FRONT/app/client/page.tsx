import Navbar2 from "../components/Navbar2";
import ContactSection from "../components/ContactSection";
import ClientDashboard from "../components/ClientDashboard";

export default function Home() {
  return (
    <main className="bg-[#141516] min-h-screen">
      <Navbar2 />
      
        <ClientDashboard />
      {/* Tu pourras ajouter d'autres sections ici plus tard (A Sketch, Vision, etc.) */}
      
      <ContactSection />
    </main>
  );
}


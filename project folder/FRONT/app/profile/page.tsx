import Navbar2 from "../components/Navbar2";
import ContactSection from "../components/ContactSection";
import Profile from "../components/Profile";
export default function Home() {
  return (
    <main className="min-h-screen flex flex-col bg-white">
      <Navbar2 />
      
        <Profile />
      <ContactSection />
    </main>
  );    
}
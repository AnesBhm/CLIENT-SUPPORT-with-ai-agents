import Navbar from "../components/Navbar";
import ContactSection from "../components/ContactSection";
import Login from "../components/Login";

export default function Home() {
  return (
    <div className=" min-h-screen">
      <Navbar />
      <Login />
      <ContactSection />
    </div>
  );
}
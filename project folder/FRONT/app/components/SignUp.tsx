'use client'; // Only needed for App Router

import Navbar from './Navbar';
import ContactSection from './ContactSection';
import Image from 'next/image'
import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { authService } from '../lib/services/auth';


export default function SignUpPage() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    ageConfirm: false,
    termsAccept: false,
    newsletter: false
  });

  const [errors, setErrors] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    ageConfirm: '',
    termsAccept: '',
    newsletter: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    const fieldName = name as keyof typeof errors;

    setFormData(prev => ({
      ...prev,
      [fieldName]: type === 'checkbox' ? checked : value
    }));

    // Clear error when user starts typing
    if (errors[fieldName]) {
      setErrors(prev => ({ ...prev, [fieldName]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {
      fullName: '',
      email: '',
      password: '',
      confirmPassword: '',
      ageConfirm: '',
      termsAccept: '',
      newsletter: ''
    };

    let isValid = true;

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
      isValid = false;
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
      isValid = false;
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
      isValid = false;
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
      isValid = false;
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
      isValid = false;
    }

    if (!formData.ageConfirm) {
      newErrors.ageConfirm = 'You must be at least 18 years old';
      isValid = false;
    }

    if (!formData.termsAccept) {
      newErrors.termsAccept = 'You must accept the terms and conditions';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async () => {
    if (validateForm()) {
      setLoading(true);
      try {
        await authService.signup({
          email: formData.email,
          password: formData.password,
          full_name: formData.fullName
        });

        alert('Account created successfully! Please log in.');
        router.push('/login');

        // Reset form
        setFormData({
          fullName: '',
          email: '',
          password: '',
          confirmPassword: '',
          ageConfirm: false,
          termsAccept: false,
          newsletter: false
        });
      } catch (error: any) {
        alert(error.message || "Registration failed");
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen mt-10 bg-white relative overflow-hidden flex flex-col ">


      {/* Decorative circles - Right */}
      <Navbar />
      {/* =========================================
                1. PATTERNS DÉCORATIFS (Thème DOXA)
            ========================================== */}

      <div className="hidden lg:block absolute top-0 left-0 h-full w-32 xl:w-64 z-0">
        <div className="relative h-full w-full">
          <Image
            src="/pattern.svg"
            alt="Design Pattern Left"
            fill
            className="object-cover object-left"
            priority
          />
        </div>
      </div>

      <div className="hidden lg:block absolute top-0 right-0 h-full w-32 xl:w-64 z-0 rotate-180">
        <div className="relative h-full w-full">
          <Image
            src="/pattern.svg"
            alt="Design Pattern Right"
            fill
            className="object-cover object-left"
            priority
          />
        </div>
      </div>


      <main className="bg-white flex-1 max-w-2xl mx-auto px-4 py-8 md:py-12 mt-15 relative z-10 w-full">
        <div className="bg-gray-200 rounded-3xl p-8 md:p-12 shadow-lg">
          <h1 className="text-2xl md:text-3xl font-bold text-center mb-8 md:mb-10 text-[rgb(53,68,81)]">Sign up now!</h1>

          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 ">
                Full name
              </label>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                placeholder="Enter your name"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-[#354451]"
              />
              {errors.fullName && <p className="text-red-600 text-xs mt-1">{errors.fullName}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mail
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Type your mail"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-[#354451]"
              />
              {errors.email && <p className="text-red-600 text-xs mt-1">{errors.email}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Type your password"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-[#354451]"
              />
              <p className="text-xs text-gray-500 mt-1">Must be 8 characters at least,one CAPS,one number</p>
              {errors.password && <p className="text-red-600 text-xs mt-1">{errors.password}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 ">
                Confirm password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm your password"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-[#354451]"
              />
              {errors.confirmPassword && <p className="text-red-600 text-xs mt-1">{errors.confirmPassword}</p>}
            </div>

            <div>
              <label className="flex items-start cursor-pointer">
                <input
                  type="checkbox"
                  name="ageConfirm"
                  checked={formData.ageConfirm}
                  onChange={handleChange}
                  className="mt-1 mr-2 cursor-pointer"
                />
                <span className="text-sm text-gray-700">
                  I am at least <span className="font-semibold">18 years old</span>
                </span>
              </label>
              {errors.ageConfirm && <p className="text-red-600 text-xs mt-1">{errors.ageConfirm}</p>}
            </div>

            <div>
              <label className="flex items-start cursor-pointer">
                <input
                  type="checkbox"
                  name="termsAccept"
                  checked={formData.termsAccept}
                  onChange={handleChange}
                  className="mt-1 mr-2 cursor-pointer"
                />
                <span className="text-sm text-gray-700">
                  By creating an account means you agree to the{' '}
                  <button className="text-blue-600 underline hover:text-blue-800">Terms and Conditions</button>
                  {', and our '}
                  <button className="text-blue-600 underline hover:text-blue-800">Privacy Policy</button>
                </span>
              </label>
              {errors.termsAccept && <p className="text-red-600 text-xs mt-1">{errors.termsAccept}</p>}
            </div>

            <div>
              <label className="flex items-start cursor-pointer">
                <input
                  type="checkbox"
                  name="newsletter"
                  checked={formData.newsletter}
                  onChange={handleChange}
                  className="mt-1 mr-2 cursor-pointer"
                />
                <span className="text-sm text-gray-700">
                  Do you want to receive news and updates via e-mail
                </span>
              </label>
            </div>

            <Link href={'login'}>
              <div className="text-center pt-2">
                <button className="text-sm text-blue-600 hover:underline">
                  Already have an account?
                </button>
              </div>
            </Link>

            <div className="flex items-center justify-center">
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="w-full bg-[#FCEE21] text-black font-semibold py-3 rounded-full hover:bg-yellow-400 transition-colors shadow-md disabled:opacity-50"
              >
                {loading ? "Creating Account..." : "Submit"}
              </button>
            </div>

          </div>
        </div>
      </main>

      {/* Footer */}
      <ContactSection />
    </div>
  );
}
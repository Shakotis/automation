import { Fira_Code as FontMono, Inter as FontSans, Roboto } from "next/font/google";

export const fontSans = FontSans({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const fontMono = FontMono({
  subsets: ["latin"],
  variable: "--font-mono",
});

// Roboto font for Google Sign-In button (Google Branding Guidelines compliance)
export const fontRoboto = Roboto({
  weight: ["400", "500", "700"],
  subsets: ["latin"],
  variable: "--font-roboto",
  display: "swap",
});

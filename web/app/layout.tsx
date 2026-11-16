import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "HyperGen — Agent Reliability Lab",
  description: "Test AI agents before they touch real systems. Reproducible synthetic scenarios, action traces and independent state verification.",
  openGraph: { title: "HyperGen — Agent Reliability Lab", description: "Test AI agents before they touch real systems.", type: "website", images: ["/og.svg"] },
  robots: { index: true, follow: true },
};
export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
  return <html lang="en"><body>{children}</body></html>;
}

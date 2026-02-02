import type { Metadata } from 'next';
import ThemeRegistry from '@/components/ThemeRegistry';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'PyLogic Admin',
  description: 'PyLogic Administration Panel',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>
        <ThemeRegistry>{children}</ThemeRegistry>
      </body>
    </html>
  );
}

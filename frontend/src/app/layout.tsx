import type { Metadata } from 'next';
import ThemeRegistry from '@/components/ThemeRegistry';
import { AuthProvider } from '@/contexts/AuthContext';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'PyLogic - Demonstrador de Equivalencias',
  description: 'Demonstrador interativo de equivalencias logicas com redes neurais',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>
        <ThemeRegistry>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeRegistry>
      </body>
    </html>
  );
}

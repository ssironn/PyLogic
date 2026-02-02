'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  useTheme,
  useMediaQuery,
  CircularProgress,
} from '@mui/material';
import { Menu as MenuIcon } from '@mui/icons-material';
import Sidebar, { DRAWER_WIDTH } from './Sidebar';
import { useAuth } from '@/contexts/AuthContext';

interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
}

export default function DashboardLayout({ children, title }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleSidebarClose = () => {
    setSidebarOpen(false);
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', overflow: 'hidden' }}>
      <Sidebar open={sidebarOpen} onClose={handleSidebarClose} />

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
          width: '100%',
        }}
      >
        {/* App Bar for mobile */}
        {isMobile && (
          <AppBar
            position="sticky"
            sx={{
              bgcolor: 'background.paper',
              color: 'text.primary',
              boxShadow: 1,
            }}
          >
            <Toolbar>
              <IconButton
                edge="start"
                color="inherit"
                onClick={handleSidebarToggle}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                {title || 'PyLogic'}
              </Typography>
            </Toolbar>
          </AppBar>
        )}

        {/* Page Content */}
        <Box
          sx={{
            flex: 1,
            p: 3,
            bgcolor: 'background.default',
            overflow: 'auto',
            minWidth: 0,
          }}
        >
          {!isMobile && title && (
            <Typography
              variant="h4"
              component="h1"
              sx={{ mb: 3, fontWeight: 600 }}
            >
              {title}
            </Typography>
          )}
          {children}
        </Box>
      </Box>
    </Box>
  );
}

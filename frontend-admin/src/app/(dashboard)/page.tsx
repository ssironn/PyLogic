'use client';

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material';
import {
  Groups as GroupsIcon,
  People as PeopleIcon,
  Folder as FolderIcon,
} from '@mui/icons-material';
import AdminLayout from '@/components/AdminLayout';
import { classGroupsApi, studentsApi, contentNodesApi } from '@/services/adminApi';

interface DashboardStats {
  classGroups: number;
  students: number;
  contentNodes: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [classGroupsRes, studentsRes, contentNodesRes] = await Promise.all([
          classGroupsApi.list(),
          studentsApi.list(),
          contentNodesApi.list(),
        ]);

        setStats({
          classGroups: classGroupsRes.data?.length || 0,
          students: studentsRes.data?.length || 0,
          contentNodes: contentNodesRes.data?.length || 0,
        });
      } catch (error) {
        console.error('Error loading stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, []);

  const statCards = [
    {
      title: 'Turmas',
      value: stats?.classGroups || 0,
      icon: <GroupsIcon sx={{ fontSize: 40 }} />,
      color: '#6366f1',
    },
    {
      title: 'Alunos',
      value: stats?.students || 0,
      icon: <PeopleIcon sx={{ fontSize: 40 }} />,
      color: '#22c55e',
    },
    {
      title: 'Conteudos',
      value: stats?.contentNodes || 0,
      icon: <FolderIcon sx={{ fontSize: 40 }} />,
      color: '#f59e0b',
    },
  ];

  return (
    <AdminLayout>
      <Box>
        <Typography variant="h4" sx={{ mb: 4 }}>
          Dashboard
        </Typography>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {statCards.map((card) => (
              <Grid item xs={12} sm={6} md={4} key={card.title}>
                <Card>
                  <CardContent>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <Box>
                        <Typography color="text.secondary" gutterBottom>
                          {card.title}
                        </Typography>
                        <Typography variant="h3" component="div">
                          {card.value}
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          p: 2,
                          borderRadius: 2,
                          bgcolor: `${card.color}20`,
                          color: card.color,
                        }}
                      >
                        {card.icon}
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </AdminLayout>
  );
}

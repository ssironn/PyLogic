'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { School as SchoolIcon } from '@mui/icons-material';
import { DashboardLayout } from '@/components/layout';
import coursesService, { Enrollment } from '@/services/courses';

export default function CoursesPage() {
  const router = useRouter();
  const [courses, setCourses] = useState<Enrollment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCourses();
  }, []);

  const handleCourseClick = (classGroupId: string) => {
    router.push(`/courses/${classGroupId}`);
  };

  const loadCourses = async () => {
    try {
      setIsLoading(true);
      const response = await coursesService.list();

      if (response.status === 'success' && response.data) {
        setCourses(response.data);
      } else {
        setError(response.message || 'Erro ao carregar cursos');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao conectar com o servidor');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  return (
    <DashboardLayout title="Disciplinas">
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        ) : courses.length === 0 ? (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <SchoolIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                Voce ainda nao esta matriculado em nenhum curso
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Entre em contato com o administrador para ser adicionado a uma turma
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={3}>
            {courses.map((enrollment) => (
              <Grid item xs={12} md={6} lg={4} key={enrollment.id}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4,
                    },
                  }}
                >
                  <CardActionArea
                    onClick={() => handleCourseClick(enrollment.class_group.id)}
                    sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
                  >
                    <Box
                      sx={{
                        p: 2,
                        background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
                        color: 'white',
                        width: '100%',
                      }}
                    >
                      <SchoolIcon sx={{ fontSize: 40, mb: 1 }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {enrollment.class_group.name}
                      </Typography>
                    </Box>
                    <CardContent sx={{ flex: 1, width: '100%' }}>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 2, minHeight: 40 }}
                      >
                        {enrollment.class_group.description || 'Sem descricao'}
                      </Typography>
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <Typography variant="caption" color="text.secondary">
                          Matriculado em {formatDate(enrollment.enrollment_date)}
                        </Typography>
                        <Chip
                          label={enrollment.status}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      </Box>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </DashboardLayout>
  );
}

'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Card,
  CardActionArea,
  CardContent,
  Grid,
  Breadcrumbs,
  Link,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  YouTube as YouTubeIcon,
  ArrowBack as ArrowBackIcon,
  PlayCircle as PlayIcon,
  Description as DocIcon,
} from '@mui/icons-material';
import { DashboardLayout } from '@/components/layout';
import contentService, { ContentNode } from '@/services/content';
import coursesService from '@/services/courses';

export default function CourseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const classGroupId = params.classGroupId as string;

  const [contents, setContents] = useState<ContentNode[]>([]);
  const [courseName, setCourseName] = useState<string>('');
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<Array<{ id: string | null; title: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCourseName();
  }, [classGroupId]);

  useEffect(() => {
    loadContents();
  }, [classGroupId, currentFolderId]);

  const loadCourseName = async () => {
    try {
      const response = await coursesService.list();
      if (response.status === 'success' && response.data) {
        const course = response.data.find((e) => e.class_group.id === classGroupId);
        if (course) {
          setCourseName(course.class_group.name);
          setBreadcrumbs([{ id: null, title: course.class_group.name }]);
        }
      }
    } catch (err) {
      console.error('Error loading course name:', err);
    }
  };

  const loadContents = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await contentService.listContents(classGroupId, currentFolderId || undefined);

      if (response.status === 'success' && response.data) {
        setContents(response.data);
      } else {
        setError(response.message || 'Erro ao carregar conteudos');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao conectar com o servidor');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFolderClick = (folder: ContentNode) => {
    setCurrentFolderId(folder.id);
    setBreadcrumbs([...breadcrumbs, { id: folder.id, title: folder.title }]);
  };

  const handleBreadcrumbClick = (index: number) => {
    const item = breadcrumbs[index];
    setCurrentFolderId(item.id);
    setBreadcrumbs(breadcrumbs.slice(0, index + 1));
  };

  const handleContentClick = (content: ContentNode) => {
    if (content.type === 'pasta') {
      handleFolderClick(content);
    } else {
      router.push(`/courses/${classGroupId}/content/${content.id}`);
    }
  };

  const getContentIcon = (content: ContentNode) => {
    switch (content.type) {
      case 'pasta':
        return <FolderIcon sx={{ fontSize: 48, color: content.color || '#6366f1' }} />;
      case 'youtube':
        return <YouTubeIcon sx={{ fontSize: 48, color: '#ff0000' }} />;
      case 'arquivo':
        if (content.mime_type?.includes('pdf')) {
          return <DocIcon sx={{ fontSize: 48, color: '#ea4335' }} />;
        }
        return <FileIcon sx={{ fontSize: 48, color: '#4285f4' }} />;
      default:
        return <FileIcon sx={{ fontSize: 48 }} />;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(1)} MB`;
  };

  return (
    <DashboardLayout title={courseName || 'Carregando...'}>
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        {/* Back button and Breadcrumbs */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <IconButton onClick={() => router.push('/courses')} size="small">
            <ArrowBackIcon />
          </IconButton>
          <Breadcrumbs>
            {breadcrumbs.map((item, index) => (
              <Link
                key={item.id || 'root'}
                component="button"
                variant="body2"
                onClick={() => handleBreadcrumbClick(index)}
                sx={{
                  cursor: 'pointer',
                  color: index === breadcrumbs.length - 1 ? 'text.primary' : 'text.secondary',
                  textDecoration: 'none',
                  '&:hover': { textDecoration: 'underline' },
                }}
              >
                {item.title}
              </Link>
            ))}
          </Breadcrumbs>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : contents.length === 0 ? (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 8 }}>
              <FolderIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                {currentFolderId ? 'Esta pasta esta vazia' : 'Nenhum conteudo disponivel'}
              </Typography>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={2}>
            {contents.map((content) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={content.id}>
                <Card
                  sx={{
                    height: '100%',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4,
                    },
                  }}
                >
                  <CardActionArea
                    onClick={() => handleContentClick(content)}
                    sx={{ height: '100%', p: 2 }}
                  >
                    {/* Thumbnail for YouTube */}
                    {content.type === 'youtube' && content.thumbnail_url ? (
                      <Box
                        sx={{
                          position: 'relative',
                          mb: 2,
                          borderRadius: 1,
                          overflow: 'hidden',
                        }}
                      >
                        <Box
                          component="img"
                          src={content.thumbnail_url}
                          alt={content.title}
                          sx={{
                            width: '100%',
                            height: 120,
                            objectFit: 'cover',
                          }}
                        />
                        <Box
                          sx={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            bgcolor: 'rgba(0,0,0,0.7)',
                            borderRadius: '50%',
                            p: 0.5,
                          }}
                        >
                          <PlayIcon sx={{ fontSize: 40, color: 'white' }} />
                        </Box>
                        {content.duration && (
                          <Chip
                            label={formatDuration(content.duration)}
                            size="small"
                            sx={{
                              position: 'absolute',
                              bottom: 8,
                              right: 8,
                              bgcolor: 'rgba(0,0,0,0.8)',
                              color: 'white',
                            }}
                          />
                        )}
                      </Box>
                    ) : (
                      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                        {getContentIcon(content)}
                      </Box>
                    )}

                    <Typography
                      variant="subtitle1"
                      sx={{
                        fontWeight: 600,
                        mb: 0.5,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {content.title}
                    </Typography>

                    {content.description && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          mb: 1,
                        }}
                      >
                        {content.description}
                      </Typography>
                    )}

                    {/* Meta info */}
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {content.type === 'youtube' && content.channel && (
                        <Typography variant="caption" color="text.secondary">
                          {content.channel}
                        </Typography>
                      )}
                      {content.type === 'arquivo' && content.size && (
                        <Typography variant="caption" color="text.secondary">
                          {formatFileSize(content.size)}
                        </Typography>
                      )}
                    </Box>
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

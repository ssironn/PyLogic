'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Breadcrumbs,
  Link,
  CircularProgress,
  Alert,
  IconButton,
  Chip,
  Button,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  YouTube as YouTubeIcon,
  Description as DocIcon,
  OpenInNew as OpenInNewIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { DashboardLayout } from '@/components/layout';
import contentService, { ContentNode, Breadcrumb } from '@/services/content';

export default function ContentViewerPage() {
  const params = useParams();
  const router = useRouter();
  const classGroupId = params.classGroupId as string;
  const contentId = params.contentId as string;

  const [content, setContent] = useState<ContentNode | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadContent();
    loadBreadcrumbs();
  }, [contentId]);

  const loadContent = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await contentService.getContent(contentId);

      if (response.status === 'success' && response.data) {
        setContent(response.data);
      } else {
        setError(response.message || 'Erro ao carregar conteudo');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao conectar com o servidor');
    } finally {
      setIsLoading(false);
    }
  };

  const loadBreadcrumbs = async () => {
    try {
      const response = await contentService.getBreadcrumbs(contentId);
      if (response.status === 'success' && response.data) {
        setBreadcrumbs(response.data);
      }
    } catch (err) {
      console.error('Error loading breadcrumbs:', err);
    }
  };

  const handleBreadcrumbClick = (crumb: Breadcrumb) => {
    if (crumb.type === 'pasta') {
      // Navigate to folder view
      router.push(`/courses/${classGroupId}?folder=${crumb.id}`);
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    return `${m}m ${s}s`;
  };

  const getGoogleDocsEmbedUrl = (driveUrl?: string, driveFileId?: string) => {
    if (driveFileId) {
      return `https://drive.google.com/file/d/${driveFileId}/preview`;
    }
    if (driveUrl) {
      // Extract file ID from various Google Drive URL formats
      const match = driveUrl.match(/[-\w]{25,}/);
      if (match) {
        return `https://drive.google.com/file/d/${match[0]}/preview`;
      }
    }
    return null;
  };

  const renderYouTubePlayer = () => {
    if (!content?.youtube_id) return null;

    return (
      <Box sx={{ width: '100%' }}>
        <Box
          sx={{
            position: 'relative',
            paddingBottom: '56.25%', // 16:9 aspect ratio
            height: 0,
            overflow: 'hidden',
            borderRadius: 2,
            bgcolor: 'black',
          }}
        >
          <iframe
            src={`https://www.youtube.com/embed/${content.youtube_id}`}
            title={content.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              border: 'none',
            }}
          />
        </Box>

        {/* Video info */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
            {content.title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
            {content.channel && (
              <Chip
                icon={<YouTubeIcon />}
                label={content.channel}
                size="small"
                variant="outlined"
              />
            )}
            {content.duration && (
              <Typography variant="body2" color="text.secondary">
                Duracao: {formatDuration(content.duration)}
              </Typography>
            )}
          </Box>
          {content.description && (
            <Typography variant="body1" color="text.secondary">
              {content.description}
            </Typography>
          )}
        </Box>
      </Box>
    );
  };

  const renderFileViewer = () => {
    if (!content) return null;

    const embedUrl = getGoogleDocsEmbedUrl(content.drive_url, content.drive_file_id);

    return (
      <Box sx={{ width: '100%' }}>
        {/* File header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <DocIcon sx={{ fontSize: 40, color: '#4285f4' }} />
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                {content.title}
              </Typography>
              {content.original_name && (
                <Typography variant="body2" color="text.secondary">
                  {content.original_name}
                </Typography>
              )}
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {content.drive_url && (
              <Button
                variant="outlined"
                startIcon={<OpenInNewIcon />}
                href={content.drive_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Abrir no Drive
              </Button>
            )}
          </Box>
        </Box>

        {/* Embedded viewer */}
        {embedUrl ? (
          <Box
            sx={{
              position: 'relative',
              paddingBottom: '75%', // 4:3 aspect ratio for documents
              height: 0,
              overflow: 'hidden',
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            <iframe
              src={embedUrl}
              title={content.title}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                border: 'none',
              }}
            />
          </Box>
        ) : (
          <Alert severity="info">
            Este arquivo nao pode ser visualizado diretamente. Use o botao acima para abrir no Google Drive.
          </Alert>
        )}

        {/* Description */}
        {content.description && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body1" color="text.secondary">
              {content.description}
            </Typography>
          </Box>
        )}
      </Box>
    );
  };

  return (
    <DashboardLayout title="">
      <Box sx={{ maxWidth: 1000, mx: 'auto' }}>
        {/* Navigation */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <IconButton onClick={() => router.back()} size="small">
            <ArrowBackIcon />
          </IconButton>
          <Breadcrumbs>
            <Link
              component="button"
              variant="body2"
              onClick={() => router.push(`/courses/${classGroupId}`)}
              sx={{ cursor: 'pointer', textDecoration: 'none' }}
            >
              Voltar ao curso
            </Link>
            {breadcrumbs.map((crumb, index) => (
              <Link
                key={crumb.id}
                component="button"
                variant="body2"
                onClick={() => handleBreadcrumbClick(crumb)}
                sx={{
                  cursor: crumb.type === 'pasta' ? 'pointer' : 'default',
                  color: index === breadcrumbs.length - 1 ? 'text.primary' : 'text.secondary',
                  textDecoration: 'none',
                }}
              >
                {crumb.title}
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
        ) : content ? (
          <Card>
            <CardContent sx={{ p: 3 }}>
              {content.type === 'youtube' && renderYouTubePlayer()}
              {content.type === 'arquivo' && renderFileViewer()}
            </CardContent>
          </Card>
        ) : null}
      </Box>
    </DashboardLayout>
  );
}

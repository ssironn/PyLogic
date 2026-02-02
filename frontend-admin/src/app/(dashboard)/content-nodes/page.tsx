'use client';

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  YouTube as YouTubeIcon,
} from '@mui/icons-material';
import AdminLayout from '@/components/AdminLayout';
import ColorPicker from '@/components/ColorPicker';
import {
  contentNodesApi,
  classGroupsApi,
  youtubeApi,
  ContentNode,
  ContentNodeCreate,
  ContentNodeUpdate,
  ClassGroup,
} from '@/services/adminApi';

const TYPE_ICONS = {
  pasta: <FolderIcon />,
  arquivo: <FileIcon />,
  youtube: <YouTubeIcon />,
};

const TYPE_LABELS = {
  pasta: 'Pasta',
  arquivo: 'Arquivo',
  youtube: 'YouTube',
};

const VISIBILITY_LABELS = {
  publico: 'Publico',
  privado: 'Privado',
  restrito: 'Restrito',
};

export default function ContentNodesPage() {
  const [contentNodes, setContentNodes] = useState<ContentNode[]>([]);
  const [classGroups, setClassGroups] = useState<ClassGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [currentParentId, setCurrentParentId] = useState<string | null>(null);
  const [breadcrumbs, setBreadcrumbs] = useState<Array<{ id: string | null; title: string }>>([
    { id: null, title: 'Raiz' },
  ]);

  const [filterClassGroup, setFilterClassGroup] = useState<string>('');

  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [selectedItem, setSelectedItem] = useState<ContentNode | null>(null);
  const [formData, setFormData] = useState<ContentNodeCreate>({
    type: 'pasta',
    title: '',
    description: '',
    class_group_id: '',
    visibility: 'privado',
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<ContentNode | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const params: Record<string, string> = {};
      if (filterClassGroup) params.class_group_id = filterClassGroup;
      if (currentParentId) {
        params.parent_id = currentParentId;
      } else {
        params.parent_id = 'null';
      }

      const [contentRes, classGroupsRes] = await Promise.all([
        contentNodesApi.list(params),
        classGroupsApi.list(),
      ]);

      if (contentRes.status === 'success' && contentRes.data) {
        setContentNodes(contentRes.data);
      }
      if (classGroupsRes.status === 'success' && classGroupsRes.data) {
        setClassGroups(classGroupsRes.data);
      }
    } catch (err) {
      setError('Erro ao carregar dados');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filterClassGroup, currentParentId]);

  const handleNavigateToFolder = async (folder: ContentNode) => {
    setCurrentParentId(folder.id);
    setBreadcrumbs([...breadcrumbs, { id: folder.id, title: folder.title }]);
  };

  const handleNavigateToBreadcrumb = (index: number) => {
    const item = breadcrumbs[index];
    setCurrentParentId(item.id);
    setBreadcrumbs(breadcrumbs.slice(0, index + 1));
  };

  const handleOpenCreate = (type: 'pasta' | 'arquivo' | 'youtube') => {
    setDialogMode('create');
    setSelectedItem(null);
    setFormData({
      type,
      title: '',
      description: '',
      class_group_id: filterClassGroup || classGroups[0]?.id || '',
      parent_id: currentParentId || undefined,
      visibility: 'privado',
      ...(type === 'pasta' && { color: '', icon: '', allow_upload: false }),
      ...(type === 'arquivo' && { drive_file_id: '', drive_url: '', original_name: '', mime_type: '', size: 0 }),
      ...(type === 'youtube' && { youtube_id: '', full_url: '' }),
    });
    setFormError(null);
    setDialogOpen(true);
  };

  const handleOpenEdit = (item: ContentNode) => {
    setDialogMode('edit');
    setSelectedItem(item);
    setFormData({
      type: item.type,
      title: item.title,
      description: item.description || '',
      class_group_id: item.class_group_id,
      parent_id: item.parent_id || undefined,
      visibility: item.visibility,
      color: item.color,
      icon: item.icon,
      allow_upload: item.allow_upload,
      youtube_id: item.youtube_id,
      full_url: item.full_url,
      duration: item.duration,
      thumbnail_url: item.thumbnail_url,
      channel: item.channel,
    });
    setFormError(null);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedItem(null);
    setFormError(null);
  };

  const handleSave = async () => {
    setFormError(null);
    setIsSaving(true);

    try {
      if (dialogMode === 'create') {
        const response = await contentNodesApi.create(formData);
        if (response.status === 'success') {
          await loadData();
          handleCloseDialog();
        } else {
          setFormError(response.message || 'Erro ao criar conteudo');
        }
      } else if (selectedItem) {
        const updateData: ContentNodeUpdate = {
          title: formData.title,
          description: formData.description,
          visibility: formData.visibility,
        };
        if (formData.type === 'pasta') {
          updateData.color = formData.color;
          updateData.icon = formData.icon;
          updateData.allow_upload = formData.allow_upload;
        }
        if (formData.type === 'youtube') {
          updateData.duration = formData.duration;
          updateData.thumbnail_url = formData.thumbnail_url;
          updateData.channel = formData.channel;
        }
        const response = await contentNodesApi.update(selectedItem.id, updateData);
        if (response.status === 'success') {
          await loadData();
          handleCloseDialog();
        } else {
          setFormError(response.message || 'Erro ao atualizar conteudo');
        }
      }
    } catch (err) {
      setFormError('Erro ao salvar conteudo');
    } finally {
      setIsSaving(false);
    }
  };

  const handleOpenDelete = (item: ContentNode) => {
    setItemToDelete(item);
    setDeleteDialogOpen(true);
  };

  const handleCloseDelete = () => {
    setDeleteDialogOpen(false);
    setItemToDelete(null);
  };

  const handleDelete = async () => {
    if (!itemToDelete) return;

    setIsDeleting(true);
    try {
      const response = await contentNodesApi.delete(itemToDelete.id);
      if (response.status === 'success') {
        await loadData();
        handleCloseDelete();
      } else {
        setError(response.message || 'Erro ao excluir conteudo');
      }
    } catch (err) {
      setError('Erro ao excluir conteudo');
    } finally {
      setIsDeleting(false);
    }
  };

  const renderTypeSpecificFields = () => {
    if (dialogMode === 'edit') {
      if (formData.type === 'pasta') {
        return (
          <>
            <ColorPicker
              label="Cor"
              value={formData.color || ''}
              onChange={(color) => setFormData({ ...formData, color })}
            />
            <TextField
              fullWidth
              label="Icone"
              value={formData.icon || ''}
              onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
              margin="normal"
            />
          </>
        );
      }
      if (formData.type === 'youtube') {
        return (
          <>
            <TextField
              fullWidth
              label="Duracao (segundos)"
              type="number"
              value={formData.duration || ''}
              onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) || undefined })}
              margin="normal"
              helperText="Duracao do video em segundos"
            />
            <TextField
              fullWidth
              label="Canal"
              value={formData.channel || ''}
              onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
              margin="normal"
              helperText="Nome do canal do YouTube"
            />
          </>
        );
      }
      return null;
    }

    if (formData.type === 'pasta') {
      return (
        <>
          <ColorPicker
            label="Cor"
            value={formData.color || ''}
            onChange={(color) => setFormData({ ...formData, color })}
          />
          <TextField
            fullWidth
            label="Icone"
            value={formData.icon || ''}
            onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
            margin="normal"
          />
        </>
      );
    }

    if (formData.type === 'arquivo') {
      return (
        <>
          <TextField
            fullWidth
            label="Drive File ID"
            value={formData.drive_file_id || ''}
            onChange={(e) => setFormData({ ...formData, drive_file_id: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Drive URL"
            value={formData.drive_url || ''}
            onChange={(e) => setFormData({ ...formData, drive_url: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Nome Original"
            value={formData.original_name || ''}
            onChange={(e) => setFormData({ ...formData, original_name: e.target.value })}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Tipo MIME"
            value={formData.mime_type || ''}
            onChange={(e) => setFormData({ ...formData, mime_type: e.target.value })}
            margin="normal"
            required
            placeholder="application/pdf"
          />
          <TextField
            fullWidth
            label="Tamanho (bytes)"
            type="number"
            value={formData.size || ''}
            onChange={(e) => setFormData({ ...formData, size: parseInt(e.target.value) || 0 })}
            margin="normal"
            required
          />
        </>
      );
    }

    if (formData.type === 'youtube') {
      const extractYouTubeId = (url: string): string | null => {
        const patterns = [
          /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
          /^([a-zA-Z0-9_-]{11})$/,
        ];
        for (const pattern of patterns) {
          const match = url.match(pattern);
          if (match) return match[1];
        }
        return null;
      };

      const handleUrlChange = async (url: string) => {
        const videoId = extractYouTubeId(url);
        setFormData({
          ...formData,
          full_url: url,
          youtube_id: videoId || '',
        });

        if (videoId) {
          try {
            const response = await youtubeApi.getVideoInfo(videoId);
            if (response.status === 'success' && response.data) {
              setFormData((prev) => ({
                ...prev,
                full_url: url,
                youtube_id: videoId,
                title: prev.title || response.data!.title,
                duration: response.data!.duration,
                channel: response.data!.channel,
                thumbnail_url: response.data!.thumbnail_url,
              }));
            }
          } catch (err) {
            // API key not configured or error fetching - fields remain manual
            console.log('Could not fetch YouTube video info automatically');
          }
        }
      };

      const formatDuration = (seconds: number): string => {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        if (h > 0) return `${h}h ${m}m ${s}s`;
        if (m > 0) return `${m}m ${s}s`;
        return `${s}s`;
      };

      const hasVideoInfo = formData.youtube_id && (formData.duration || formData.channel || formData.thumbnail_url);

      return (
        <>
          <Alert severity="info" sx={{ mt: 2, mb: 1 }}>
            O video deve ser enviado primeiro para o YouTube. Apos o upload, copie a URL do video e cole no campo abaixo.
          </Alert>
          <TextField
            fullWidth
            label="URL do Video no YouTube"
            value={formData.full_url || ''}
            onChange={(e) => handleUrlChange(e.target.value)}
            margin="normal"
            required
            placeholder="https://www.youtube.com/watch?v=..."
            helperText="Cole a URL completa do video do YouTube"
            sx={{ mb: 2 }}
          />

          {hasVideoInfo && (
            <Paper variant="outlined" sx={{ p: 2, mt: 1, mb: 1, bgcolor: 'action.hover' }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
                Informacoes do Video
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                {formData.thumbnail_url && (
                  <Box
                    component="img"
                    src={formData.thumbnail_url}
                    alt="Thumbnail do video"
                    sx={{
                      width: 160,
                      height: 90,
                      borderRadius: 1,
                      objectFit: 'cover',
                      flexShrink: 0,
                    }}
                  />
                )}
                <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {formData.channel && (
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Canal
                      </Typography>
                      <Typography variant="body2">
                        {formData.channel}
                      </Typography>
                    </Box>
                  )}
                  {formData.duration && (
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Duracao
                      </Typography>
                      <Typography variant="body2">
                        {formatDuration(formData.duration)}
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Box>
            </Paper>
          )}

          {formData.youtube_id && !hasVideoInfo && (
            <Alert severity="warning" sx={{ mt: 1 }}>
              Nao foi possivel carregar as informacoes do video. A YouTube API Key pode nao estar configurada.
            </Alert>
          )}
        </>
      );
    }

    return null;
  };

  return (
    <AdminLayout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Conteudos</Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<FolderIcon />}
              onClick={() => handleOpenCreate('pasta')}
              disabled={classGroups.length === 0}
            >
              Nova Pasta
            </Button>
            <Button
              variant="outlined"
              startIcon={<FileIcon />}
              onClick={() => handleOpenCreate('arquivo')}
              disabled={classGroups.length === 0}
            >
              Novo Arquivo
            </Button>
            <Button
              variant="outlined"
              startIcon={<YouTubeIcon />}
              onClick={() => handleOpenCreate('youtube')}
              disabled={classGroups.length === 0}
            >
              Adicionar Video
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Filtrar por Turma</InputLabel>
            <Select
              value={filterClassGroup}
              onChange={(e) => setFilterClassGroup(e.target.value)}
              label="Filtrar por Turma"
            >
              <MenuItem value="">Todas</MenuItem>
              {classGroups.map((cg) => (
                <MenuItem key={cg.id} value={cg.id}>
                  {cg.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Breadcrumbs>
            {breadcrumbs.map((item, index) => (
              <Link
                key={item.id || 'root'}
                component="button"
                variant="body2"
                onClick={() => handleNavigateToBreadcrumb(index)}
                sx={{ cursor: 'pointer' }}
                underline={index < breadcrumbs.length - 1 ? 'hover' : 'none'}
                color={index < breadcrumbs.length - 1 ? 'inherit' : 'text.primary'}
              >
                {item.title}
              </Link>
            ))}
          </Breadcrumbs>
        </Box>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Tipo</TableCell>
                  <TableCell>Titulo</TableCell>
                  <TableCell>Turma</TableCell>
                  <TableCell>Visibilidade</TableCell>
                  <TableCell>Atualizado</TableCell>
                  <TableCell align="right">Acoes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {contentNodes.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      {currentParentId ? 'Pasta vazia' : 'Nenhum conteudo encontrado'}
                    </TableCell>
                  </TableRow>
                ) : (
                  contentNodes.map((item) => (
                    <TableRow
                      key={item.id}
                      sx={{
                        cursor: item.type === 'pasta' ? 'pointer' : 'default',
                        '&:hover': item.type === 'pasta' ? { bgcolor: 'action.hover' } : {},
                      }}
                      onClick={() => item.type === 'pasta' && handleNavigateToFolder(item)}
                    >
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'primary.main' }}>
                          {TYPE_ICONS[item.type]}
                          <Typography variant="body2">{TYPE_LABELS[item.type]}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography fontWeight={500}>{item.title}</Typography>
                        {item.description && (
                          <Typography variant="body2" color="text.secondary" noWrap sx={{ maxWidth: 300 }}>
                            {item.description}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {classGroups.find((cg) => cg.id === item.class_group_id)?.name || '-'}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={VISIBILITY_LABELS[item.visibility]}
                          size="small"
                          variant="outlined"
                          color={item.visibility === 'publico' ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(item.updated_at).toLocaleDateString('pt-BR')}
                      </TableCell>
                      <TableCell align="right" onClick={(e) => e.stopPropagation()}>
                        <IconButton size="small" onClick={() => handleOpenEdit(item)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton size="small" onClick={() => handleOpenDelete(item)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {dialogMode === 'create'
              ? `Novo ${TYPE_LABELS[formData.type]}`
              : `Editar ${TYPE_LABELS[formData.type]}`}
          </DialogTitle>
          <DialogContent>
            {formError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {formError}
              </Alert>
            )}
            <TextField
              fullWidth
              label="Titulo"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Descricao"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              margin="normal"
              multiline
              rows={2}
            />
            {dialogMode === 'create' && (
              <FormControl fullWidth margin="normal" required>
                <InputLabel>Turma</InputLabel>
                <Select
                  value={formData.class_group_id}
                  onChange={(e) => setFormData({ ...formData, class_group_id: e.target.value })}
                  label="Turma"
                >
                  {classGroups.map((cg) => (
                    <MenuItem key={cg.id} value={cg.id}>
                      {cg.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            <FormControl fullWidth margin="normal">
              <InputLabel>Visibilidade</InputLabel>
              <Select
                value={formData.visibility}
                onChange={(e) => setFormData({ ...formData, visibility: e.target.value as 'publico' | 'privado' | 'restrito' })}
                label="Visibilidade"
              >
                <MenuItem value="privado">Privado</MenuItem>
                <MenuItem value="publico">Publico</MenuItem>
                <MenuItem value="restrito">Restrito</MenuItem>
              </Select>
            </FormControl>
            {renderTypeSpecificFields()}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog} disabled={isSaving}>
              Cancelar
            </Button>
            <Button onClick={handleSave} variant="contained" disabled={isSaving}>
              {isSaving ? <CircularProgress size={20} /> : 'Salvar'}
            </Button>
          </DialogActions>
        </Dialog>

        <Dialog open={deleteDialogOpen} onClose={handleCloseDelete}>
          <DialogTitle>Confirmar Exclusao</DialogTitle>
          <DialogContent>
            <Typography>
              Tem certeza que deseja excluir &quot;{itemToDelete?.title}&quot;?
            </Typography>
            {itemToDelete?.type === 'pasta' && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                Pastas com conteudos nao podem ser excluidas. Remova os conteudos primeiro.
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDelete} disabled={isDeleting}>
              Cancelar
            </Button>
            <Button onClick={handleDelete} color="error" variant="contained" disabled={isDeleting}>
              {isDeleting ? <CircularProgress size={20} /> : 'Excluir'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </AdminLayout>
  );
}

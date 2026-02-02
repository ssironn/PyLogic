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
  Collapse,
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material';
import AdminLayout from '@/components/AdminLayout';
import {
  mathAreasApi,
  mathSubareasApi,
  MathArea,
  MathAreaCreate,
  MathAreaUpdate,
  MathSubarea,
  MathSubareaCreate,
  MathSubareaUpdate,
} from '@/services/adminApi';

export default function MathAreasPage() {
  const [areas, setAreas] = useState<MathArea[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Expanded rows for showing subareas
  const [expandedAreas, setExpandedAreas] = useState<Set<string>>(new Set());
  const [subareasMap, setSubareasMap] = useState<Record<string, MathSubarea[]>>({});
  const [loadingSubareas, setLoadingSubareas] = useState<Set<string>>(new Set());

  // Area dialog
  const [areaDialogOpen, setAreaDialogOpen] = useState(false);
  const [areaDialogMode, setAreaDialogMode] = useState<'create' | 'edit'>('create');
  const [selectedArea, setSelectedArea] = useState<MathArea | null>(null);
  const [areaFormData, setAreaFormData] = useState<MathAreaCreate>({
    name: '',
    description: '',
    icon: '',
    color: '',
    order: 0,
  });
  const [areaFormError, setAreaFormError] = useState<string | null>(null);
  const [isAreaSaving, setIsAreaSaving] = useState(false);

  // Subarea dialog
  const [subareaDialogOpen, setSubareaDialogOpen] = useState(false);
  const [subareaDialogMode, setSubareaDialogMode] = useState<'create' | 'edit'>('create');
  const [selectedSubarea, setSelectedSubarea] = useState<MathSubarea | null>(null);
  const [subareaParentId, setSubareaParentId] = useState<string | null>(null);
  const [subareaFormData, setSubareaFormData] = useState<MathSubareaCreate>({
    name: '',
    description: '',
    order: 0,
  });
  const [subareaFormError, setSubareaFormError] = useState<string | null>(null);
  const [isSubareaSaving, setIsSubareaSaving] = useState(false);

  // Delete dialogs
  const [deleteAreaDialogOpen, setDeleteAreaDialogOpen] = useState(false);
  const [areaToDelete, setAreaToDelete] = useState<MathArea | null>(null);
  const [isDeletingArea, setIsDeletingArea] = useState(false);

  const [deleteSubareaDialogOpen, setDeleteSubareaDialogOpen] = useState(false);
  const [subareaToDelete, setSubareaToDelete] = useState<MathSubarea | null>(null);
  const [isDeletingSubarea, setIsDeletingSubarea] = useState(false);

  useEffect(() => {
    loadAreas();
  }, []);

  const loadAreas = async () => {
    try {
      setIsLoading(true);
      const response = await mathAreasApi.list();
      if (response.status === 'success' && response.data) {
        setAreas(response.data);
      }
    } catch (err) {
      setError('Erro ao carregar areas');
    } finally {
      setIsLoading(false);
    }
  };

  const loadSubareas = async (areaId: string) => {
    if (subareasMap[areaId]) return; // Already loaded

    setLoadingSubareas((prev) => new Set(prev).add(areaId));
    try {
      const response = await mathAreasApi.getSubareas(areaId);
      if (response.status === 'success' && response.data) {
        setSubareasMap((prev) => ({ ...prev, [areaId]: response.data! }));
      }
    } catch (err) {
      console.error('Error loading subareas:', err);
    } finally {
      setLoadingSubareas((prev) => {
        const next = new Set(prev);
        next.delete(areaId);
        return next;
      });
    }
  };

  const toggleExpand = (areaId: string) => {
    setExpandedAreas((prev) => {
      const next = new Set(prev);
      if (next.has(areaId)) {
        next.delete(areaId);
      } else {
        next.add(areaId);
        loadSubareas(areaId);
      }
      return next;
    });
  };

  // Area CRUD handlers
  const handleOpenCreateArea = () => {
    setAreaDialogMode('create');
    setSelectedArea(null);
    setAreaFormData({
      name: '',
      description: '',
      icon: '',
      color: '',
      order: 0,
    });
    setAreaFormError(null);
    setAreaDialogOpen(true);
  };

  const handleOpenEditArea = (area: MathArea) => {
    setAreaDialogMode('edit');
    setSelectedArea(area);
    setAreaFormData({
      name: area.name,
      description: area.description || '',
      icon: area.icon || '',
      color: area.color || '',
      order: area.order,
    });
    setAreaFormError(null);
    setAreaDialogOpen(true);
  };

  const handleCloseAreaDialog = () => {
    setAreaDialogOpen(false);
    setSelectedArea(null);
    setAreaFormError(null);
  };

  const handleSaveArea = async () => {
    if (!areaFormData.name.trim()) {
      setAreaFormError('Nome e obrigatorio');
      return;
    }

    setAreaFormError(null);
    setIsAreaSaving(true);

    try {
      if (areaDialogMode === 'create') {
        const response = await mathAreasApi.create(areaFormData);
        if (response.status === 'success') {
          await loadAreas();
          handleCloseAreaDialog();
        } else {
          setAreaFormError(response.message || 'Erro ao criar area');
        }
      } else if (selectedArea) {
        const updateData: MathAreaUpdate = {
          ...areaFormData,
        };
        const response = await mathAreasApi.update(selectedArea.id, updateData);
        if (response.status === 'success') {
          await loadAreas();
          handleCloseAreaDialog();
        } else {
          setAreaFormError(response.message || 'Erro ao atualizar area');
        }
      }
    } catch (err) {
      setAreaFormError('Erro ao salvar area');
    } finally {
      setIsAreaSaving(false);
    }
  };

  const handleOpenDeleteArea = (area: MathArea) => {
    setAreaToDelete(area);
    setDeleteAreaDialogOpen(true);
  };

  const handleCloseDeleteArea = () => {
    setDeleteAreaDialogOpen(false);
    setAreaToDelete(null);
  };

  const handleDeleteArea = async () => {
    if (!areaToDelete) return;

    setIsDeletingArea(true);
    try {
      const response = await mathAreasApi.delete(areaToDelete.id);
      if (response.status === 'success') {
        await loadAreas();
        handleCloseDeleteArea();
      } else {
        setError(response.message || 'Erro ao excluir area');
        handleCloseDeleteArea();
      }
    } catch (err) {
      setError('Erro ao excluir area');
      handleCloseDeleteArea();
    } finally {
      setIsDeletingArea(false);
    }
  };

  // Subarea CRUD handlers
  const handleOpenCreateSubarea = (areaId: string) => {
    setSubareaDialogMode('create');
    setSelectedSubarea(null);
    setSubareaParentId(areaId);
    setSubareaFormData({
      name: '',
      description: '',
      order: 0,
    });
    setSubareaFormError(null);
    setSubareaDialogOpen(true);
  };

  const handleOpenEditSubarea = (subarea: MathSubarea) => {
    setSubareaDialogMode('edit');
    setSelectedSubarea(subarea);
    setSubareaParentId(subarea.math_area_id);
    setSubareaFormData({
      name: subarea.name,
      description: subarea.description || '',
      order: subarea.order,
    });
    setSubareaFormError(null);
    setSubareaDialogOpen(true);
  };

  const handleCloseSubareaDialog = () => {
    setSubareaDialogOpen(false);
    setSelectedSubarea(null);
    setSubareaParentId(null);
    setSubareaFormError(null);
  };

  const handleSaveSubarea = async () => {
    if (!subareaFormData.name.trim()) {
      setSubareaFormError('Nome e obrigatorio');
      return;
    }

    setSubareaFormError(null);
    setIsSubareaSaving(true);

    try {
      if (subareaDialogMode === 'create' && subareaParentId) {
        const response = await mathAreasApi.createSubarea(subareaParentId, subareaFormData);
        if (response.status === 'success') {
          // Reload subareas for this area
          setSubareasMap((prev) => {
            const next = { ...prev };
            delete next[subareaParentId];
            return next;
          });
          loadSubareas(subareaParentId);
          await loadAreas(); // Refresh counts
          handleCloseSubareaDialog();
        } else {
          setSubareaFormError(response.message || 'Erro ao criar subarea');
        }
      } else if (selectedSubarea) {
        const updateData: MathSubareaUpdate = {
          ...subareaFormData,
        };
        const response = await mathSubareasApi.update(selectedSubarea.id, updateData);
        if (response.status === 'success') {
          // Reload subareas for this area
          const areaId = selectedSubarea.math_area_id;
          setSubareasMap((prev) => {
            const next = { ...prev };
            delete next[areaId];
            return next;
          });
          loadSubareas(areaId);
          handleCloseSubareaDialog();
        } else {
          setSubareaFormError(response.message || 'Erro ao atualizar subarea');
        }
      }
    } catch (err) {
      setSubareaFormError('Erro ao salvar subarea');
    } finally {
      setIsSubareaSaving(false);
    }
  };

  const handleOpenDeleteSubarea = (subarea: MathSubarea) => {
    setSubareaToDelete(subarea);
    setDeleteSubareaDialogOpen(true);
  };

  const handleCloseDeleteSubarea = () => {
    setDeleteSubareaDialogOpen(false);
    setSubareaToDelete(null);
  };

  const handleDeleteSubarea = async () => {
    if (!subareaToDelete) return;

    setIsDeletingSubarea(true);
    try {
      const response = await mathSubareasApi.delete(subareaToDelete.id);
      if (response.status === 'success') {
        // Reload subareas for this area
        const areaId = subareaToDelete.math_area_id;
        setSubareasMap((prev) => {
          const next = { ...prev };
          delete next[areaId];
          return next;
        });
        loadSubareas(areaId);
        await loadAreas(); // Refresh counts
        handleCloseDeleteSubarea();
      } else {
        setError(response.message || 'Erro ao excluir subarea');
        handleCloseDeleteSubarea();
      }
    } catch (err) {
      setError('Erro ao excluir subarea');
      handleCloseDeleteSubarea();
    } finally {
      setIsDeletingSubarea(false);
    }
  };

  return (
    <AdminLayout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Areas Matematicas</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenCreateArea}
          >
            Nova Area
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell width={50}></TableCell>
                  <TableCell>Nome</TableCell>
                  <TableCell>Descricao</TableCell>
                  <TableCell align="center">Subareas</TableCell>
                  <TableCell align="center">Questoes</TableCell>
                  <TableCell align="center">Ordem</TableCell>
                  <TableCell align="center">Status</TableCell>
                  <TableCell align="right">Acoes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {areas.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      Nenhuma area encontrada
                    </TableCell>
                  </TableRow>
                ) : (
                  areas.map((area) => (
                    <React.Fragment key={area.id}>
                      <TableRow>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => toggleExpand(area.id)}
                          >
                            {expandedAreas.has(area.id) ? <CollapseIcon /> : <ExpandIcon />}
                          </IconButton>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {area.color && (
                              <Box
                                sx={{
                                  width: 16,
                                  height: 16,
                                  borderRadius: '50%',
                                  bgcolor: area.color,
                                }}
                              />
                            )}
                            <Typography fontWeight={500}>{area.name}</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary" noWrap sx={{ maxWidth: 200 }}>
                            {area.description || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Chip label={area.subarea_count} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell align="center">
                          <Chip label={area.question_count} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell align="center">{area.order}</TableCell>
                        <TableCell align="center">
                          <Chip
                            label={area.active ? 'Ativo' : 'Inativo'}
                            size="small"
                            color={area.active ? 'success' : 'default'}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Adicionar Subarea">
                            <IconButton size="small" onClick={() => handleOpenCreateSubarea(area.id)}>
                              <AddIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <IconButton size="small" onClick={() => handleOpenEditArea(area)}>
                            <EditIcon fontSize="small" />
                          </IconButton>
                          <IconButton size="small" onClick={() => handleOpenDeleteArea(area)}>
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell colSpan={8} sx={{ py: 0, borderBottom: expandedAreas.has(area.id) ? undefined : 'none' }}>
                          <Collapse in={expandedAreas.has(area.id)} timeout="auto" unmountOnExit>
                            <Box sx={{ py: 2, pl: 6 }}>
                              {loadingSubareas.has(area.id) ? (
                                <CircularProgress size={20} />
                              ) : (
                                <>
                                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                                    Subareas
                                  </Typography>
                                  {subareasMap[area.id]?.length === 0 ? (
                                    <Typography variant="body2" color="text.secondary">
                                      Nenhuma subarea cadastrada
                                    </Typography>
                                  ) : (
                                    <Table size="small">
                                      <TableHead>
                                        <TableRow>
                                          <TableCell>Nome</TableCell>
                                          <TableCell>Descricao</TableCell>
                                          <TableCell align="center">Questoes</TableCell>
                                          <TableCell align="center">Ordem</TableCell>
                                          <TableCell align="center">Status</TableCell>
                                          <TableCell align="right">Acoes</TableCell>
                                        </TableRow>
                                      </TableHead>
                                      <TableBody>
                                        {subareasMap[area.id]?.map((subarea) => (
                                          <TableRow key={subarea.id}>
                                            <TableCell>{subarea.name}</TableCell>
                                            <TableCell>
                                              <Typography variant="body2" color="text.secondary" noWrap sx={{ maxWidth: 150 }}>
                                                {subarea.description || '-'}
                                              </Typography>
                                            </TableCell>
                                            <TableCell align="center">
                                              <Chip label={subarea.question_count} size="small" variant="outlined" />
                                            </TableCell>
                                            <TableCell align="center">{subarea.order}</TableCell>
                                            <TableCell align="center">
                                              <Chip
                                                label={subarea.active ? 'Ativo' : 'Inativo'}
                                                size="small"
                                                color={subarea.active ? 'success' : 'default'}
                                                variant="outlined"
                                              />
                                            </TableCell>
                                            <TableCell align="right">
                                              <IconButton size="small" onClick={() => handleOpenEditSubarea(subarea)}>
                                                <EditIcon fontSize="small" />
                                              </IconButton>
                                              <IconButton size="small" onClick={() => handleOpenDeleteSubarea(subarea)}>
                                                <DeleteIcon fontSize="small" />
                                              </IconButton>
                                            </TableCell>
                                          </TableRow>
                                        ))}
                                      </TableBody>
                                    </Table>
                                  )}
                                </>
                              )}
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Area Dialog */}
        <Dialog open={areaDialogOpen} onClose={handleCloseAreaDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {areaDialogMode === 'create' ? 'Nova Area' : 'Editar Area'}
          </DialogTitle>
          <DialogContent>
            {areaFormError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {areaFormError}
              </Alert>
            )}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <TextField
                fullWidth
                label="Nome"
                value={areaFormData.name}
                onChange={(e) => setAreaFormData({ ...areaFormData, name: e.target.value })}
                required
              />
              <TextField
                fullWidth
                label="Descricao"
                value={areaFormData.description}
                onChange={(e) => setAreaFormData({ ...areaFormData, description: e.target.value })}
                multiline
                rows={2}
              />
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Icone"
                  value={areaFormData.icon}
                  onChange={(e) => setAreaFormData({ ...areaFormData, icon: e.target.value })}
                  placeholder="ex: calculate"
                />
                <TextField
                  fullWidth
                  label="Cor"
                  value={areaFormData.color}
                  onChange={(e) => setAreaFormData({ ...areaFormData, color: e.target.value })}
                  placeholder="ex: #3f51b5"
                />
              </Box>
              <TextField
                fullWidth
                label="Ordem"
                type="number"
                value={areaFormData.order}
                onChange={(e) => setAreaFormData({ ...areaFormData, order: parseInt(e.target.value) || 0 })}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseAreaDialog} disabled={isAreaSaving}>
              Cancelar
            </Button>
            <Button onClick={handleSaveArea} variant="contained" disabled={isAreaSaving}>
              {isAreaSaving ? <CircularProgress size={20} /> : 'Salvar'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Subarea Dialog */}
        <Dialog open={subareaDialogOpen} onClose={handleCloseSubareaDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {subareaDialogMode === 'create' ? 'Nova Subarea' : 'Editar Subarea'}
          </DialogTitle>
          <DialogContent>
            {subareaFormError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {subareaFormError}
              </Alert>
            )}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <TextField
                fullWidth
                label="Nome"
                value={subareaFormData.name}
                onChange={(e) => setSubareaFormData({ ...subareaFormData, name: e.target.value })}
                required
              />
              <TextField
                fullWidth
                label="Descricao"
                value={subareaFormData.description}
                onChange={(e) => setSubareaFormData({ ...subareaFormData, description: e.target.value })}
                multiline
                rows={2}
              />
              <TextField
                fullWidth
                label="Ordem"
                type="number"
                value={subareaFormData.order}
                onChange={(e) => setSubareaFormData({ ...subareaFormData, order: parseInt(e.target.value) || 0 })}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseSubareaDialog} disabled={isSubareaSaving}>
              Cancelar
            </Button>
            <Button onClick={handleSaveSubarea} variant="contained" disabled={isSubareaSaving}>
              {isSubareaSaving ? <CircularProgress size={20} /> : 'Salvar'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Area Dialog */}
        <Dialog open={deleteAreaDialogOpen} onClose={handleCloseDeleteArea}>
          <DialogTitle>Confirmar Exclusao</DialogTitle>
          <DialogContent>
            <Typography>
              Tem certeza que deseja excluir a area &quot;{areaToDelete?.name}&quot;?
            </Typography>
            {areaToDelete && areaToDelete.question_count > 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                Esta area possui {areaToDelete.question_count} questoes vinculadas.
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDeleteArea} disabled={isDeletingArea}>
              Cancelar
            </Button>
            <Button onClick={handleDeleteArea} color="error" variant="contained" disabled={isDeletingArea}>
              {isDeletingArea ? <CircularProgress size={20} /> : 'Excluir'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Subarea Dialog */}
        <Dialog open={deleteSubareaDialogOpen} onClose={handleCloseDeleteSubarea}>
          <DialogTitle>Confirmar Exclusao</DialogTitle>
          <DialogContent>
            <Typography>
              Tem certeza que deseja excluir a subarea &quot;{subareaToDelete?.name}&quot;?
            </Typography>
            {subareaToDelete && subareaToDelete.question_count > 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                Esta subarea possui {subareaToDelete.question_count} questoes vinculadas.
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDeleteSubarea} disabled={isDeletingSubarea}>
              Cancelar
            </Button>
            <Button onClick={handleDeleteSubarea} color="error" variant="contained" disabled={isDeletingSubarea}>
              {isDeletingSubarea ? <CircularProgress size={20} /> : 'Excluir'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </AdminLayout>
  );
}

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
  Switch,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import AdminLayout from '@/components/AdminLayout';
import { classGroupsApi, ClassGroup, ClassGroupCreate, ClassGroupUpdate } from '@/services/adminApi';

export default function ClassGroupsPage() {
  const [classGroups, setClassGroups] = useState<ClassGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [selectedItem, setSelectedItem] = useState<ClassGroup | null>(null);
  const [formData, setFormData] = useState<ClassGroupCreate>({
    name: '',
    description: '',
    access_code: '',
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<ClassGroup | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const response = await classGroupsApi.list();
      if (response.status === 'success' && response.data) {
        setClassGroups(response.data);
      }
    } catch (err) {
      setError('Erro ao carregar turmas');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenCreate = () => {
    setDialogMode('create');
    setSelectedItem(null);
    setFormData({ name: '', description: '', access_code: '' });
    setFormError(null);
    setDialogOpen(true);
  };

  const handleOpenEdit = (item: ClassGroup) => {
    setDialogMode('edit');
    setSelectedItem(item);
    setFormData({
      name: item.name,
      description: item.description || '',
      access_code: item.access_code,
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
        const response = await classGroupsApi.create(formData);
        if (response.status === 'success') {
          await loadData();
          handleCloseDialog();
        } else {
          setFormError(response.message || 'Erro ao criar turma');
        }
      } else if (selectedItem) {
        const updateData: ClassGroupUpdate = {
          name: formData.name,
          description: formData.description,
          access_code: formData.access_code,
        };
        const response = await classGroupsApi.update(selectedItem.id, updateData);
        if (response.status === 'success') {
          await loadData();
          handleCloseDialog();
        } else {
          setFormError(response.message || 'Erro ao atualizar turma');
        }
      }
    } catch (err) {
      setFormError('Erro ao salvar turma');
    } finally {
      setIsSaving(false);
    }
  };

  const handleOpenDelete = (item: ClassGroup) => {
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
      const response = await classGroupsApi.delete(itemToDelete.id);
      if (response.status === 'success') {
        await loadData();
        handleCloseDelete();
      } else {
        setError(response.message || 'Erro ao excluir turma');
      }
    } catch (err) {
      setError('Erro ao excluir turma');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleToggleActive = async (item: ClassGroup) => {
    try {
      await classGroupsApi.update(item.id, { active: !item.active });
      await loadData();
    } catch (err) {
      setError('Erro ao atualizar status');
    }
  };

  return (
    <AdminLayout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Turmas</Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpenCreate}>
            Nova Turma
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
                  <TableCell>Nome</TableCell>
                  <TableCell>Codigo de Acesso</TableCell>
                  <TableCell>Alunos</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Acoes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {classGroups.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      Nenhuma turma encontrada
                    </TableCell>
                  </TableRow>
                ) : (
                  classGroups.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Typography fontWeight={500}>{item.name}</Typography>
                        {item.description && (
                          <Typography variant="body2" color="text.secondary">
                            {item.description}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip label={item.access_code} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>{item.student_count}</TableCell>
                      <TableCell>
                        <Switch
                          checked={item.active}
                          onChange={() => handleToggleActive(item)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <IconButton size="small" onClick={() => handleOpenEdit(item)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDelete(item)}
                          disabled={item.student_count > 0}
                        >
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
            {dialogMode === 'create' ? 'Nova Turma' : 'Editar Turma'}
          </DialogTitle>
          <DialogContent>
            {formError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {formError}
              </Alert>
            )}
            <TextField
              fullWidth
              label="Nome"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
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
            <TextField
              fullWidth
              label="Codigo de Acesso"
              value={formData.access_code}
              onChange={(e) => setFormData({ ...formData, access_code: e.target.value })}
              margin="normal"
              required
              helperText="Codigo que os alunos usarao para se cadastrar"
            />
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
              Tem certeza que deseja excluir a turma &quot;{itemToDelete?.name}&quot;?
            </Typography>
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

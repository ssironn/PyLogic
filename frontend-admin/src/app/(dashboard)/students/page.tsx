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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import AdminLayout from '@/components/AdminLayout';
import {
  studentsApi,
  classGroupsApi,
  Student,
  StudentCreate,
  StudentUpdate,
  ClassGroup,
} from '@/services/adminApi';

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [classGroups, setClassGroups] = useState<ClassGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filterClassGroup, setFilterClassGroup] = useState<string>('');

  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [selectedItem, setSelectedItem] = useState<Student | null>(null);
  const [formData, setFormData] = useState<StudentCreate>({
    name: '',
    email: '',
    password: '',
    registration_number: '',
    class_group_id: '',
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<Student | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [studentsRes, classGroupsRes] = await Promise.all([
        studentsApi.list(filterClassGroup ? { class_group_id: filterClassGroup } : undefined),
        classGroupsApi.list(),
      ]);

      if (studentsRes.status === 'success' && studentsRes.data) {
        setStudents(studentsRes.data);
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
  }, [filterClassGroup]);

  const handleOpenCreate = () => {
    setDialogMode('create');
    setSelectedItem(null);
    setFormData({
      name: '',
      email: '',
      password: '',
      registration_number: '',
      class_group_id: classGroups[0]?.id || '',
    });
    setFormError(null);
    setDialogOpen(true);
  };

  const handleOpenEdit = (item: Student) => {
    setDialogMode('edit');
    setSelectedItem(item);
    setFormData({
      name: item.name,
      email: item.email,
      password: '',
      registration_number: item.registration_number || '',
      class_group_id: item.class_group_id,
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
        if (!formData.password) {
          setFormError('Senha e obrigatoria');
          setIsSaving(false);
          return;
        }
        const response = await studentsApi.create(formData);
        if (response.status === 'success') {
          await loadData();
          handleCloseDialog();
        } else {
          setFormError(response.message || 'Erro ao criar aluno');
        }
      } else if (selectedItem) {
        const updateData: StudentUpdate = {
          name: formData.name,
          email: formData.email,
          registration_number: formData.registration_number || undefined,
          class_group_id: formData.class_group_id,
        };
        if (formData.password) {
          updateData.password = formData.password;
        }
        const response = await studentsApi.update(selectedItem.id, updateData);
        if (response.status === 'success') {
          await loadData();
          handleCloseDialog();
        } else {
          setFormError(response.message || 'Erro ao atualizar aluno');
        }
      }
    } catch (err) {
      setFormError('Erro ao salvar aluno');
    } finally {
      setIsSaving(false);
    }
  };

  const handleOpenDelete = (item: Student) => {
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
      const response = await studentsApi.delete(itemToDelete.id);
      if (response.status === 'success') {
        await loadData();
        handleCloseDelete();
      } else {
        setError(response.message || 'Erro ao excluir aluno');
      }
    } catch (err) {
      setError('Erro ao excluir aluno');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleToggleActive = async (item: Student) => {
    try {
      await studentsApi.update(item.id, { active: !item.active });
      await loadData();
    } catch (err) {
      setError('Erro ao atualizar status');
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  return (
    <AdminLayout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Alunos</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenCreate}
            disabled={classGroups.length === 0}
          >
            Novo Aluno
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 2 }}>
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
                  <TableCell>Nome</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Turma</TableCell>
                  <TableCell>Matricula</TableCell>
                  <TableCell>Ultimo Acesso</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Acoes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {students.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      Nenhum aluno encontrado
                    </TableCell>
                  </TableRow>
                ) : (
                  students.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Typography fontWeight={500}>{item.name}</Typography>
                      </TableCell>
                      <TableCell>{item.email}</TableCell>
                      <TableCell>
                        <Chip label={item.class_group_name} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>{item.registration_number || '-'}</TableCell>
                      <TableCell>{formatDate(item.last_access)}</TableCell>
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
            {dialogMode === 'create' ? 'Novo Aluno' : 'Editar Aluno'}
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
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label={dialogMode === 'edit' ? 'Nova Senha (deixe em branco para manter)' : 'Senha'}
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              margin="normal"
              required={dialogMode === 'create'}
            />
            <TextField
              fullWidth
              label="Matricula"
              value={formData.registration_number}
              onChange={(e) => setFormData({ ...formData, registration_number: e.target.value })}
              margin="normal"
            />
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
              Tem certeza que deseja excluir o aluno &quot;{itemToDelete?.name}&quot;?
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

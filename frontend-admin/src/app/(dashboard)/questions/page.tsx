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
  Tabs,
  Tab,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Code as LatexIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import AdminLayout from '@/components/AdminLayout';
import {
  questionsApi,
  mathAreasApi,
  Question,
  QuestionCreate,
  QuestionUpdate,
  MathArea,
  MathSubarea,
} from '@/services/adminApi';

const DIFFICULTY_LABELS: Record<string, string> = {
  facil: 'Facil',
  medio: 'Medio',
  dificil: 'Dificil',
  especialista: 'Especialista',
};

const DIFFICULTY_COLORS: Record<string, 'success' | 'info' | 'warning' | 'error'> = {
  facil: 'success',
  medio: 'info',
  dificil: 'warning',
  especialista: 'error',
};

export default function QuestionsPage() {
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [mathAreas, setMathAreas] = useState<MathArea[]>([]);
  const [subareas, setSubareas] = useState<MathSubarea[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filterArea, setFilterArea] = useState<string>('');
  const [filterDifficulty, setFilterDifficulty] = useState<string>('');

  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [selectedItem, setSelectedItem] = useState<Question | null>(null);
  const [formData, setFormData] = useState<QuestionCreate>({
    math_area_id: '',
    title: '',
    content: '',
    difficulty: 'medio',
    tags: [],
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<Question | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    loadData();
  }, [filterArea, filterDifficulty]);

  useEffect(() => {
    loadMathAreas();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const params: Record<string, string> = {};
      if (filterArea) params.math_area_id = filterArea;
      if (filterDifficulty) params.difficulty = filterDifficulty;

      const response = await questionsApi.list(params);
      if (response.status === 'success' && response.data) {
        setQuestions(response.data);
      }
    } catch (err) {
      setError('Erro ao carregar questoes');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMathAreas = async () => {
    try {
      const response = await mathAreasApi.list();
      if (response.status === 'success' && response.data) {
        setMathAreas(response.data);
      }
    } catch (err) {
      console.error('Error loading math areas:', err);
    }
  };

  const loadSubareas = async (areaId: string) => {
    if (!areaId) {
      setSubareas([]);
      return;
    }
    try {
      const response = await mathAreasApi.getSubareas(areaId);
      if (response.status === 'success' && response.data) {
        setSubareas(response.data);
      }
    } catch (err) {
      console.error('Error loading subareas:', err);
    }
  };

  const handleOpenCreate = () => {
    setDialogMode('create');
    setSelectedItem(null);
    setFormData({
      math_area_id: '',
      title: '',
      content: '',
      difficulty: 'medio',
      tags: [],
    });
    setSubareas([]);
    setFormError(null);
    setActiveTab(0);
    setDialogOpen(true);
  };

  const handleOpenEdit = (item: Question) => {
    setDialogMode('edit');
    setSelectedItem(item);
    setFormData({
      math_area_id: item.math_area_id,
      math_subarea_id: item.math_subarea_id || undefined,
      title: item.title,
      content: item.content,
      content_latex: item.content_latex || undefined,
      answer: item.answer || undefined,
      answer_latex: item.answer_latex || undefined,
      explanation: item.explanation || undefined,
      explanation_latex: item.explanation_latex || undefined,
      difficulty: item.difficulty,
      tags: item.tags || [],
    });
    loadSubareas(item.math_area_id);
    setFormError(null);
    setActiveTab(0);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedItem(null);
    setFormError(null);
  };

  const handleAreaChange = (areaId: string) => {
    setFormData({ ...formData, math_area_id: areaId, math_subarea_id: undefined });
    loadSubareas(areaId);
  };

  const handleConvertToLatex = async (field: 'content' | 'answer' | 'explanation') => {
    const text = formData[field];
    if (!text) return;

    try {
      const response = await questionsApi.convertToLatex(text);
      if (response.status === 'success' && response.data) {
        const latexField = `${field}_latex` as keyof QuestionCreate;
        setFormData({ ...formData, [latexField]: response.data.latex });
      }
    } catch (err) {
      console.error('Error converting to LaTeX:', err);
    }
  };

  const handleSave = async () => {
    setFormError(null);
    setIsSaving(true);

    try {
      if (dialogMode === 'create') {
        const response = await questionsApi.create(formData);
        if (response.status === 'success') {
          await loadData();
          handleCloseDialog();
        } else {
          setFormError(response.message || 'Erro ao criar questao');
        }
      } else if (selectedItem) {
        const updateData: QuestionUpdate = {
          ...formData,
        };
        const response = await questionsApi.update(selectedItem.id, updateData);
        if (response.status === 'success') {
          await loadData();
          handleCloseDialog();
        } else {
          setFormError(response.message || 'Erro ao atualizar questao');
        }
      }
    } catch (err) {
      setFormError('Erro ao salvar questao');
    } finally {
      setIsSaving(false);
    }
  };

  const handleOpenDelete = (item: Question) => {
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
      const response = await questionsApi.delete(itemToDelete.id);
      if (response.status === 'success') {
        await loadData();
        handleCloseDelete();
      } else {
        setError(response.message || 'Erro ao excluir questao');
      }
    } catch (err) {
      setError('Erro ao excluir questao');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <AdminLayout>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Questoes</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenCreate}
            disabled={mathAreas.length === 0}
          >
            Nova Questao
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Filtrar por Area</InputLabel>
            <Select
              value={filterArea}
              onChange={(e) => setFilterArea(e.target.value)}
              label="Filtrar por Area"
            >
              <MenuItem value="">Todas</MenuItem>
              {mathAreas.map((area) => (
                <MenuItem key={area.id} value={area.id}>
                  {area.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Dificuldade</InputLabel>
            <Select
              value={filterDifficulty}
              onChange={(e) => setFilterDifficulty(e.target.value)}
              label="Dificuldade"
            >
              <MenuItem value="">Todas</MenuItem>
              <MenuItem value="facil">Facil</MenuItem>
              <MenuItem value="medio">Medio</MenuItem>
              <MenuItem value="dificil">Dificil</MenuItem>
              <MenuItem value="especialista">Especialista</MenuItem>
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
                  <TableCell>Titulo</TableCell>
                  <TableCell>Area</TableCell>
                  <TableCell>Subarea</TableCell>
                  <TableCell>Dificuldade</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Acoes</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {questions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      Nenhuma questao encontrada
                    </TableCell>
                  </TableRow>
                ) : (
                  questions.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Typography fontWeight={500}>{item.title}</Typography>
                      </TableCell>
                      <TableCell>{item.math_area_name || '-'}</TableCell>
                      <TableCell>{item.math_subarea_name || '-'}</TableCell>
                      <TableCell>
                        <Chip
                          label={DIFFICULTY_LABELS[item.difficulty]}
                          size="small"
                          color={DIFFICULTY_COLORS[item.difficulty]}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={item.active ? 'Ativo' : 'Inativo'}
                          size="small"
                          color={item.active ? 'success' : 'default'}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <IconButton size="small" onClick={() => router.push(`/questions/${item.id}`)}>
                          <ViewIcon fontSize="small" />
                        </IconButton>
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

        {/* Create/Edit Dialog */}
        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>
            {dialogMode === 'create' ? 'Nova Questao' : 'Editar Questao'}
          </DialogTitle>
          <DialogContent>
            {formError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {formError}
              </Alert>
            )}

            <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 2 }}>
              <Tab label="Informacoes" />
              <Tab label="Conteudo" />
              <Tab label="Resposta" />
            </Tabs>

            {activeTab === 0 && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Titulo"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <FormControl fullWidth required error={!formData.math_area_id}>
                    <InputLabel>Area Matematica</InputLabel>
                    <Select
                      value={formData.math_area_id}
                      onChange={(e) => handleAreaChange(e.target.value)}
                      label="Area Matematica"
                      displayEmpty
                    >
                      <MenuItem value="" disabled>
                        Selecione uma area
                      </MenuItem>
                      {mathAreas.map((area) => (
                        <MenuItem key={area.id} value={area.id}>
                          {area.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl fullWidth>
                    <InputLabel>Subarea</InputLabel>
                    <Select
                      value={formData.math_subarea_id || ''}
                      onChange={(e) => setFormData({ ...formData, math_subarea_id: e.target.value || undefined })}
                      label="Subarea"
                    >
                      <MenuItem value="">Nenhuma</MenuItem>
                      {subareas.map((sub) => (
                        <MenuItem key={sub.id} value={sub.id}>
                          {sub.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>
                <FormControl fullWidth>
                  <InputLabel>Dificuldade</InputLabel>
                  <Select
                    value={formData.difficulty}
                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value as QuestionCreate['difficulty'] })}
                    label="Dificuldade"
                  >
                    <MenuItem value="facil">Facil</MenuItem>
                    <MenuItem value="medio">Medio</MenuItem>
                    <MenuItem value="dificil">Dificil</MenuItem>
                    <MenuItem value="especialista">Especialista</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            )}

            {activeTab === 1 && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle2">Conteudo (Texto)</Typography>
                    <Button
                      size="small"
                      startIcon={<LatexIcon />}
                      onClick={() => handleConvertToLatex('content')}
                    >
                      Converter para LaTeX
                    </Button>
                  </Box>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    value={formData.content}
                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                    placeholder="Digite o conteudo da questao..."
                  />
                </Box>
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>Conteudo (LaTeX)</Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    value={formData.content_latex || ''}
                    onChange={(e) => setFormData({ ...formData, content_latex: e.target.value })}
                    placeholder="Versao em LaTeX do conteudo..."
                    helperText="Sera gerado automaticamente se deixado em branco"
                  />
                </Box>
              </Box>
            )}

            {activeTab === 2 && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle2">Resposta (Texto)</Typography>
                    <Button
                      size="small"
                      startIcon={<LatexIcon />}
                      onClick={() => handleConvertToLatex('answer')}
                    >
                      Converter para LaTeX
                    </Button>
                  </Box>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    value={formData.answer || ''}
                    onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
                    placeholder="Resposta da questao..."
                  />
                </Box>
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>Resposta (LaTeX)</Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    value={formData.answer_latex || ''}
                    onChange={(e) => setFormData({ ...formData, answer_latex: e.target.value })}
                    placeholder="Versao em LaTeX da resposta..."
                  />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle2">Explicacao (Texto)</Typography>
                    <Button
                      size="small"
                      startIcon={<LatexIcon />}
                      onClick={() => handleConvertToLatex('explanation')}
                    >
                      Converter para LaTeX
                    </Button>
                  </Box>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    value={formData.explanation || ''}
                    onChange={(e) => setFormData({ ...formData, explanation: e.target.value })}
                    placeholder="Explicacao detalhada..."
                  />
                </Box>
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>Explicacao (LaTeX)</Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    value={formData.explanation_latex || ''}
                    onChange={(e) => setFormData({ ...formData, explanation_latex: e.target.value })}
                    placeholder="Versao em LaTeX da explicacao..."
                  />
                </Box>
              </Box>
            )}
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

        {/* Delete Dialog */}
        <Dialog open={deleteDialogOpen} onClose={handleCloseDelete}>
          <DialogTitle>Confirmar Exclusao</DialogTitle>
          <DialogContent>
            <Typography>
              Tem certeza que deseja excluir a questao &quot;{itemToDelete?.title}&quot;?
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

'use client';

import React, { useEffect, useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  Send as SendIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  CheckCircle as AnsweredIcon,
  AccessTime as PendingIcon,
} from '@mui/icons-material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import {
  questionsService,
  Question,
  MathArea,
  MathSubarea,
  ApprovedAnswer,
} from '@/services/questions';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

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

function LatexRenderer({ content }: { content: string }) {
  if (!content) return null;

  const parts: React.ReactNode[] = [];
  let key = 0;
  const latexPattern = /(\$\$[\s\S]*?\$\$|\$[^$\n]+?\$)/g;
  let lastIndex = 0;
  let match;

  while ((match = latexPattern.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push(<span key={key++}>{content.slice(lastIndex, match.index)}</span>);
    }

    const latex = match[0];
    if (latex.startsWith('$$')) {
      const mathContent = latex.slice(2, -2).trim();
      try {
        parts.push(
          <Box key={key++} sx={{ my: 2, textAlign: 'center' }}>
            <BlockMath math={mathContent} />
          </Box>
        );
      } catch {
        parts.push(
          <Box key={key++} sx={{ color: 'error.main', fontFamily: 'monospace' }}>
            {latex}
          </Box>
        );
      }
    } else {
      const mathContent = latex.slice(1, -1).trim();
      try {
        parts.push(<InlineMath key={key++} math={mathContent} />);
      } catch {
        parts.push(
          <span key={key++} style={{ color: 'red', fontFamily: 'monospace' }}>
            {latex}
          </span>
        );
      }
    }

    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < content.length) {
    parts.push(<span key={key++}>{content.slice(lastIndex)}</span>);
  }

  if (parts.length === 0) {
    return <Typography>{content}</Typography>;
  }

  return <Box sx={{ lineHeight: 2 }}>{parts}</Box>;
}

export default function QuestionsPage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [mathAreas, setMathAreas] = useState<MathArea[]>([]);
  const [subareas, setSubareas] = useState<MathSubarea[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [filterArea, setFilterArea] = useState<string>('');
  const [filterSubarea, setFilterSubarea] = useState<string>('');
  const [filterDifficulty, setFilterDifficulty] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Answer dialog
  const [answerDialogOpen, setAnswerDialogOpen] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [answerContent, setAnswerContent] = useState('');
  const [answerLatex, setAnswerLatex] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Approved answers
  const [approvedAnswers, setApprovedAnswers] = useState<ApprovedAnswer[]>([]);
  const [showApprovedAnswers, setShowApprovedAnswers] = useState(false);
  const [loadingApproved, setLoadingApproved] = useState(false);

  useEffect(() => {
    loadMathAreas();
  }, []);

  useEffect(() => {
    loadQuestions();
  }, [filterArea, filterSubarea, filterDifficulty]);

  useEffect(() => {
    if (filterArea) {
      loadSubareas(filterArea);
    } else {
      setSubareas([]);
      setFilterSubarea('');
    }
  }, [filterArea]);

  // Live LaTeX conversion
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (answerContent && answerContent !== answerLatex) {
        try {
          const latex = await questionsService.convertToLatex(answerContent);
          setAnswerLatex(latex);
        } catch {
          setAnswerLatex(answerContent);
        }
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [answerContent]);

  const loadMathAreas = async () => {
    try {
      const areas = await questionsService.listMathAreas();
      setMathAreas(areas);
    } catch {
      console.error('Error loading math areas');
    }
  };

  const loadSubareas = async (areaId: string) => {
    try {
      const subs = await questionsService.listSubareas(areaId);
      setSubareas(subs);
    } catch {
      console.error('Error loading subareas');
    }
  };

  const loadQuestions = async () => {
    try {
      setIsLoading(true);
      const params: Record<string, string> = {};
      if (filterArea) params.math_area_id = filterArea;
      if (filterSubarea) params.math_subarea_id = filterSubarea;
      if (filterDifficulty) params.difficulty = filterDifficulty;

      const data = await questionsService.listQuestions(params);
      setQuestions(data);
    } catch {
      setError('Erro ao carregar questoes');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenAnswer = (question: Question) => {
    setSelectedQuestion(question);
    setAnswerContent(question.my_answer?.content || '');
    setAnswerLatex(question.my_answer?.content_latex || question.my_answer?.content || '');
    setSubmitError(null);
    setSubmitSuccess(false);
    setShowApprovedAnswers(false);
    setApprovedAnswers([]);
    setAnswerDialogOpen(true);
  };

  const handleSubmitAnswer = async () => {
    if (!selectedQuestion || !answerContent.trim()) return;

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const result = await questionsService.submitAnswer(selectedQuestion.id, {
        content: answerContent,
        content_latex: answerLatex,
      });

      if (result) {
        setSubmitSuccess(true);
        await loadQuestions();
        setTimeout(() => {
          setAnswerDialogOpen(false);
        }, 1500);
      } else {
        setSubmitError('Erro ao enviar resposta');
      }
    } catch {
      setSubmitError('Erro ao enviar resposta');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLoadApprovedAnswers = async () => {
    if (!selectedQuestion) return;

    setLoadingApproved(true);
    try {
      const answers = await questionsService.getApprovedAnswers(selectedQuestion.id);
      setApprovedAnswers(answers);
      setShowApprovedAnswers(true);
    } catch {
      console.error('Error loading approved answers');
    } finally {
      setLoadingApproved(false);
    }
  };

  // Filter questions by search query
  const filteredQuestions = useMemo(() => {
    if (!searchQuery) return questions;
    const query = searchQuery.toLowerCase();
    return questions.filter(
      (q) =>
        q.title.toLowerCase().includes(query) ||
        q.content.toLowerCase().includes(query)
    );
  }, [questions, searchQuery]);

  return (
    <DashboardLayout title="Questoes">
      <Box>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Area</InputLabel>
                <Select
                  value={filterArea}
                  onChange={(e) => setFilterArea(e.target.value)}
                  label="Area"
                >
                  <MenuItem value="">Todas</MenuItem>
                  {mathAreas.map((area) => (
                    <MenuItem key={area.id} value={area.id}>
                      {area.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small" disabled={!filterArea}>
                <InputLabel>Subarea</InputLabel>
                <Select
                  value={filterSubarea}
                  onChange={(e) => setFilterSubarea(e.target.value)}
                  label="Subarea"
                >
                  <MenuItem value="">Todas</MenuItem>
                  {subareas.map((sub) => (
                    <MenuItem key={sub.id} value={sub.id}>
                      {sub.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
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
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Buscar"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar por titulo ou conteudo..."
              />
            </Grid>
          </Grid>
        </Paper>

        {/* Questions list */}
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : filteredQuestions.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography color="text.secondary">
              Nenhuma questao encontrada.
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={2}>
            {filteredQuestions.map((question) => (
              <Grid item xs={12} key={question.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="h6">{question.title}</Typography>
                        {question.my_answer && (
                          question.my_answer.status === 'aprovado' ? (
                            <Chip
                              icon={<AnsweredIcon />}
                              label="Respondido"
                              size="small"
                              color="success"
                            />
                          ) : question.my_answer.status === 'pendente' ? (
                            <Chip
                              icon={<PendingIcon />}
                              label="Aguardando"
                              size="small"
                              color="warning"
                            />
                          ) : (
                            <Chip
                              label="Rejeitado"
                              size="small"
                              color="error"
                            />
                          )
                        )}
                      </Box>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Chip
                          label={question.math_area_name}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={DIFFICULTY_LABELS[question.difficulty]}
                          size="small"
                          color={DIFFICULTY_COLORS[question.difficulty]}
                        />
                      </Box>
                    </Box>

                    <Box sx={{ maxHeight: 150, overflow: 'hidden', mb: 2 }}>
                      <LatexRenderer content={question.content_latex || question.content} />
                    </Box>

                    {question.my_answer?.feedback && (
                      <Alert severity={question.my_answer.is_correct ? 'success' : 'info'} sx={{ mt: 2 }}>
                        <Typography variant="subtitle2">Feedback:</Typography>
                        <Typography variant="body2">{question.my_answer.feedback}</Typography>
                        {question.my_answer.score !== null && (
                          <Typography variant="body2" fontWeight={600}>
                            Nota: {question.my_answer.score}
                          </Typography>
                        )}
                      </Alert>
                    )}
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'flex-end' }}>
                    {question.approved_answers_count > 0 && (
                      <Typography variant="body2" color="text.secondary" sx={{ mr: 'auto' }}>
                        {question.approved_answers_count} resposta(s) aprovada(s)
                      </Typography>
                    )}
                    <Button
                      variant="contained"
                      startIcon={<SendIcon />}
                      onClick={() => handleOpenAnswer(question)}
                    >
                      {question.my_answer ? 'Ver / Editar Resposta' : 'Responder'}
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Answer Dialog */}
        <Dialog
          open={answerDialogOpen}
          onClose={() => setAnswerDialogOpen(false)}
          maxWidth="lg"
          fullWidth
        >
          <DialogTitle>
            {selectedQuestion?.title}
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <Chip label={selectedQuestion?.math_area_name} size="small" />
              {selectedQuestion?.difficulty && (
                <Chip
                  label={DIFFICULTY_LABELS[selectedQuestion.difficulty]}
                  size="small"
                  color={DIFFICULTY_COLORS[selectedQuestion.difficulty]}
                />
              )}
            </Box>
          </DialogTitle>
          <DialogContent dividers>
            {submitSuccess ? (
              <Alert severity="success" sx={{ mb: 2 }}>
                Resposta enviada com sucesso! Aguarde a avaliacao.
              </Alert>
            ) : (
              <>
                {submitError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {submitError}
                  </Alert>
                )}

                {/* Question content */}
                <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Enunciado
                  </Typography>
                  <LatexRenderer
                    content={selectedQuestion?.content_latex || selectedQuestion?.content || ''}
                  />
                </Paper>

                {/* Answer input with side preview */}
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Sua Resposta
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={8}
                      value={answerContent}
                      onChange={(e) => setAnswerContent(e.target.value)}
                      placeholder="Digite sua resposta aqui... Use $ para formulas inline e $$ para formulas em bloco."
                      helperText="Dica: x^2 vira x², sqrt(x) vira raiz quadrada, alpha vira letra grega"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Preview (LaTeX)
                    </Typography>
                    <Paper
                      sx={{
                        p: 2,
                        minHeight: 200,
                        maxHeight: 250,
                        overflow: 'auto',
                        bgcolor: 'grey.50',
                      }}
                    >
                      {answerLatex ? (
                        <LatexRenderer content={answerLatex} />
                      ) : (
                        <Typography color="text.secondary">
                          O preview aparecera aqui...
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                </Grid>

                {/* Approved answers section */}
                {selectedQuestion && selectedQuestion.approved_answers_count > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Divider sx={{ mb: 2 }} />
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        cursor: 'pointer',
                      }}
                      onClick={() => {
                        if (!showApprovedAnswers && approvedAnswers.length === 0) {
                          handleLoadApprovedAnswers();
                        } else {
                          setShowApprovedAnswers(!showApprovedAnswers);
                        }
                      }}
                    >
                      <Typography variant="subtitle2">
                        Respostas Aprovadas ({selectedQuestion.approved_answers_count})
                      </Typography>
                      <IconButton size="small">
                        {showApprovedAnswers ? <CollapseIcon /> : <ExpandIcon />}
                      </IconButton>
                      {loadingApproved && <CircularProgress size={20} sx={{ ml: 1 }} />}
                    </Box>
                    <Collapse in={showApprovedAnswers}>
                      <Box sx={{ mt: 2 }}>
                        {approvedAnswers.map((answer) => (
                          <Paper key={answer.id} sx={{ p: 2, mb: 2, bgcolor: 'success.lighter' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="subtitle2">{answer.student_name}</Typography>
                              {answer.score !== null && (
                                <Chip label={`Nota: ${answer.score}`} size="small" color="success" />
                              )}
                            </Box>
                            <LatexRenderer content={answer.content_latex || answer.content} />
                          </Paper>
                        ))}
                      </Box>
                    </Collapse>
                  </Box>
                )}
              </>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAnswerDialogOpen(false)} disabled={isSubmitting}>
              {submitSuccess ? 'Fechar' : 'Cancelar'}
            </Button>
            {!submitSuccess && (
              <Button
                variant="contained"
                onClick={handleSubmitAnswer}
                disabled={isSubmitting || !answerContent.trim()}
                startIcon={isSubmitting ? <CircularProgress size={20} /> : <SendIcon />}
              >
                Enviar Resposta
              </Button>
            )}
          </DialogActions>
        </Dialog>
      </Box>
    </DashboardLayout>
  );
}

'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Divider,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  Badge,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Edit as EditIcon,
  QuestionAnswer as AnswersIcon,
  Check as ApproveIcon,
  Close as RejectIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import AdminLayout from '@/components/AdminLayout';
import { questionsApi, answersApi, Question, Answer, AnswerStats } from '@/services/adminApi';
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

const STATUS_LABELS: Record<string, string> = {
  pendente: 'Pendente',
  aprovado: 'Aprovado',
  rejeitado: 'Rejeitado',
};

const STATUS_COLORS: Record<string, 'warning' | 'success' | 'error'> = {
  pendente: 'warning',
  aprovado: 'success',
  rejeitado: 'error',
};

interface LatexRendererProps {
  content: string;
}

function LatexRenderer({ content }: LatexRendererProps) {
  if (!content) return null;

  const parts: React.ReactNode[] = [];
  let key = 0;
  const latexPattern = /(\$\$[\s\S]*?\$\$|\$[^$\n]+?\$)/g;
  let lastIndex = 0;
  let match;

  while ((match = latexPattern.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push(
        <span key={key++}>{content.slice(lastIndex, match.index)}</span>
      );
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

export default function QuestionViewPage() {
  const params = useParams();
  const router = useRouter();
  const questionId = params.id as string;

  const [question, setQuestion] = useState<Question | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  // Answers state
  const [answersDialogOpen, setAnswersDialogOpen] = useState(false);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [answersStats, setAnswersStats] = useState<AnswerStats | null>(null);
  const [loadingAnswers, setLoadingAnswers] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<Answer | null>(null);
  const [answerDetailOpen, setAnswerDetailOpen] = useState(false);

  // Review state
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  const [reviewAnswer, setReviewAnswer] = useState<Answer | null>(null);
  const [reviewData, setReviewData] = useState({
    status: 'aprovado' as 'aprovado' | 'rejeitado',
    is_correct: false,
    feedback: '',
    score: 0,
  });
  const [isReviewing, setIsReviewing] = useState(false);

  useEffect(() => {
    loadQuestion();
    loadAnswersStats();
  }, [questionId]);

  const loadQuestion = async () => {
    try {
      setIsLoading(true);
      const response = await questionsApi.get(questionId);
      if (response.status === 'success' && response.data) {
        setQuestion(response.data);
      } else {
        setError('Questao nao encontrada');
      }
    } catch {
      setError('Erro ao carregar questao');
    } finally {
      setIsLoading(false);
    }
  };

  const loadAnswersStats = async () => {
    try {
      const response = await questionsApi.getAnswersStats(questionId);
      if (response.status === 'success' && response.data) {
        setAnswersStats(response.data);
      }
    } catch {
      console.error('Error loading answers stats');
    }
  };

  const loadAnswers = async () => {
    setLoadingAnswers(true);
    try {
      const response = await questionsApi.getAnswers(questionId);
      if (response.status === 'success' && response.data) {
        setAnswers(response.data);
      }
    } catch {
      console.error('Error loading answers');
    } finally {
      setLoadingAnswers(false);
    }
  };

  const handleOpenAnswers = () => {
    setAnswersDialogOpen(true);
    loadAnswers();
  };

  const handleOpenReview = (answer: Answer) => {
    setReviewAnswer(answer);
    setReviewData({
      status: answer.status === 'rejeitado' ? 'rejeitado' : 'aprovado',
      is_correct: answer.is_correct || false,
      feedback: answer.feedback || '',
      score: answer.score || 0,
    });
    setReviewDialogOpen(true);
  };

  const handleReview = async () => {
    if (!reviewAnswer) return;

    setIsReviewing(true);
    try {
      const response = await answersApi.review(reviewAnswer.id, reviewData);
      if (response.status === 'success') {
        await loadAnswers();
        await loadAnswersStats();
        setReviewDialogOpen(false);
      }
    } catch {
      console.error('Error reviewing answer');
    } finally {
      setIsReviewing(false);
    }
  };

  const handleDeleteAnswer = async (answerId: string) => {
    if (!confirm('Tem certeza que deseja excluir esta resposta?')) return;

    try {
      const response = await answersApi.delete(answerId);
      if (response.status === 'success') {
        await loadAnswers();
        await loadAnswersStats();
      }
    } catch {
      console.error('Error deleting answer');
    }
  };

  const handleViewAnswer = (answer: Answer) => {
    setSelectedAnswer(answer);
    setAnswerDetailOpen(true);
  };

  if (isLoading) {
    return (
      <AdminLayout>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </AdminLayout>
    );
  }

  if (error || !question) {
    return (
      <AdminLayout>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || 'Questao nao encontrada'}
        </Alert>
        <Button startIcon={<BackIcon />} onClick={() => router.push('/questions')}>
          Voltar
        </Button>
      </AdminLayout>
    );
  }

  const renderContent = (text: string | null, latex: string | null) => {
    if (activeTab === 0) {
      const content = latex || text;
      if (!content) return <Typography color="text.secondary">-</Typography>;
      return <LatexRenderer content={content} />;
    } else {
      return (
        <Typography
          component="pre"
          sx={{
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            bgcolor: 'grey.100',
            p: 2,
            borderRadius: 1,
            fontSize: '0.875rem',
          }}
        >
          {latex || text || '-'}
        </Typography>
      );
    }
  };

  return (
    <AdminLayout>
      <Box>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Button
              startIcon={<BackIcon />}
              onClick={() => router.push('/questions')}
              sx={{ mb: 1 }}
            >
              Voltar
            </Button>
            <Typography variant="h4">{question.title}</Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <Chip label={question.math_area_name || 'Sem area'} size="small" />
              {question.math_subarea_name && (
                <Chip label={question.math_subarea_name} size="small" variant="outlined" />
              )}
              <Chip
                label={DIFFICULTY_LABELS[question.difficulty]}
                size="small"
                color={DIFFICULTY_COLORS[question.difficulty]}
              />
              <Chip
                label={question.active ? 'Ativo' : 'Inativo'}
                size="small"
                color={question.active ? 'success' : 'default'}
                variant="outlined"
              />
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Badge badgeContent={answersStats?.pending || 0} color="warning">
              <Button
                variant="outlined"
                startIcon={<AnswersIcon />}
                onClick={handleOpenAnswers}
              >
                Respostas ({answersStats?.total || 0})
              </Button>
            </Badge>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              onClick={() => router.push(`/questions?edit=${question.id}`)}
            >
              Editar
            </Button>
          </Box>
        </Box>

        {/* View mode toggle */}
        <Box sx={{ mb: 2 }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
            <Tab label="Preview LaTeX" />
            <Tab label="Codigo Fonte" />
          </Tabs>
        </Box>

        {/* Content */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Enunciado
          </Typography>
          {renderContent(question.content, question.content_latex)}
        </Paper>

        {/* Answer */}
        {(question.answer || question.answer_latex) && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Resposta Esperada
            </Typography>
            {renderContent(question.answer, question.answer_latex)}
          </Paper>
        )}

        {/* Explanation */}
        {(question.explanation || question.explanation_latex) && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Explicacao
            </Typography>
            {renderContent(question.explanation, question.explanation_latex)}
          </Paper>
        )}

        {/* Metadata */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Informacoes
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                ID
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                {question.id}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Criado em
              </Typography>
              <Typography variant="body2">
                {question.created_at ? new Date(question.created_at).toLocaleString('pt-BR') : '-'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Atualizado em
              </Typography>
              <Typography variant="body2">
                {question.updated_at ? new Date(question.updated_at).toLocaleString('pt-BR') : '-'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Tags
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                {question.tags && question.tags.length > 0 ? (
                  question.tags.map((tag) => (
                    <Chip key={tag} label={tag} size="small" variant="outlined" />
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Sem tags
                  </Typography>
                )}
              </Box>
            </Box>
          </Box>
        </Paper>

        {/* Answers Dialog */}
        <Dialog open={answersDialogOpen} onClose={() => setAnswersDialogOpen(false)} maxWidth="lg" fullWidth>
          <DialogTitle>
            Respostas dos Alunos
            {answersStats && (
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Chip label={`Total: ${answersStats.total}`} size="small" />
                <Chip label={`Pendentes: ${answersStats.pending}`} size="small" color="warning" />
                <Chip label={`Aprovadas: ${answersStats.approved}`} size="small" color="success" />
                <Chip label={`Rejeitadas: ${answersStats.rejected}`} size="small" color="error" />
              </Box>
            )}
          </DialogTitle>
          <DialogContent>
            {loadingAnswers ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : answers.length === 0 ? (
              <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
                Nenhuma resposta enviada ainda.
              </Typography>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Aluno</TableCell>
                      <TableCell>Resposta</TableCell>
                      <TableCell align="center">Status</TableCell>
                      <TableCell align="center">Correto</TableCell>
                      <TableCell align="center">Nota</TableCell>
                      <TableCell>Enviado em</TableCell>
                      <TableCell align="right">Acoes</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {answers.map((answer) => (
                      <TableRow key={answer.id}>
                        <TableCell>
                          <Typography fontWeight={500}>{answer.student_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {answer.student_email}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography
                            variant="body2"
                            sx={{
                              maxWidth: 300,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {answer.content}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={STATUS_LABELS[answer.status]}
                            size="small"
                            color={STATUS_COLORS[answer.status]}
                          />
                        </TableCell>
                        <TableCell align="center">
                          {answer.is_correct !== null ? (
                            answer.is_correct ? (
                              <Chip label="Sim" size="small" color="success" variant="outlined" />
                            ) : (
                              <Chip label="Nao" size="small" color="error" variant="outlined" />
                            )
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell align="center">
                          {answer.score !== null ? answer.score : '-'}
                        </TableCell>
                        <TableCell>
                          {answer.created_at
                            ? new Date(answer.created_at).toLocaleString('pt-BR')
                            : '-'}
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Ver detalhes">
                            <IconButton size="small" onClick={() => handleViewAnswer(answer)}>
                              <ViewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Avaliar">
                            <IconButton size="small" onClick={() => handleOpenReview(answer)}>
                              <ApproveIcon fontSize="small" color="success" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Excluir">
                            <IconButton size="small" onClick={() => handleDeleteAnswer(answer.id)}>
                              <DeleteIcon fontSize="small" color="error" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAnswersDialogOpen(false)}>Fechar</Button>
          </DialogActions>
        </Dialog>

        {/* Answer Detail Dialog */}
        <Dialog open={answerDetailOpen} onClose={() => setAnswerDetailOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Detalhes da Resposta</DialogTitle>
          <DialogContent>
            {selectedAnswer && (
              <Box>
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Aluno
                  </Typography>
                  <Typography>{selectedAnswer.student_name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedAnswer.student_email}
                  </Typography>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                    Resposta (Preview)
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <LatexRenderer content={selectedAnswer.content_latex || selectedAnswer.content} />
                  </Paper>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                    Resposta (Codigo)
                  </Typography>
                  <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                    <Typography
                      component="pre"
                      sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', fontSize: '0.875rem', m: 0 }}
                    >
                      {selectedAnswer.content_latex || selectedAnswer.content}
                    </Typography>
                  </Paper>
                </Box>

                {selectedAnswer.feedback && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Feedback
                    </Typography>
                    <Typography>{selectedAnswer.feedback}</Typography>
                  </Box>
                )}

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Chip label={STATUS_LABELS[selectedAnswer.status]} color={STATUS_COLORS[selectedAnswer.status]} />
                  {selectedAnswer.is_correct !== null && (
                    <Chip
                      label={selectedAnswer.is_correct ? 'Correto' : 'Incorreto'}
                      color={selectedAnswer.is_correct ? 'success' : 'error'}
                      variant="outlined"
                    />
                  )}
                  {selectedAnswer.score !== null && (
                    <Chip label={`Nota: ${selectedAnswer.score}`} variant="outlined" />
                  )}
                </Box>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAnswerDetailOpen(false)}>Fechar</Button>
            {selectedAnswer && (
              <Button variant="contained" onClick={() => {
                setAnswerDetailOpen(false);
                handleOpenReview(selectedAnswer);
              }}>
                Avaliar
              </Button>
            )}
          </DialogActions>
        </Dialog>

        {/* Review Dialog */}
        <Dialog open={reviewDialogOpen} onClose={() => setReviewDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Avaliar Resposta</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={reviewData.status}
                  onChange={(e) => setReviewData({ ...reviewData, status: e.target.value as 'aprovado' | 'rejeitado' })}
                  label="Status"
                >
                  <MenuItem value="aprovado">Aprovado</MenuItem>
                  <MenuItem value="rejeitado">Rejeitado</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Correto?</InputLabel>
                <Select
                  value={reviewData.is_correct ? 'sim' : 'nao'}
                  onChange={(e) => setReviewData({ ...reviewData, is_correct: e.target.value === 'sim' })}
                  label="Correto?"
                >
                  <MenuItem value="sim">Sim</MenuItem>
                  <MenuItem value="nao">Nao</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Nota (0-10)"
                type="number"
                inputProps={{ min: 0, max: 10, step: 0.5 }}
                value={reviewData.score}
                onChange={(e) => setReviewData({ ...reviewData, score: parseFloat(e.target.value) || 0 })}
              />

              <TextField
                fullWidth
                label="Feedback"
                multiline
                rows={3}
                value={reviewData.feedback}
                onChange={(e) => setReviewData({ ...reviewData, feedback: e.target.value })}
                placeholder="Feedback para o aluno..."
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setReviewDialogOpen(false)} disabled={isReviewing}>
              Cancelar
            </Button>
            <Button onClick={handleReview} variant="contained" disabled={isReviewing}>
              {isReviewing ? <CircularProgress size={20} /> : 'Salvar'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </AdminLayout>
  );
}

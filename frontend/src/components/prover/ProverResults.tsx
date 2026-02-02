'use client';

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  Alert,
  AlertTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import HelpIcon from '@mui/icons-material/Help';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import PsychologyIcon from '@mui/icons-material/Psychology';
import ShuffleIcon from '@mui/icons-material/Shuffle';
import TableChartIcon from '@mui/icons-material/TableChart';
import { ProveResponse, Transformation } from '@/services/api';
import { PropositionDisplay } from '@/utils/propositionRenderer';

// Mapeamento de nomes de leis lógicas para português
const lawTranslations: Record<string, string> = {
  // Leis básicas
  'double_negation': 'Dupla negação',
  'idempotence': 'Idempotência',
  'absorption': 'Absorção',
  'complement': 'Complemento',
  'identity': 'Identidade',
  'domination': 'Dominação',
  'commutativity': 'Comutatividade',
  'associativity': 'Associatividade',
  'distributivity': 'Distributividade',

  // Leis de De Morgan
  'de_morgan': 'Lei de De Morgan',
  'de_morgan_reverse': 'Lei de De Morgan (reversa)',

  // Implicação
  'implication_elimination': 'Eliminando implicação',
  'implication_introduction': 'Introduzindo implicação',
  'implication_constant': 'Implicação com constante',
  'contraposition': 'Contraposição',

  // Outras
  'factoring': 'Fatoração',
  'negation_constant': 'Negação de constante',
  'exportation': 'Exportação',
  'importation': 'Importação',
};

// Mapeamento de nomes de métodos para português
const methodTranslations: Record<string, string> = {
  'direct': 'Direto',
  'direto': 'Direto',
  'contrapositive': 'Contrapositiva',
  'contrapositiva': 'Contrapositiva',
  'absurdity': 'Absurdo',
  'absurdo': 'Absurdo',
  'bidirectional': 'Bidirecional',
  'bidirecional': 'Bidirecional',
  'automatic': 'Qualquer um',
  'automatico': 'Qualquer um',
  'verificacao_semantica': 'Verificação Semântica',
  'igualdade_sintatica': 'Igualdade Sintática',
};

function translateLaw(law: string): string {
  return lawTranslations[law] || law.replace(/_/g, ' ');
}

function translateMethod(method: string): string {
  return methodTranslations[method] || method.replace(/_/g, ' ');
}

function formatVariable(v: string): string {
  // Converte ~p para ¬p
  return v.replace(/^~/, '¬');
}

interface ProverResultsProps {
  result: ProveResponse | null;
  loading: boolean;
}

function StepItem({ step, index, isLast, isSuccess }: { step: Transformation; index: number; isLast: boolean; isSuccess: boolean }) {
  return (
    <ListItem
      sx={{
        borderRadius: 2,
        mb: 1,
        backgroundColor: step.guided_by_nn
          ? 'rgba(99, 102, 241, 0.06)'
          : 'rgba(100, 116, 139, 0.05)',
        border: step.guided_by_nn
          ? '1px solid rgba(99, 102, 241, 0.2)'
          : '1px solid rgba(100, 116, 139, 0.15)',
        transition: 'all 0.2s ease',
        '&:hover': {
          backgroundColor: step.guided_by_nn
            ? 'rgba(99, 102, 241, 0.1)'
            : 'rgba(100, 116, 139, 0.08)',
          transform: 'translateX(4px)',
        },
      }}
    >
      <ListItemIcon>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 32,
            height: 32,
            borderRadius: '50%',
            backgroundColor: step.guided_by_nn ? 'primary.main' : 'grey.600',
            color: 'white',
            fontSize: '0.85rem',
            fontWeight: 600,
          }}
        >
          {step.iteration + 1}
        </Box>
      </ListItemIcon>
      <ListItemText
        disableTypography
        primary={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              size="small"
              icon={step.guided_by_nn ? <PsychologyIcon /> : <ShuffleIcon />}
              label={step.guided_by_nn ? 'NN' : 'RND'}
              color={step.guided_by_nn ? 'primary' : 'default'}
              sx={{ fontWeight: 600 }}
            />
            <Chip
              size="small"
              label={`P${step.proposition}`}
              variant="outlined"
              color="secondary"
            />
            <Typography
              component="span"
              sx={{
                color: 'warning.main',
                fontWeight: 500,
              }}
            >
              {translateLaw(step.law)}
            </Typography>
            {step.subexpression && (
              <Typography
                component="span"
                sx={{
                  color: 'text.secondary',
                  fontSize: '0.85rem',
                }}
              >
                em "<PropositionDisplay text={step.subexpression} size="small" />"
              </Typography>
            )}
          </Box>
        }
        secondary={
          <Box sx={{ mt: 1 }}>
            <Typography component="span" variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              <ArrowForwardIcon sx={{ fontSize: 12, mr: 0.5, verticalAlign: 'middle' }} />
              Resultado: <PropositionDisplay text={step.result} size="small" />
            </Typography>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mt: 1,
                p: 1.5,
                borderRadius: 1,
                backgroundColor: 'rgba(15, 15, 20, 0.5)',
                border: '1px solid rgba(99, 102, 241, 0.08)',
              }}
            >
              <Box sx={{
                flex: 1,
                textAlign: 'center',
                p: 1,
                borderRadius: 1,
                backgroundColor: step.proposition === 1 ? 'rgba(251, 146, 60, 0.1)' : 'transparent',
                border: step.proposition === 1 ? '1px solid rgba(251, 146, 60, 0.3)' : '1px solid transparent',
              }}>
                <Typography component="span" variant="caption" sx={{ display: 'block', mb: 0.5, color: step.proposition === 1 ? 'warning.main' : 'text.secondary' }}>P₁</Typography>
                <PropositionDisplay text={step.p1} size="medium" />
              </Box>
              <Typography component="span" sx={{ color: isLast && isSuccess ? 'success.main' : 'primary.main', fontWeight: 'bold', fontSize: '1.2rem' }}>≡</Typography>
              <Box sx={{
                flex: 1,
                textAlign: 'center',
                p: 1,
                borderRadius: 1,
                backgroundColor: step.proposition === 2 ? 'rgba(251, 146, 60, 0.1)' : 'transparent',
                border: step.proposition === 2 ? '1px solid rgba(251, 146, 60, 0.3)' : '1px solid transparent',
              }}>
                <Typography component="span" variant="caption" sx={{ display: 'block', mb: 0.5, color: step.proposition === 2 ? 'warning.main' : 'text.secondary' }}>P₂</Typography>
                <PropositionDisplay text={step.p2} size="medium" />
              </Box>
            </Box>
          </Box>
        }
      />
    </ListItem>
  );
}

export default function ProverResults({ result, loading }: ProverResultsProps) {
  if (loading) {
    return (
      <Paper
        elevation={3}
        sx={{
          p: 4,
          textAlign: 'center',
          background: 'linear-gradient(145deg, rgba(15, 15, 20, 0.95) 0%, rgba(5, 5, 10, 0.98) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.15)',
        }}
      >
        <Typography variant="h6" color="text.secondary">
          Processando prova...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          O modelo neural está analisando as proposições
        </Typography>
      </Paper>
    );
  }

  if (!result) {
    return null;
  }

  const isSuccess = result.success && result.equivalent;

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        background: 'linear-gradient(145deg, rgba(15, 15, 20, 0.95) 0%, rgba(5, 5, 10, 0.98) 100%)',
        border: `1px solid ${isSuccess ? 'rgba(34, 197, 94, 0.25)' : result.equivalent ? 'rgba(245, 158, 11, 0.25)' : 'rgba(239, 68, 68, 0.25)'}`,
      }}
    >
      {/* Result Header */}
      <Alert
        severity={isSuccess ? 'success' : result.equivalent ? 'warning' : 'error'}
        icon={isSuccess ? <CheckCircleIcon /> : result.equivalent ? <HelpIcon /> : <CancelIcon />}
        sx={{ mb: 3 }}
      >
        <AlertTitle sx={{ fontWeight: 600 }}>
          {isSuccess
            ? 'Equivalência Provada!'
            : result.equivalent
            ? 'Semanticamente Equivalentes (prova sintática não encontrada)'
            : 'Proposições Não Equivalentes'}
        </AlertTitle>
        {result.message}
      </Alert>

      {/* Summary Stats */}
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
        <Chip
          label={`Método: ${translateMethod(result.method_used)}`}
          color="primary"
          variant="outlined"
        />
        <Chip
          label={`${result.iterations} iterações`}
          color="secondary"
          variant="outlined"
        />
        <Chip
          label={`${result.nn_predictions} predições NN`}
          color="info"
          variant="outlined"
          icon={<PsychologyIcon />}
        />
      </Box>

      {/* Initial Propositions */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Proposições Iniciais:
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', sm: 'row' } }}>
          <Paper
            sx={{
              p: 2,
              flex: 1,
              backgroundColor: 'rgba(100, 116, 139, 0.08)',
              border: '1px solid rgba(100, 116, 139, 0.15)',
            }}
          >
            <Typography variant="caption" color="text.secondary">P₁ Inicial:</Typography>
            <PropositionDisplay text={result.proposition1_initial} size="large" />
          </Paper>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography variant="h5" sx={{ color: 'text.secondary' }}>
              ≟
            </Typography>
          </Box>
          <Paper
            sx={{
              p: 2,
              flex: 1,
              backgroundColor: 'rgba(100, 116, 139, 0.08)',
              border: '1px solid rgba(100, 116, 139, 0.15)',
            }}
          >
            <Typography variant="caption" color="text.secondary">P₂ Inicial:</Typography>
            <PropositionDisplay text={result.proposition2_initial} size="large" />
          </Paper>
        </Box>
      </Box>

      {/* Final Propositions */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Proposições Finais:
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', sm: 'row' } }}>
          <Paper
            sx={{
              p: 2,
              flex: 1,
              backgroundColor: 'rgba(99, 102, 241, 0.08)',
              border: '1px solid rgba(99, 102, 241, 0.15)',
            }}
          >
            <Typography variant="caption" color="text.secondary">P₁ Final:</Typography>
            <PropositionDisplay text={result.proposition1_final} size="large" />
          </Paper>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography variant="h5" sx={{ color: isSuccess ? 'success.main' : result.equivalent ? 'warning.main' : 'error.main' }}>
              {isSuccess ? '≡' : result.equivalent ? '≟' : '≢'}
            </Typography>
          </Box>
          <Paper
            sx={{
              p: 2,
              flex: 1,
              backgroundColor: 'rgba(34, 197, 94, 0.08)',
              border: '1px solid rgba(34, 197, 94, 0.15)',
            }}
          >
            <Typography variant="caption" color="text.secondary">P₂ Final:</Typography>
            <PropositionDisplay text={result.proposition2_final} size="large" />
          </Paper>
        </Box>
      </Box>

      {/* Transformation Steps */}
      {result.transformations && result.transformations.length > 0 && (
        <>
          <Divider sx={{ my: 3 }} />
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ArrowForwardIcon />
            Passos da Transformação ({result.transformations.length})
          </Typography>
          <List sx={{ mt: 2 }}>
            {result.transformations.map((step, index) => (
              <StepItem
                key={index}
                step={step}
                index={index}
                isLast={index === result.transformations.length - 1}
                isSuccess={result.success && result.equivalent}
              />
            ))}
          </List>
        </>
      )}

      {/* Truth Table */}
      {result.truth_table && result.truth_table.rows.length > 0 && (
        <>
          <Divider sx={{ my: 3 }} />
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TableChartIcon />
            Tabela Verdade
          </Typography>
          <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' }, mt: 2 }}>
            {/* P1 Truth Table */}
            <Box sx={{ flex: 1, overflowX: 'auto' }}>
              <Typography variant="subtitle2" color="primary" gutterBottom sx={{ textAlign: 'center' }}>
                P₁: <PropositionDisplay text={result.proposition1_initial} size="small" />
              </Typography>
              <TableContainer component={Paper} sx={{ backgroundColor: 'rgba(99, 102, 241, 0.03)', border: '1px solid rgba(99, 102, 241, 0.1)' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {result.truth_table.variables.map((v) => (
                        <TableCell key={v} align="center" sx={{ fontWeight: 'bold', fontStyle: v.startsWith('~') ? 'normal' : 'italic' }}>{formatVariable(v)}</TableCell>
                      ))}
                      {result.truth_table.subexpressions_p1?.map((sub) => (
                        <TableCell key={sub} align="center" sx={{ fontWeight: 'bold', fontSize: '0.75rem', maxWidth: 120, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          <PropositionDisplay text={sub} size="small" />
                        </TableCell>
                      ))}
                      <TableCell align="center" sx={{ fontWeight: 'bold', color: 'primary.main' }}>P₁</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {result.truth_table.rows.map((row, idx) => (
                      <TableRow key={idx}>
                        {result.truth_table.variables.map((v) => (
                          <TableCell key={v} align="center">{row.values[v] ? 'V' : 'F'}</TableCell>
                        ))}
                        {result.truth_table.subexpressions_p1?.map((sub) => (
                          <TableCell key={sub} align="center" sx={{ color: row.subvalues_p1?.[sub] ? 'success.main' : 'error.main' }}>
                            {row.subvalues_p1?.[sub] != null ? (row.subvalues_p1[sub] ? 'V' : 'F') : '-'}
                          </TableCell>
                        ))}
                        <TableCell align="center" sx={{ fontWeight: 'bold', color: row.p1 ? 'success.main' : 'error.main' }}>
                          {row.p1 ? 'V' : 'F'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>

            {/* P2 Truth Table */}
            <Box sx={{ flex: 1, overflowX: 'auto' }}>
              <Typography variant="subtitle2" color="secondary" gutterBottom sx={{ textAlign: 'center' }}>
                P₂: <PropositionDisplay text={result.proposition2_initial} size="small" />
              </Typography>
              <TableContainer component={Paper} sx={{ backgroundColor: 'rgba(34, 197, 94, 0.03)', border: '1px solid rgba(34, 197, 94, 0.1)' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {result.truth_table.variables.map((v) => (
                        <TableCell key={v} align="center" sx={{ fontWeight: 'bold', fontStyle: v.startsWith('~') ? 'normal' : 'italic' }}>{formatVariable(v)}</TableCell>
                      ))}
                      {result.truth_table.subexpressions_p2?.map((sub) => (
                        <TableCell key={sub} align="center" sx={{ fontWeight: 'bold', fontSize: '0.75rem', maxWidth: 120, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          <PropositionDisplay text={sub} size="small" />
                        </TableCell>
                      ))}
                      <TableCell align="center" sx={{ fontWeight: 'bold', color: 'secondary.main' }}>P₂</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {result.truth_table.rows.map((row, idx) => (
                      <TableRow key={idx}>
                        {result.truth_table.variables.map((v) => (
                          <TableCell key={v} align="center">{row.values[v] ? 'V' : 'F'}</TableCell>
                        ))}
                        {result.truth_table.subexpressions_p2?.map((sub) => (
                          <TableCell key={sub} align="center" sx={{ color: row.subvalues_p2?.[sub] ? 'success.main' : 'error.main' }}>
                            {row.subvalues_p2?.[sub] != null ? (row.subvalues_p2[sub] ? 'V' : 'F') : '-'}
                          </TableCell>
                        ))}
                        <TableCell align="center" sx={{ fontWeight: 'bold', color: row.p2 ? 'success.main' : 'error.main' }}>
                          {row.p2 ? 'V' : 'F'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </Box>
        </>
      )}

      {/* Legend */}
      <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid rgba(148, 163, 184, 0.2)' }}>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <span><PsychologyIcon sx={{ fontSize: 14, verticalAlign: 'middle', mr: 0.5 }} /> NN = Guiado por Rede Neural</span>
          <span><ShuffleIcon sx={{ fontSize: 14, verticalAlign: 'middle', mr: 0.5 }} /> RND = Seleção Aleatória</span>
        </Typography>
      </Box>
    </Paper>
  );
}

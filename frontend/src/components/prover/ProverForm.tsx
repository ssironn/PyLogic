'use client';

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Tooltip,
  IconButton,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { proverService, ProveRequest, ProveResponse } from '@/services/api';
import { PropositionDisplay } from '@/utils/propositionRenderer';

interface ProverFormProps {
  onResult: (result: ProveResponse | null) => void;
  onLoading: (loading: boolean) => void;
}

const PROOF_METHODS = [
  { value: 'automatic', label: 'Qualquer um' },
  { value: 'direct', label: 'Direto' },
  { value: 'contrapositive', label: 'Contrapositiva' },
  { value: 'absurd', label: 'Absurdo' },
  { value: 'bidirectional', label: 'Bidirecional' },
];

const MAX_ITERATIONS_OPTIONS = [50, 100, 150, 300, 500];

export default function ProverForm({ onResult, onLoading }: ProverFormProps) {
  const [prop1, setProp1] = useState('');
  const [prop2, setProp2] = useState('');
  const [method, setMethod] = useState<ProveRequest['method']>('automatic');
  const [maxIterations, setMaxIterations] = useState(50);
  const [allowBidirectional, setAllowBidirectional] = useState(false);
  const [showFullSteps, setShowFullSteps] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!prop1.trim() || !prop2.trim()) {
      setError('Por favor, preencha ambas as proposições');
      return;
    }

    setLoading(true);
    onLoading(true);

    try {
      const result = await proverService.prove({
        proposition1: prop1,
        proposition2: prop2,
        method: method,
        max_iterations: maxIterations,
        allow_bidirectional: allowBidirectional,
        verbose: showFullSteps,
      });
      onResult(result);
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'Erro ao processar a requisição';
      setError(message);
      onResult(null);
    } finally {
      setLoading(false);
      onLoading(false);
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        background: 'linear-gradient(145deg, rgba(15, 15, 20, 0.95) 0%, rgba(5, 5, 10, 0.98) 100%)',
        border: '1px solid rgba(99, 102, 241, 0.15)',
        backdropFilter: 'blur(10px)',
      }}
    >
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Proposition Inputs */}
          <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', md: 'row' }, alignItems: 'flex-start' }}>
            {/* P1 Input with Preview */}
            <Box sx={{ flex: 1, width: '100%' }}>
              <TextField
                fullWidth
                label="Proposição 1 (P₁)"
                value={prop1}
                onChange={(e) => setProp1(e.target.value)}
                placeholder="Ex: p ^ q"
                variant="outlined"
                InputProps={{
                  endAdornment: (
                    <Tooltip title="Use: ~ (não), ^ (e), v (ou), -> (implica), T (verdadeiro), F (falso)">
                      <IconButton size="small">
                        <HelpOutlineIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  ),
                }}
              />
              {/* P1 Preview */}
              {prop1.trim() && (
                <Box
                  sx={{
                    mt: 1,
                    p: 1.5,
                    borderRadius: 2,
                    backgroundColor: 'rgba(99, 102, 241, 0.08)',
                    border: '1px solid rgba(99, 102, 241, 0.2)',
                    minHeight: 40,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <PropositionDisplay text={prop1} size="large" />
                </Box>
              )}
            </Box>

            {/* Equivalence Symbol */}
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', pt: { xs: 0, md: 2 } }}>
              <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 300 }}>≡</Typography>
            </Box>

            {/* P2 Input with Preview */}
            <Box sx={{ flex: 1, width: '100%' }}>
              <TextField
                fullWidth
                label="Proposição 2 (P₂)"
                value={prop2}
                onChange={(e) => setProp2(e.target.value)}
                placeholder="Ex: q ^ p"
                variant="outlined"
                InputProps={{
                  endAdornment: (
                    <Tooltip title="Use: ~ (não), ^ (e), v (ou), -> (implica), T (verdadeiro), F (falso)">
                      <IconButton size="small">
                        <HelpOutlineIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  ),
                }}
              />
              {/* P2 Preview */}
              {prop2.trim() && (
                <Box
                  sx={{
                    mt: 1,
                    p: 1.5,
                    borderRadius: 2,
                    backgroundColor: 'rgba(34, 197, 94, 0.08)',
                    border: '1px solid rgba(34, 197, 94, 0.2)',
                    minHeight: 40,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <PropositionDisplay text={prop2} size="large" />
                </Box>
              )}
            </Box>
          </Box>

          {/* Options Row */}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Método de Prova</InputLabel>
              <Select
                value={method}
                label="Método de Prova"
                onChange={(e) => setMethod(e.target.value as ProveRequest['method'])}
              >
                {PROOF_METHODS.map((m) => (
                  <MenuItem key={m.value} value={m.value}>
                    {m.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Máx. Iterações</InputLabel>
              <Select
                value={maxIterations}
                label="Máx. Iterações"
                onChange={(e) => setMaxIterations(Number(e.target.value))}
              >
                {MAX_ITERATIONS_OPTIONS.map((n) => (
                  <MenuItem key={n} value={n}>{n}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Checkbox
                  checked={allowBidirectional}
                  onChange={(e) => setAllowBidirectional(e.target.checked)}
                />
              }
              label="Permitir dupla implicação"
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={showFullSteps}
                  onChange={(e) => setShowFullSteps(e.target.checked)}
                />
              }
              label="Mostrar passos completos"
            />
          </Box>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
            sx={{
              py: 1.5,
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
              },
            }}
          >
            {loading ? 'Processando...' : 'Provar Equivalência'}
          </Button>
        </Box>
      </form>
    </Paper>
  );
}

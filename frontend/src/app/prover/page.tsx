'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Collapse,
  Alert,
  IconButton,
} from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { DashboardLayout } from '@/components/layout';
import ProverForm from '@/components/prover/ProverForm';
import ProverResults from '@/components/prover/ProverResults';
import { ProveResponse, proverService } from '@/services/api';

export default function ProverPage() {
  const [result, setResult] = useState<ProveResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [showSyntax, setShowSyntax] = useState(false);
  const [apiStatus, setApiStatus] = useState<'loading' | 'online' | 'offline'>('loading');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        await proverService.getStatus();
        setApiStatus('online');
      } catch {
        setApiStatus('offline');
      }
    };
    checkStatus();
  }, []);

  return (
    <DashboardLayout title="Provar Equivalencias">
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        {/* Status */}
        <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
          <Chip
            label={apiStatus === 'online' ? 'API Online' : apiStatus === 'offline' ? 'API Offline' : 'Verificando...'}
            color={apiStatus === 'online' ? 'success' : apiStatus === 'offline' ? 'error' : 'default'}
            size="small"
          />
          <Chip label="Guiado por NN" color="primary" size="small" variant="outlined" />
        </Box>

        {/* API Offline Warning */}
        {apiStatus === 'offline' && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            A API esta offline. Certifique-se de que o backend esta rodando.
          </Alert>
        )}

        {/* Syntax Help */}
        <Paper sx={{ mb: 3, p: 2 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
            }}
            onClick={() => setShowSyntax(!showSyntax)}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <InfoOutlinedIcon color="primary" />
              <Typography variant="subtitle1" fontWeight={500}>
                Guia de Sintaxe
              </Typography>
            </Box>
            <IconButton size="small">
              {showSyntax ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
          <Collapse in={showSyntax}>
            <Box
              sx={{
                mt: 2,
                display: 'grid',
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
                gap: 2,
              }}
            >
              <Box>
                <Typography variant="subtitle2" color="primary" gutterBottom>
                  Operadores
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Negacao:</strong> ~p, !p, NOT p<br />
                  <strong>Conjuncao (E):</strong> p ^ q, p & q<br />
                  <strong>Disjuncao (OU):</strong> p v q, p | q<br />
                  <strong>Implicacao:</strong> p -{'>'} q, p ={'>'} q
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="primary" gutterBottom>
                  Constantes
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Verdadeiro:</strong> T<br />
                  <strong>Falso:</strong> F
                </Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="primary" gutterBottom>
                  Exemplos
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                  p ^ q<br />
                  ~(p v q)<br />
                  p -{'>'} q<br />
                  (p ^ q) v r
                </Typography>
              </Box>
            </Box>
          </Collapse>
        </Paper>

        {/* Prover Form */}
        <Box sx={{ mb: 4 }}>
          <ProverForm onResult={setResult} onLoading={setLoading} />
        </Box>

        {/* Results */}
        <ProverResults result={result} loading={loading} />
      </Box>
    </DashboardLayout>
  );
}

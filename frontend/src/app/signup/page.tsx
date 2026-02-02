'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Lock as LockIcon,
  Badge as BadgeIcon,
  Key as KeyIcon,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { useAuth } from '@/contexts/AuthContext';
import { SignupRequest } from '@/services/auth';

export default function SignupPage() {
  const router = useRouter();
  const { isAuthenticated, signup } = useAuth();

  const [formData, setFormData] = useState<SignupRequest>({
    name: '',
    email: '',
    password: '',
    confirm_password: '',
    registration_number: '',
    access_code: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  const handleChange = (field: keyof SignupRequest) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: e.target.value,
    }));
    // Clear field error when user starts typing
    if (fieldErrors[field]) {
      setFieldErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setFieldErrors({});
    setIsLoading(true);

    const result = await signup(formData);

    if (result.success) {
      router.push('/');
    } else {
      if (result.fieldErrors) {
        setFieldErrors(result.fieldErrors);
      }
      setError(result.message || 'Erro ao fazer cadastro');
    }

    setIsLoading(false);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)',
        padding: 2,
      }}
    >
      <Card
        sx={{
          maxWidth: 450,
          width: '100%',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography
              variant="h4"
              component="h1"
              sx={{
                fontWeight: 700,
                color: 'primary.main',
                mb: 1,
              }}
            >
              PyLogic
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Crie sua conta para acessar a plataforma
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Nome completo"
              type="text"
              value={formData.name}
              onChange={handleChange('name')}
              required
              disabled={isLoading}
              error={!!fieldErrors.name}
              helperText={fieldErrors.name}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <PersonIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Email"
              type="email"
              value={formData.email}
              onChange={handleChange('email')}
              required
              disabled={isLoading}
              error={!!fieldErrors.email}
              helperText={fieldErrors.email}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <EmailIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Matricula (opcional)"
              type="text"
              value={formData.registration_number}
              onChange={handleChange('registration_number')}
              disabled={isLoading}
              error={!!fieldErrors.registration_number}
              helperText={fieldErrors.registration_number}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <BadgeIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Codigo de acesso da turma"
              type="text"
              value={formData.access_code}
              onChange={handleChange('access_code')}
              required
              disabled={isLoading}
              error={!!fieldErrors.access_code}
              helperText={fieldErrors.access_code}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <KeyIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Senha"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleChange('password')}
              required
              disabled={isLoading}
              error={!!fieldErrors.password}
              helperText={fieldErrors.password || 'Minimo 6 caracteres'}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      disabled={isLoading}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Confirmar senha"
              type={showConfirmPassword ? 'text' : 'password'}
              value={formData.confirm_password}
              onChange={handleChange('confirm_password')}
              required
              disabled={isLoading}
              error={!!fieldErrors.confirm_password}
              helperText={fieldErrors.confirm_password}
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      edge="end"
                      disabled={isLoading}
                    >
                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isLoading}
              sx={{
                py: 1.5,
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 600,
              }}
            >
              {isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Criar conta'
              )}
            </Button>
          </Box>

          <Divider sx={{ my: 3 }}>
            <Typography variant="body2" color="text.secondary">
              ou
            </Typography>
          </Divider>

          <Button
            component={Link}
            href="/login"
            fullWidth
            variant="outlined"
            size="large"
            sx={{
              py: 1.5,
              textTransform: 'none',
              fontSize: '1rem',
            }}
          >
            Ja tenho uma conta
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
}

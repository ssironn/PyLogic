'use client';

import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Divider,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Badge as BadgeIcon,
  Lock as LockIcon,
  Visibility,
  VisibilityOff,
  Save as SaveIcon,
} from '@mui/icons-material';
import { DashboardLayout } from '@/components/layout';
import profileService, { ProfileData } from '@/services/profile';

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Profile form
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);

  // Password form
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setIsLoading(true);
      const response = await profileService.get();

      if (response.status === 'success' && response.data) {
        setProfile(response.data);
        setName(response.data.name);
        setEmail(response.data.email);
      } else {
        setError(response.message || 'Erro ao carregar perfil');
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erro ao conectar com o servidor');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileError(null);
    setProfileSuccess(null);
    setProfileSaving(true);

    try {
      const response = await profileService.update({ name, email });

      if (response.status === 'success') {
        setProfileSuccess('Perfil atualizado com sucesso');
        if (response.data) {
          setProfile(response.data);
        }
      } else {
        setProfileError(response.message || 'Erro ao atualizar perfil');
      }
    } catch (err: any) {
      setProfileError(err.response?.data?.message || 'Erro ao atualizar perfil');
    } finally {
      setProfileSaving(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(null);

    if (newPassword !== confirmPassword) {
      setPasswordError('As senhas nao conferem');
      return;
    }

    if (newPassword.length < 6) {
      setPasswordError('A nova senha deve ter pelo menos 6 caracteres');
      return;
    }

    setPasswordSaving(true);

    try {
      const response = await profileService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      if (response.status === 'success') {
        setPasswordSuccess('Senha alterada com sucesso');
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
      } else {
        setPasswordError(response.message || 'Erro ao alterar senha');
      }
    } catch (err: any) {
      setPasswordError(err.response?.data?.message || 'Erro ao alterar senha');
    } finally {
      setPasswordSaving(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <DashboardLayout title="Meu Perfil">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout title="Meu Perfil">
        <Alert severity="error">{error}</Alert>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Meu Perfil">
      <Box sx={{ maxWidth: 800, mx: 'auto' }}>
        <Grid container spacing={3}>
          {/* Profile Info Card */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                  Informacoes Pessoais
                </Typography>

                {profileSuccess && (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    {profileSuccess}
                  </Alert>
                )}
                {profileError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {profileError}
                  </Alert>
                )}

                <Box component="form" onSubmit={handleProfileSubmit}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Nome"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                        disabled={profileSaving}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <PersonIcon color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        disabled={profileSaving}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <EmailIcon color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Matricula"
                        value={profile?.registration_number || '-'}
                        disabled
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <BadgeIcon color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Ultimo Acesso"
                        value={formatDate(profile?.last_access || null)}
                        disabled
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Button
                        type="submit"
                        variant="contained"
                        startIcon={profileSaving ? <CircularProgress size={20} /> : <SaveIcon />}
                        disabled={profileSaving}
                      >
                        Salvar Alteracoes
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Change Password Card */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                  Alterar Senha
                </Typography>

                {passwordSuccess && (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    {passwordSuccess}
                  </Alert>
                )}
                {passwordError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {passwordError}
                  </Alert>
                )}

                <Box component="form" onSubmit={handlePasswordSubmit}>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Senha Atual"
                        type={showCurrentPassword ? 'text' : 'password'}
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        required
                        disabled={passwordSaving}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <LockIcon color="action" />
                            </InputAdornment>
                          ),
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                                edge="end"
                              >
                                {showCurrentPassword ? <VisibilityOff /> : <Visibility />}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Nova Senha"
                        type={showNewPassword ? 'text' : 'password'}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        required
                        disabled={passwordSaving}
                        helperText="Minimo de 6 caracteres"
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <LockIcon color="action" />
                            </InputAdornment>
                          ),
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => setShowNewPassword(!showNewPassword)}
                                edge="end"
                              >
                                {showNewPassword ? <VisibilityOff /> : <Visibility />}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Confirmar Nova Senha"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        disabled={passwordSaving}
                        error={confirmPassword !== '' && newPassword !== confirmPassword}
                        helperText={
                          confirmPassword !== '' && newPassword !== confirmPassword
                            ? 'As senhas nao conferem'
                            : ''
                        }
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <LockIcon color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Button
                        type="submit"
                        variant="contained"
                        color="warning"
                        startIcon={passwordSaving ? <CircularProgress size={20} /> : <LockIcon />}
                        disabled={passwordSaving}
                      >
                        Alterar Senha
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </DashboardLayout>
  );
}

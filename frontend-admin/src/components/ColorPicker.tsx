'use client';

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Popover,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Palette as PaletteIcon } from '@mui/icons-material';

interface ColorPickerProps {
  label: string;
  value: string;
  onChange: (color: string) => void;
}

const PRESET_COLORS = [
  '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
  '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
  '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
  '#ec4899', '#f43f5e', '#78716c', '#64748b', '#000000',
];

export default function ColorPicker({ label, value, onChange }: ColorPickerProps) {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleColorChange = (color: string) => {
    onChange(color);
  };

  const open = Boolean(anchorEl);

  return (
    <>
      <TextField
        fullWidth
        label={label}
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        margin="normal"
        placeholder="#6366f1"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Box
                sx={{
                  width: 24,
                  height: 24,
                  borderRadius: 1,
                  bgcolor: value || '#cccccc',
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton onClick={handleClick} edge="end" size="small">
                <PaletteIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
      >
        <Box sx={{ p: 2, width: 240 }}>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(5, 1fr)',
              gap: 1,
              mb: 2,
            }}
          >
            {PRESET_COLORS.map((color) => (
              <Box
                key={color}
                onClick={() => {
                  handleColorChange(color);
                  handleClose();
                }}
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: 1,
                  bgcolor: color,
                  cursor: 'pointer',
                  border: value === color ? '3px solid' : '1px solid',
                  borderColor: value === color ? 'primary.main' : 'divider',
                  '&:hover': {
                    transform: 'scale(1.1)',
                  },
                  transition: 'transform 0.1s',
                }}
              />
            ))}
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <input
              type="color"
              value={value || '#6366f1'}
              onChange={(e) => handleColorChange(e.target.value)}
              style={{
                width: 48,
                height: 36,
                padding: 0,
                border: 'none',
                borderRadius: 4,
                cursor: 'pointer',
              }}
            />
            <TextField
              size="small"
              value={value || ''}
              onChange={(e) => handleColorChange(e.target.value)}
              placeholder="#6366f1"
              sx={{ flex: 1 }}
            />
          </Box>
        </Box>
      </Popover>
    </>
  );
}

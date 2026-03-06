import React, { useCallback, useEffect } from 'react';
import { Box, Button, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const INTRO_FLAG_KEY = 'showBrandIntroAfterLogin';
const BRAND_INTRO_VIDEO_PATH =
  process.env.REACT_APP_BRAND_INTRO_VIDEO || '/branding/mandirmitra-logo.mp4';
const INTRO_FALLBACK_TIMEOUT_MS = 10000;

function BrandIntro() {
  const navigate = useNavigate();

  const goToDashboard = useCallback(() => {
    sessionStorage.removeItem(INTRO_FLAG_KEY);
    navigate('/dashboard', { replace: true });
  }, [navigate]);

  useEffect(() => {
    const shouldPlayIntro = sessionStorage.getItem(INTRO_FLAG_KEY) === '1';

    if (!shouldPlayIntro) {
      navigate('/dashboard', { replace: true });
      return undefined;
    }

    const fallbackTimer = window.setTimeout(goToDashboard, INTRO_FALLBACK_TIMEOUT_MS);
    return () => window.clearTimeout(fallbackTimer);
  }, [goToDashboard, navigate]);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'black',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        px: 2,
      }}
    >
      <Box
        component="video"
        src={BRAND_INTRO_VIDEO_PATH}
        autoPlay
        muted
        playsInline
        preload="auto"
        onEnded={goToDashboard}
        onError={goToDashboard}
        sx={{
          width: 'min(100%, 720px)',
          maxHeight: '70vh',
          borderRadius: 2,
          bgcolor: 'black',
        }}
      />

      <Typography variant="body2" sx={{ mt: 2, color: 'rgba(255,255,255,0.9)' }}>
        Loading dashboard...
      </Typography>

      <Button
        onClick={goToDashboard}
        variant="outlined"
        sx={{
          mt: 2,
          color: 'white',
          borderColor: 'rgba(255,255,255,0.6)',
          '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.08)' },
        }}
      >
        Skip
      </Button>
    </Box>
  );
}

export default BrandIntro;

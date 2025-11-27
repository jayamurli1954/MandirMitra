import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography } from '@mui/material';

function Splash() {
  const navigate = useNavigate();

  useEffect(() => {
    // Navigate to dashboard after ~30 seconds
    const timer = setTimeout(() => {
      navigate('/dashboard');
    }, 30000); // 30,000 ms = 30 seconds

    return () => clearTimeout(timer);
  }, [navigate]);

  const handleVideoEnded = () => {
    // If video ends earlier, navigate immediately
    navigate('/dashboard');
  };

  return (
    <Box
      sx={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: '#000',
        color: '#fff',
      }}
    >
      <video
        src="/mandirsync-logo.mp4"
        autoPlay
        muted
        playsInline
        onEnded={handleVideoEnded}
        style={{
          maxWidth: '80%',
          maxHeight: '80%',
          objectFit: 'contain',
        }}
      />
    </Box>
  );
}

export default Splash;

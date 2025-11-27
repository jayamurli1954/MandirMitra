import React from 'react';
import { Box, Typography } from '@mui/material';

const Watermark = () => {
  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 10,
        right: 10,
        zIndex: 1000,
        pointerEvents: 'none',
        opacity: 0.3,
      }}
    >
      <Typography
        variant="caption"
        sx={{
          color: '#666',
          fontSize: '0.75rem',
          fontFamily: 'monospace',
        }}
      >
        Developed by MandirSync
      </Typography>
    </Box>
  );
};

export default Watermark;



import React from 'react';
import { Box, Typography, Button, Chip, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

function PanchangRibbon({ data, settings }) {
  const navigate = useNavigate();

  if (!data) {
    return null;
  }

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';
    try {
      const date = new Date(timeString);
      return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return timeString;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) {
      // Fallback to today's date
      const today = new Date();
      return today.toLocaleDateString('en-IN', { 
        weekday: 'short', 
        day: 'numeric', 
        month: 'short',
        year: 'numeric'
      });
    }
    try {
      // Handle different date formats
      let date;
      if (typeof dateString === 'string') {
        // Try parsing ISO format or other formats
        date = new Date(dateString);
        // Check if date is valid
        if (isNaN(date.getTime())) {
          // Invalid date, use today
          date = new Date();
        }
      } else {
        date = new Date(dateString);
      }
      return date.toLocaleDateString('en-IN', { 
        weekday: 'short', 
        day: 'numeric', 
        month: 'short',
        year: 'numeric'
      });
    } catch {
      // Fallback to today's date
      const today = new Date();
      return today.toLocaleDateString('en-IN', { 
        weekday: 'short', 
        day: 'numeric', 
        month: 'short',
        year: 'numeric'
      });
    }
  };

  // Extract key panchang data - handle various response formats
  const tithi = data.tithi || data.tithi_name || data.tithi_name_english || 'N/A';
  const nakshatra = data.nakshatra || data.nakshatra_name || data.nakshatra_name_english || 'N/A';
  const sunrise = data.sunrise ? formatTime(data.sunrise) : (data.sunrise_time || data.sunrise_ist || 'N/A');
  const sunset = data.sunset ? formatTime(data.sunset) : (data.sunset_time || data.sunset_ist || 'N/A');
  
  // Try to get date from various possible fields
  const dateStr = data.date || data.today_date || data.current_date || new Date().toISOString().split('T')[0];
  const date = formatDate(dateStr);

  return (
    <Paper
      elevation={2}
      sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        p: 1.5,
        mb: 3,
        borderRadius: 2,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
        {/* Left: Panchang Info */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', flex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CalendarTodayIcon sx={{ fontSize: 20 }} />
            <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.85rem' }}>
              {date}
            </Typography>
          </Box>
          
          <Chip
            label={`Tithi: ${tithi}`}
            size="small"
            sx={{
              bgcolor: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              fontWeight: 500,
              fontSize: '0.75rem',
              height: 24,
            }}
          />
          
          <Chip
            label={`Nakshatra: ${nakshatra}`}
            size="small"
            sx={{
              bgcolor: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              fontWeight: 500,
              fontSize: '0.75rem',
              height: 24,
            }}
          />
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 1 }}>
            <Typography variant="caption" sx={{ fontSize: '0.75rem', opacity: 0.9 }}>
              ☀️ {sunrise}
            </Typography>
            <Typography variant="caption" sx={{ fontSize: '0.75rem', opacity: 0.9 }}>
              🌙 {sunset}
            </Typography>
          </Box>
        </Box>

        {/* Right: View Full Panchang Button */}
        <Button
          variant="contained"
          size="small"
          onClick={() => navigate('/panchang')}
          sx={{
            bgcolor: 'rgba(255, 255, 255, 0.2)',
            color: 'white',
            '&:hover': {
              bgcolor: 'rgba(255, 255, 255, 0.3)',
            },
            minWidth: 140,
            fontSize: '0.75rem',
            fontWeight: 600,
          }}
          endIcon={<OpenInNewIcon sx={{ fontSize: 16 }} />}
        >
          View Full Panchang
        </Button>
      </Box>
    </Paper>
  );
}

export default PanchangRibbon;


import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Divider,
  Alert,
  Stack,
  Card,
  CardContent,
} from '@mui/material';

/**
 * Modern Panchang Display Component - Compact and Visually Appealing
 * Redesigned for better space utilization and modern aesthetics
 */
function PanchangDisplay({ data, settings, compact = false }) {
  // Default settings
  const defaultSettings = {
    show_tithi: true,
    show_nakshatra: true,
    show_yoga: true,
    show_karana: true,
    show_sun_timings: true,
    show_rahu_kaal: true,
    show_yamaganda: true,
    show_gulika: true,
    show_abhijit_muhurat: true,
    display_mode: 'full',
    primary_language: 'English',
    show_on_dashboard: true,
  };

  const displaySettings = settings || defaultSettings;

  if (!data) {
    return (
      <Paper sx={{ p: 2, bgcolor: '#FFF9E6' }}>
        <Typography variant="body2" color="text.secondary">
          Panchang data will be displayed here once connected to panchang service API.
        </Typography>
      </Paper>
    );
  }

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';

    // Handle time-only strings like "06:25:00"
    if (timeString.match(/^\d{2}:\d{2}:\d{2}$/)) {
      const [hours, minutes] = timeString.split(':');
      const hour = parseInt(hours);
      const min = minutes;
      const period = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
      return `${displayHour}:${min} ${period}`;
    }

    const date = new Date(timeString);
    if (isNaN(date.getTime())) return 'N/A';
    return date.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Compact info card component
  const InfoCard = ({ title, value, color = '#1976d2', icon = '' }) => (
    <Paper
      elevation={0}
      sx={{
        p: 1.5,
        border: '1px solid #e0e0e0',
        borderLeft: `4px solid ${color}`,
        height: '100%'
      }}
    >
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
        {icon} {title}
      </Typography>
      <Typography variant="body1" sx={{ fontWeight: 600, color: color }}>
        {value}
      </Typography>
    </Paper>
  );

  // Compact view for dashboard
  if (compact) {
    return (
      <Paper sx={{ p: 2, bgcolor: '#FFF9E6', boxShadow: 2 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#FF9933', mb: 2 }}>
          📅 Today's Panchang
        </Typography>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          {formatDate(data.date?.gregorian?.date)}
        </Typography>

        <Box sx={{ mt: 2 }}>
          {displaySettings.show_tithi && data.panchang?.tithi && (
            <Box sx={{ mb: 1.5 }}>
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                Tithi:
              </Typography>
              <Typography variant="body2">
                {data.panchang.tithi.full_name || data.panchang.tithi.name}
              </Typography>
            </Box>
          )}

          {settings?.show_nakshatra && data.panchang?.nakshatra && (
            <Box sx={{ mb: 1.5 }}>
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                Nakshatra:
              </Typography>
              <Chip
                label={data.panchang.nakshatra.name}
                size="small"
                sx={{ bgcolor: '#E3F2FD', color: '#1565C0', fontWeight: 'bold' }}
              />
            </Box>
          )}

          {settings?.show_sun_timings && data.sun_moon && (
            <Box sx={{ mb: 1.5 }}>
              <Typography variant="body2">
                🌅 {formatTime(data.sun_moon.sunrise)}  🌇 {formatTime(data.sun_moon.sunset)}
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>
    );
  }

  // Full page view - MODERN REDESIGN
  return (
    <Box>
      {/* Compact Header */}
      <Paper sx={{ p: 2, mb: 2, bgcolor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', background: 'linear-gradient(135deg, #FF9933 0%, #FF6B35 100%)' }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item xs={12} md={8}>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#fff', mb: 0.5 }}>
              📅 {formatDate(data.date?.gregorian?.date)}
            </Typography>
            {data.date?.hindu && (
              <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 0.5 }}>
                <Chip
                  label={`Vikram Samvat ${data.date.hindu.samvat_vikram}`}
                  size="small"
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: '#fff', fontWeight: 500 }}
                />
                <Chip
                  label={`${data.date.hindu.month} ${data.date.hindu.paksha} Paksha`}
                  size="small"
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: '#fff', fontWeight: 500 }}
                />
                {data.date.hindu.samvatsara && (
                  <Chip
                    label={`${data.date.hindu.samvatsara.name} (${data.date.hindu.samvatsara.cycle_year}/60)`}
                    size="small"
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: '#fff', fontWeight: 500 }}
                  />
                )}
              </Stack>
            )}
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: { xs: 'left', md: 'right' } }}>
            {data.location && (
              <Typography variant="body1" sx={{ color: '#fff', fontWeight: 500 }}>
                📍 {data.location.city}
              </Typography>
            )}
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={2}>
        {/* Panchang - Five Limbs - Compact 2x3 Grid */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#FF6B35' }}>
              पञ्चाङ्ग - Five Limbs
            </Typography>
            <Grid container spacing={1.5}>
              {/* Tithi */}
              {displaySettings.show_tithi && data.panchang?.tithi && (
                <Grid item xs={12} sm={6}>
                  <InfoCard
                    title="TITHI (तिथि)"
                    value={data.panchang.tithi.full_name || data.panchang.tithi.name}
                    color="#2E7D32"
                    icon="🌙"
                  />
                </Grid>
              )}

              {/* Nakshatra */}
              {displaySettings.show_nakshatra && data.panchang?.nakshatra && (
                <Grid item xs={12} sm={6}>
                  <InfoCard
                    title="NAKSHATRA (नक्षत्र)"
                    value={`${data.panchang.nakshatra.name} (Pada ${data.panchang.nakshatra.pada || 1})`}
                    color="#1565C0"
                    icon="⭐"
                  />
                </Grid>
              )}

              {/* Yoga */}
              {displaySettings.show_yoga && data.panchang?.yoga && (
                <Grid item xs={12} sm={6}>
                  <InfoCard
                    title="YOGA (योग)"
                    value={data.panchang.yoga.name}
                    color={data.panchang.yoga.is_inauspicious ? "#D32F2F" : "#7B1FA2"}
                    icon="🔗"
                  />
                </Grid>
              )}

              {/* Karana */}
              {displaySettings.show_karana && data.panchang?.karana && (
                <Grid item xs={12} sm={6}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 1.5,
                      border: '1px solid #e0e0e0',
                      borderLeft: '4px solid #F57C00',
                      height: '100%'
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                      ⚡ KARANA (करण)
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#F57C00' }}>
                      {data.panchang.karana.first_half?.name} | {data.panchang.karana.second_half?.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      1st Half | 2nd Half
                    </Typography>
                  </Paper>
                </Grid>
              )}

              {/* Vara */}
              {data.panchang?.vara && (
                <Grid item xs={12} sm={6}>
                  <InfoCard
                    title="VARA (वार)"
                    value={`${data.panchang.vara.name} (${data.panchang.vara.sanskrit})`}
                    color="#00796B"
                    icon="📆"
                  />
                </Grid>
              )}

              {/* Moon Sign */}
              {data.moon_sign && (
                <Grid item xs={12} sm={6}>
                  <InfoCard
                    title="MOON SIGN (राशि)"
                    value={data.moon_sign.name}
                    color="#9C27B0"
                    icon="🌙"
                  />
                </Grid>
              )}
            </Grid>
          </Paper>
        </Grid>

        {/* Sun & Moon Times - Compact */}
        <Grid item xs={12} md={4}>
          <Stack spacing={2}>
            {/* Sunrise/Sunset */}
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5, color: '#FF6B35' }}>
                ☀️ Sun & Moon
              </Typography>
              <Stack spacing={1}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">🌅 Sunrise</Typography>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    {formatTime(data.sun_moon?.sunrise)}
                  </Typography>
                </Box>
                <Divider />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">🌇 Sunset</Typography>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    {formatTime(data.sun_moon?.sunset)}
                  </Typography>
                </Box>
              </Stack>
            </Paper>

            {/* Ayana & Ruthu */}
            {(data.ayana || data.ruthu) && (
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5, color: '#FF6B35' }}>
                  🌍 Season & Ayana
                </Typography>
                <Stack spacing={1}>
                  {data.ayana && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Ayana</Typography>
                      <Chip label={data.ayana} size="small" sx={{ bgcolor: '#E3F2FD', color: '#1565C0' }} />
                    </Box>
                  )}
                  {data.ruthu && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Ruthu</Typography>
                      <Chip label={data.ruthu} size="small" sx={{ bgcolor: '#E8F5E9', color: '#2E7D32' }} />
                    </Box>
                  )}
                </Stack>
              </Paper>
            )}
          </Stack>
        </Grid>

        {/* Auspicious Times */}
        {displaySettings.show_abhijit_muhurat && data.auspicious_times?.abhijit_muhurat && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: '#E8F5E9', border: '2px solid #4CAF50' }}>
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#2E7D32', mb: 1.5 }}>
                ✅ Auspicious Timings
              </Typography>
              <Box sx={{ bgcolor: '#fff', p: 1.5, borderRadius: 1, mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    🌟 Abhijit Muhurat
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 700, color: '#2E7D32' }}>
                    {formatTime(data.auspicious_times.abhijit_muhurat.start)} - {formatTime(data.auspicious_times.abhijit_muhurat.end)}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Duration: {data.auspicious_times.abhijit_muhurat.duration_minutes} mins
                </Typography>
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Inauspicious Times */}
        {data.inauspicious_times && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: '#FFEBEE', border: '2px solid #F44336' }}>
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#C62828', mb: 1.5 }}>
                ⚠️ Inauspicious Timings
              </Typography>
              <Stack spacing={1}>
                {displaySettings.show_rahu_kaal && data.inauspicious_times.rahu_kaal && (
                  <Box sx={{ bgcolor: '#fff', p: 1.5, borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        🔴 Rahu Kala
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 700, color: '#C62828' }}>
                        {formatTime(data.inauspicious_times.rahu_kaal.start)} - {formatTime(data.inauspicious_times.rahu_kaal.end)}
                      </Typography>
                    </Box>
                  </Box>
                )}
                {displaySettings.show_yamaganda && data.inauspicious_times.yamaganda && (
                  <Box sx={{ bgcolor: '#fff', p: 1.5, borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        ⚫ Yamaganda Kala
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 700, color: '#C62828' }}>
                        {formatTime(data.inauspicious_times.yamaganda.start)} - {formatTime(data.inauspicious_times.yamaganda.end)}
                      </Typography>
                    </Box>
                  </Box>
                )}
                {displaySettings.show_gulika && data.inauspicious_times.gulika && (
                  <Box sx={{ bgcolor: '#fff', p: 1.5, borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        🟤 Gulika Kala
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 700, color: '#C62828' }}>
                        {formatTime(data.inauspicious_times.gulika.start)} - {formatTime(data.inauspicious_times.gulika.end)}
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Stack>
            </Paper>
          </Grid>
        )}

        {/* Special Days / Festivals */}
        {data.festivals && data.festivals.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2, bgcolor: '#FFF3E0', border: '2px solid #FF9800' }}>
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#E65100', mb: 1.5 }}>
                🎉 Today's Significance
              </Typography>
              <Grid container spacing={1}>
                {data.festivals.map((festival, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Box sx={{ bgcolor: '#fff', p: 1.5, borderRadius: 1, borderLeft: '4px solid #FF9800' }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, color: '#E65100', mb: 0.5 }}>
                        {festival.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {festival.description}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default PanchangDisplay;

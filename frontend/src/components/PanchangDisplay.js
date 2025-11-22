import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Chip,
  Divider,
  Alert,
} from '@mui/material';

/**
 * Panchang Display Component
 * Based on Panchang_Display_Guide.md specifications
 *
 * Displays:
 * - Essential: Date, Tithi, Nakshatra, Yoga, Karana, Sun timings, Rahu Kaal, Abhijit Muhurat
 * - Color coding: Green (auspicious), Red (inauspicious), Blue (info)
 */
function PanchangDisplay({ data, settings, compact = false }) {
  // Default settings if not provided - show all essential fields
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

  // Use provided settings or fallback to defaults
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
    const date = new Date(timeString);
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
                {data.panchang.tithi.end_time && ` → ${formatTime(data.panchang.tithi.end_time)}`}
              </Typography>
            </Box>
          )}

          {settings?.show_nakshatra && data.panchang?.nakshatra && (
            <Box sx={{ mb: 1.5 }}>
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                Nakshatra:
              </Typography>
              <Chip 
                label={`${data.panchang.nakshatra.name} ${data.panchang.nakshatra.quality === 'very_auspicious' ? '⭐⭐' : data.panchang.nakshatra.quality === 'auspicious' ? '⭐' : ''}`}
                size="small" 
                sx={{ 
                  bgcolor: data.panchang.nakshatra.quality === 'very_auspicious' ? '#E8F5E9' : '#E3F2FD',
                  color: data.panchang.nakshatra.quality === 'very_auspicious' ? '#2E7D32' : '#1565C0',
                  fontWeight: 'bold'
                }}
              />
              {data.panchang.nakshatra.end_time && (
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  Until: {formatTime(data.panchang.nakshatra.end_time)}
                </Typography>
              )}
            </Box>
          )}

          {settings?.show_yoga && data.panchang?.yoga && (
            <Box sx={{ mb: 1.5 }}>
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                Yoga:
              </Typography>
              <Chip 
                label={`${data.panchang.yoga.name} ${data.panchang.yoga.nature === 'auspicious' ? '✅' : '⚠️'}`}
                size="small"
                sx={{
                  bgcolor: data.panchang.yoga.nature === 'auspicious' ? '#E8F5E9' : '#FFF3E0',
                  color: data.panchang.yoga.nature === 'auspicious' ? '#2E7D32' : '#E65100'
                }}
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

          {settings?.show_rahu_kaal && data.inauspicious_times?.rahu_kaal && (
            <Box sx={{ mt: 1.5, p: 1.5, bgcolor: '#FFEBEE', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#C62828' }}>
                ⚠️ Rahu Kaal
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatTime(data.inauspicious_times.rahu_kaal.start)} - {formatTime(data.inauspicious_times.rahu_kaal.end)}
              </Typography>
            </Box>
          )}

          {settings?.show_abhijit_muhurat && data.auspicious_times?.abhijit_muhurat && (
            <Box sx={{ mt: 1.5, p: 1.5, bgcolor: '#E8F5E9', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#2E7D32' }}>
                ✅ Abhijit Muhurat
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatTime(data.auspicious_times.abhijit_muhurat.start)} - {formatTime(data.auspicious_times.abhijit_muhurat.end)}
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>
    );
  }

  // Full page view
  return (
    <Box>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: '#FFF9E6', textAlign: 'center' }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
          🕉️ Today's Panchang
        </Typography>
        <Typography variant="h6" color="text.secondary">
          {formatDate(data.date?.gregorian?.date)}
        </Typography>
        {data.date?.hindu && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Vikram Samvat {data.date.hindu.samvat_vikram} | {data.date.hindu.month} {data.date.hindu.paksha} Paksha
          </Typography>
        )}
      </Paper>

      <Grid container spacing={3}>
        {/* The Five Limbs (Panch-Anga) */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
              The Five Limbs (Panch-Anga)
            </Typography>
            
            <Grid container spacing={2}>
              {/* Tithi */}
              {settings?.show_tithi && data.panchang?.tithi && (
                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                      1. TITHI (तिथि)
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      {data.panchang.tithi.full_name || data.panchang.tithi.name}
                    </Typography>
                    {data.panchang.tithi.end_time && (
                      <Typography variant="body2" color="text.secondary">
                        Until: {formatTime(data.panchang.tithi.end_time)}
                      </Typography>
                    )}
                    {data.panchang.tithi.next_tithi && (
                      <Typography variant="body2" color="text.secondary">
                        Then: {data.panchang.tithi.next_tithi}
                      </Typography>
                    )}
                    {data.panchang.tithi.is_special && (
                      <Chip 
                        label={data.panchang.tithi.special_type || 'Special'}
                        size="small"
                        sx={{ mt: 1, bgcolor: '#E3F2FD' }}
                      />
                    )}
                  </Box>
                </Grid>
              )}

              {/* Nakshatra */}
              {settings?.show_nakshatra && data.panchang?.nakshatra && (
                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                      2. NAKSHATRA (नक्षत्र)
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      {data.panchang.nakshatra.name}
                      {data.panchang.nakshatra.quality === 'very_auspicious' && ' ⭐⭐'}
                      {data.panchang.nakshatra.quality === 'auspicious' && ' ⭐'}
                    </Typography>
                    {data.panchang.nakshatra.pada && (
                      <Typography variant="body2" color="text.secondary">
                        Pada: {data.panchang.nakshatra.pada}
                      </Typography>
                    )}
                    {data.panchang.nakshatra.deity && (
                      <Typography variant="body2" color="text.secondary">
                        Deity: {data.panchang.nakshatra.deity}
                      </Typography>
                    )}
                    {data.panchang.nakshatra.end_time && (
                      <Typography variant="body2" color="text.secondary">
                        Until: {formatTime(data.panchang.nakshatra.end_time)}
                      </Typography>
                    )}
                    <Chip 
                      label={data.panchang.nakshatra.quality === 'very_auspicious' ? 'Very Auspicious' : 
                             data.panchang.nakshatra.quality === 'auspicious' ? 'Auspicious' : 'Mixed'}
                      size="small"
                      sx={{ 
                        mt: 1,
                        bgcolor: data.panchang.nakshatra.quality === 'very_auspicious' ? '#E8F5E9' : '#E3F2FD',
                        color: data.panchang.nakshatra.quality === 'very_auspicious' ? '#2E7D32' : '#1565C0'
                      }}
                    />
                  </Box>
                </Grid>
              )}

              {/* Yoga */}
              {settings?.show_yoga && data.panchang?.yoga && (
                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                      3. YOGA (योग)
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      {data.panchang.yoga.name}
                    </Typography>
                    <Chip 
                      label={data.panchang.yoga.nature === 'auspicious' ? '✅ Auspicious' : '⚠️ Inauspicious'}
                      size="small"
                      sx={{
                        bgcolor: data.panchang.yoga.nature === 'auspicious' ? '#E8F5E9' : '#FFEBEE',
                        color: data.panchang.yoga.nature === 'auspicious' ? '#2E7D32' : '#C62828'
                      }}
                    />
                    {data.panchang.yoga.end_time && (
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Until: {formatTime(data.panchang.yoga.end_time)}
                      </Typography>
                    )}
                    {data.panchang.yoga.is_bad_yoga && (
                      <Alert severity="warning" sx={{ mt: 1 }}>
                        ⚠️ Avoid all activities during this yoga
                      </Alert>
                    )}
                  </Box>
                </Grid>
              )}

              {/* Karana */}
              {settings?.show_karana && data.panchang?.karana && (
                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                      4. KARANA (करण)
                    </Typography>
                    {data.panchang.karana.first_half && (
                      <Typography variant="body1" sx={{ mb: 1 }}>
                        First Half: {data.panchang.karana.first_half.name}
                        {data.panchang.karana.first_half.end_time && ` (until ${formatTime(data.panchang.karana.first_half.end_time)})`}
                      </Typography>
                    )}
                    {data.panchang.karana.second_half && (
                      <Typography variant="body1">
                        Second Half: {data.panchang.karana.second_half.name}
                        {data.panchang.karana.second_half.end_time && ` (until ${formatTime(data.panchang.karana.second_half.end_time)})`}
                      </Typography>
                    )}
                    {data.panchang.karana.is_bhadra && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        ⚠️ BHADRA (Vishti) - Avoid starting new activities
                      </Alert>
                    )}
                  </Box>
                </Grid>
              )}

              {/* Vara */}
              {data.panchang?.vara && (
                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                      5. VARA (वार)
                    </Typography>
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      {data.panchang.vara.name} ({data.panchang.vara.sanskrit})
                    </Typography>
                    {data.panchang.vara.ruling_planet && (
                      <Typography variant="body2" color="text.secondary">
                        Ruling Planet: {data.panchang.vara.ruling_planet}
                      </Typography>
                    )}
                    {data.panchang.vara.deity && (
                      <Typography variant="body2" color="text.secondary">
                        Deity: {data.panchang.vara.deity}
                      </Typography>
                    )}
                  </Box>
                </Grid>
              )}
            </Grid>
          </Paper>
        </Grid>

        {/* Sun & Moon Timings */}
        {settings?.show_sun_timings && data.sun_moon && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Sun & Moon
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  🌅 Sunrise: {formatTime(data.sun_moon.sunrise)}
                </Typography>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  🌇 Sunset: {formatTime(data.sun_moon.sunset)}
                </Typography>
                {data.sun_moon.moonrise && (
                  <Typography variant="body1" sx={{ mb: 1 }}>
                    🌙 Moonrise: {formatTime(data.sun_moon.moonrise)}
                  </Typography>
                )}
                {data.sun_moon.moonset && (
                  <Typography variant="body1">
                    🌙 Moonset: {formatTime(data.sun_moon.moonset)}
                  </Typography>
                )}
                {data.auspicious_times?.brahma_muhurat && (
                  <Box sx={{ mt: 2, p: 1.5, bgcolor: '#E3F2FD', borderRadius: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      🌄 Brahma Muhurat
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {formatTime(data.auspicious_times.brahma_muhurat.start)} - {formatTime(data.auspicious_times.brahma_muhurat.end)}
                    </Typography>
                  </Box>
                )}
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Inauspicious Times */}
        {(settings?.show_rahu_kaal || settings?.show_yamaganda || settings?.show_gulika) && data.inauspicious_times && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, bgcolor: '#FFEBEE' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#C62828' }}>
                ⚠️ Inauspicious Times - AVOID
              </Typography>
              <Box sx={{ mt: 2 }}>
                {settings?.show_rahu_kaal && data.inauspicious_times.rahu_kaal && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Rahu Kaal (राहु काल)
                    </Typography>
                    <Typography variant="body1">
                      {formatTime(data.inauspicious_times.rahu_kaal.start)} - {formatTime(data.inauspicious_times.rahu_kaal.end)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      Duration: {data.inauspicious_times.rahu_kaal.duration_minutes} minutes
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontStyle: 'italic' }}>
                      ❌ Avoid: Starting new work, important meetings, travel, financial transactions
                    </Typography>
                  </Box>
                )}
                {settings?.show_yamaganda && data.inauspicious_times.yamaganda && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Yamaganda (यमगण्ड)
                    </Typography>
                    <Typography variant="body1">
                      {formatTime(data.inauspicious_times.yamaganda.start)} - {formatTime(data.inauspicious_times.yamaganda.end)}
                    </Typography>
                  </Box>
                )}
                {settings?.show_gulika && data.inauspicious_times.gulika && (
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Gulika (गुलिक)
                    </Typography>
                    <Typography variant="body1">
                      {formatTime(data.inauspicious_times.gulika.start)} - {formatTime(data.inauspicious_times.gulika.end)}
                    </Typography>
                  </Box>
                )}
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Auspicious Times */}
        {settings?.show_abhijit_muhurat && data.auspicious_times?.abhijit_muhurat && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, bgcolor: '#E8F5E9' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#2E7D32' }}>
                ✅ Auspicious Times - BEST FOR ACTIVITIES
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Abhijit Muhurat (अभिजित मुहूर्त)
                </Typography>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  {formatTime(data.auspicious_times.abhijit_muhurat.start)} - {formatTime(data.auspicious_times.abhijit_muhurat.end)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Duration: {data.auspicious_times.abhijit_muhurat.duration_minutes} minutes
                </Typography>
                <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                  ✅ Most auspicious time of the day - Good for all activities
                </Typography>
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Festivals */}
        {data.festivals && data.festivals.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3, bgcolor: '#FFF3E0' }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                🎉 Today's Significance
              </Typography>
              {data.festivals.map((festival, index) => (
                <Box key={index} sx={{ mt: 1 }}>
                  <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                    • {festival.name}
                  </Typography>
                  {festival.description && (
                    <Typography variant="body2" color="text.secondary">
                      {festival.description}
                    </Typography>
                  )}
                </Box>
              ))}
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default PanchangDisplay;


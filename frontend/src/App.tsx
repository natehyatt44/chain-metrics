import React, { useEffect, useState } from 'react';
import { Container, Grid, Paper, Typography } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { MetricsState } from './types/metrics';
import { fetchHederaTxCount, fetchHederaUSDC, fetchGreedFearIndex } from './services/api';

const App: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsState>({
    hederaTxCount: [],
    hederaUSDC: [],
    greedFearIndex: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const [txCount, usdc, greedFear] = await Promise.all([
          fetchHederaTxCount(),
          fetchHederaUSDC(),
          fetchGreedFearIndex(),
        ]);

        setMetrics({
          hederaTxCount: txCount,
          hederaUSDC: usdc,
          greedFearIndex: greedFear,
          loading: false,
          error: null,
        });
      } catch (error) {
        setMetrics(prev => ({
          ...prev,
          loading: false,
          error: 'Failed to fetch metrics data',
        }));
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000); // Refresh every minute

    return () => clearInterval(interval);
  }, []);

  if (metrics.loading) {
    return <Typography>Loading...</Typography>;
  }

  if (metrics.error) {
    return <Typography color="error">{metrics.error}</Typography>;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h4" gutterBottom>
              Hedera Transaction Count
            </Typography>
            <LineChart width={800} height={300} data={metrics.hederaTxCount}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" />
            </LineChart>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h4" gutterBottom>
              USDC Minted on Hedera
            </Typography>
            <LineChart width={800} height={300} data={metrics.hederaUSDC}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#82ca9d" />
            </LineChart>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h4" gutterBottom>
              Crypto Greed/Fear Index
            </Typography>
            <LineChart width={800} height={300} data={metrics.greedFearIndex}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#ff7300" />
            </LineChart>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default App; 
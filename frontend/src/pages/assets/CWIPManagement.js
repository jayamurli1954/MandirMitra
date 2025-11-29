import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  MenuItem,
  Alert,
  CircularProgress,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ConstructionIcon from '@mui/icons-material/Construction';
import SaveIcon from '@mui/icons-material/Save';
import Layout from '../../components/Layout';
import api from '../../services/api';

const CWIPManagement = () => {
  const [projects, setProjects] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [projectDialogOpen, setProjectDialogOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [expenseDialogOpen, setExpenseDialogOpen] = useState(false);

  const [projectForm, setProjectForm] = useState({
    cwip_number: '',
    project_name: '',
    description: '',
    asset_category_id: '',
    start_date: new Date().toISOString().split('T')[0],
    expected_completion_date: '',
    total_budget: 0,
  });

  const [expenseForm, setExpenseForm] = useState({
    expense_date: new Date().toISOString().split('T')[0],
    description: '',
    amount: 0,
    expense_category: 'MATERIAL',
    vendor_id: '',
    reference_number: '',
  });

  const [expenses, setExpenses] = useState([]);
  const [loadingExpenses, setLoadingExpenses] = useState(false);

  useEffect(() => {
    fetchCategories();
    fetchProjects();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/api/v1/assets/categories/');
      setCategories(response.data || []);
    } catch (err) {
      console.error('Failed to load asset categories', err);
    }
  };

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/assets/cwip/');
      setProjects(response.data || []);
    } catch (err) {
      setError(err.userMessage || 'Failed to load CWIP projects');
    } finally {
      setLoading(false);
    }
  };

  const openNewProjectDialog = () => {
    setSelectedProject(null);
    setProjectForm({
      cwip_number: '',
      project_name: '',
      description: '',
      asset_category_id: '',
      start_date: new Date().toISOString().split('T')[0],
      expected_completion_date: '',
      total_budget: 0,
    });
    setProjectDialogOpen(true);
  };

  const handleProjectSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      await api.post('/api/v1/assets/cwip/', {
        ...projectForm,
        total_budget: parseFloat(projectForm.total_budget) || 0,
      });
      setSuccess('CWIP project created successfully');
      setProjectDialogOpen(false);
      fetchProjects();
    } catch (err) {
      setError(err.userMessage || 'Failed to save CWIP project');
    }
  };

  const openExpenseDialog = async (project) => {
    setSelectedProject(project);
    setExpenseForm({
      expense_date: new Date().toISOString().split('T')[0],
      description: '',
      amount: 0,
      expense_category: 'MATERIAL',
      vendor_id: '',
      reference_number: '',
    });
    setExpenseDialogOpen(true);
    await fetchExpenses(project.id);
  };

  const fetchExpenses = async (cwipId) => {
    try {
      setLoadingExpenses(true);
      const response = await api.get(`/api/v1/assets/cwip/${cwipId}/expenses/`);
      setExpenses(response.data || []);
    } catch (err) {
      console.error('Failed to load CWIP expenses', err);
    } finally {
      setLoadingExpenses(false);
    }
  };

  const handleExpenseSubmit = async (e) => {
    e.preventDefault();
    if (!selectedProject) return;
    setError('');
    setSuccess('');

    try {
      await api.post(`/api/v1/assets/cwip/${selectedProject.id}/expenses/`, {
        ...expenseForm,
        amount: parseFloat(expenseForm.amount) || 0,
      });
      setSuccess('Expense added successfully');
      await fetchProjects();
      await fetchExpenses(selectedProject.id);
    } catch (err) {
      setError(err.userMessage || 'Failed to add expense');
    }
  };

  const totalBudget = projects.reduce((sum, p) => sum + (p.total_budget || 0), 0);
  const totalExpenditure = projects.reduce((sum, p) => sum + (p.total_expenditure || 0), 0);

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
            <ConstructionIcon color="primary" />
            CWIP Management
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={openNewProjectDialog}>
            New CWIP Project
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Total Projects
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {projects.length}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Total Budget
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                ₹{new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(totalBudget)}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Total Expenditure
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                ₹{new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(totalExpenditure)}
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        <Paper>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Project No.</strong></TableCell>
                    <TableCell><strong>Project Name</strong></TableCell>
                    <TableCell><strong>Category</strong></TableCell>
                    <TableCell><strong>Start Date</strong></TableCell>
                    <TableCell align="right"><strong>Budget (₹)</strong></TableCell>
                    <TableCell align="right"><strong>Expenditure (₹)</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell align="right"><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {projects.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                        <Typography variant="body2" color="text.secondary">
                          No CWIP projects found. Click "New CWIP Project" to create one.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    projects.map((project) => (
                      <TableRow key={project.id}>
                        <TableCell>{project.cwip_number}</TableCell>
                        <TableCell>{project.project_name}</TableCell>
                        <TableCell>
                          {categories.find(c => c.id === project.asset_category_id)?.name || 'N/A'}
                        </TableCell>
                        <TableCell>
                          {project.start_date ? new Date(project.start_date).toLocaleDateString() : '-'}
                        </TableCell>
                        <TableCell align="right">
                          ₹{new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(project.total_budget || 0)}
                        </TableCell>
                        <TableCell align="right">
                          ₹{new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(project.total_expenditure || 0)}
                        </TableCell>
                        <TableCell>{project.status}</TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => openExpenseDialog(project)}
                          >
                            Expenses
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>

        {/* New Project Dialog */}
        <Dialog open={projectDialogOpen} onClose={() => setProjectDialogOpen(false)} maxWidth="sm" fullWidth>
          <form onSubmit={handleProjectSubmit}>
            <DialogTitle>New CWIP Project</DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Project Number *"
                    value={projectForm.cwip_number}
                    onChange={(e) => setProjectForm({ ...projectForm, cwip_number: e.target.value })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Project Name *"
                    value={projectForm.project_name}
                    onChange={(e) => setProjectForm({ ...projectForm, project_name: e.target.value })}
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    value={projectForm.description}
                    onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
                    multiline
                    rows={2}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Asset Category *"
                    value={projectForm.asset_category_id}
                    onChange={(e) => setProjectForm({ ...projectForm, asset_category_id: e.target.value })}
                    required
                  >
                    {categories.map((cat) => (
                      <MenuItem key={cat.id} value={cat.id}>
                        {cat.name}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="Start Date *"
                    InputLabelProps={{ shrink: true }}
                    value={projectForm.start_date}
                    onChange={(e) => setProjectForm({ ...projectForm, start_date: e.target.value })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="Expected Completion"
                    InputLabelProps={{ shrink: true }}
                    value={projectForm.expected_completion_date}
                    onChange={(e) => setProjectForm({ ...projectForm, expected_completion_date: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Total Budget (₹)"
                    value={projectForm.total_budget}
                    onChange={(e) =>
                      setProjectForm({ ...projectForm, total_budget: e.target.value })
                    }
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setProjectDialogOpen(false)}>Cancel</Button>
              <Button type="submit" variant="contained" startIcon={<SaveIcon />}>
                Save
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* Expense Dialog */}
        <Dialog open={expenseDialogOpen} onClose={() => setExpenseDialogOpen(false)} maxWidth="md" fullWidth>
          <form onSubmit={handleExpenseSubmit}>
            <DialogTitle>
              CWIP Expenses - {selectedProject?.cwip_number} ({selectedProject?.project_name})
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    type="date"
                    label="Expense Date *"
                    InputLabelProps={{ shrink: true }}
                    value={expenseForm.expense_date}
                    onChange={(e) => setExpenseForm({ ...expenseForm, expense_date: e.target.value })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Amount (₹) *"
                    type="number"
                    value={expenseForm.amount}
                    onChange={(e) => setExpenseForm({ ...expenseForm, amount: e.target.value })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    select
                    label="Expense Category"
                    value={expenseForm.expense_category}
                    onChange={(e) =>
                      setExpenseForm({ ...expenseForm, expense_category: e.target.value })
                    }
                  >
                    <MenuItem value="MATERIAL">Material</MenuItem>
                    <MenuItem value="LABOR">Labor</MenuItem>
                    <MenuItem value="OVERHEAD">Overhead</MenuItem>
                    <MenuItem value="OTHER">Other</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description *"
                    value={expenseForm.description}
                    onChange={(e) =>
                      setExpenseForm({ ...expenseForm, description: e.target.value })
                    }
                    multiline
                    rows={2}
                    required
                  />
                </Grid>
              </Grid>

              <Typography variant="subtitle1" sx={{ mb: 1 }}>
                Previous Expenses
              </Typography>
              {loadingExpenses ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : (
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell>Category</TableCell>
                        <TableCell align="right">Amount (₹)</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {expenses.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={4} align="center" sx={{ py: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                              No expenses recorded yet.
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ) : (
                        expenses.map((exp) => (
                          <TableRow key={exp.id}>
                            <TableCell>
                              {exp.expense_date
                                ? new Date(exp.expense_date).toLocaleDateString()
                                : '-'}
                            </TableCell>
                            <TableCell>{exp.description}</TableCell>
                            <TableCell>{exp.expense_category || '-'}</TableCell>
                            <TableCell align="right">
                              ₹{new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(
                                exp.amount || 0
                              )}
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setExpenseDialogOpen(false)}>Close</Button>
              <Button type="submit" variant="contained" startIcon={<SaveIcon />}>
                Add Expense
              </Button>
            </DialogActions>
          </form>
        </Dialog>
      </Box>
    </Layout>
  );
};

export default CWIPManagement;






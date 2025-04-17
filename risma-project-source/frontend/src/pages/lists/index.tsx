import { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Grid, 
  Paper, 
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  Tabs,
  Tab,
  Tooltip,
  Alert
} from '@mui/material';
import { 
  Delete as DeleteIcon,
  Edit as EditIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Add as AddIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';
import { useRouter } from 'next/router';
import api from '../../utils/api';

interface List {
  id: number;
  name: string;
  description: string;
  total_records: number;
  created_at: string;
  updated_at: string;
}

const ListsPage = () => {
  const router = useRouter();
  const [lists, setLists] = useState<List[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedList, setSelectedList] = useState<List | null>(null);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    fetchLists();
  }, []);

  const fetchLists = async () => {
    setLoading(true);
    try {
      const response = await api.lists.getAll();
      setLists(response.data);
    } catch (error) {
      console.error('リストの取得に失敗しました:', error);
      setError('リストの取得に失敗しました。再度お試しください。');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleDeleteClick = (list: List) => {
    setSelectedList(list);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedList) return;
    
    try {
      await api.lists.delete(selectedList.id);
      setLists(lists.filter(list => list.id !== selectedList.id));
      setDeleteDialogOpen(false);
      setSelectedList(null);
    } catch (error) {
      console.error('リストの削除に失敗しました:', error);
      setError('リストの削除に失敗しました。再度お試しください。');
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setSelectedList(null);
  };

  const handleExportCSV = async (listId: number) => {
    try {
      await api.lists.export(listId);
    } catch (error) {
      console.error('CSVエクスポートに失敗しました:', error);
      setError('CSVエクスポートに失敗しました。再度お試しください。');
    }
  };

  return (
    <DashboardLayout title="リスト管理">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4">
            リスト管理
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => router.push('/search/keyword')}
          >
            新規リスト作成
          </Button>
        </Box>
        <Typography variant="body1" color="text.secondary">
          作成したリストの管理、編集、エクスポートを行います。
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mb: 4 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="すべてのリスト" />
          <Tab label="キーワード検索" />
          <Tab label="業種×住所検索" />
        </Tabs>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>リスト名</TableCell>
                <TableCell>説明</TableCell>
                <TableCell align="right">レコード数</TableCell>
                <TableCell>作成日</TableCell>
                <TableCell align="center">操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : lists.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                    <Typography variant="body1" color="text.secondary">
                      リストがありません。新規リストを作成してください。
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                lists.map((list) => (
                  <TableRow key={list.id} hover>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {list.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" noWrap sx={{ maxWidth: 300 }}>
                        {list.description}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip label={list.total_records.toLocaleString()} color="primary" size="small" />
                    </TableCell>
                    <TableCell>
                      {new Date(list.created_at).toLocaleString('ja-JP')}
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                        <Tooltip title="詳細を表示">
                          <IconButton
                            size="small"
                            onClick={() => router.push(`/lists/${list.id}`)}
                          >
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="編集">
                          <IconButton
                            size="small"
                            onClick={() => router.push(`/lists/${list.id}/edit`)}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="CSVエクスポート">
                          <IconButton
                            size="small"
                            onClick={() => handleExportCSV(list.id)}
                          >
                            <DownloadIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="削除">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDeleteClick(list)}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* 削除確認ダイアログ */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
      >
        <DialogTitle>リストの削除</DialogTitle>
        <DialogContent>
          <DialogContentText>
            リスト「{selectedList?.name}」を削除しますか？
            <br />
            この操作は元に戻せません。
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>キャンセル</Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            削除
          </Button>
        </DialogActions>
      </Dialog>
    </DashboardLayout>
  );
};

export default ListsPage;

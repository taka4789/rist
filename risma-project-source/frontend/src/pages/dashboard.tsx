import { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  CardHeader,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import { 
  Search as SearchIcon, 
  LocationOn as LocationIcon, 
  List as ListIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon
} from '@mui/icons-material';
import DashboardLayout from '../components/DashboardLayout';
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';

interface SearchJob {
  id: number;
  job_type: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  result_count: number | null;
  error_message: string | null;
}

interface List {
  id: number;
  name: string;
  description: string;
  total_records: number;
  created_at: string;
}

const Dashboard = () => {
  const router = useRouter();
  const { user } = useAuth();
  const [recentJobs, setRecentJobs] = useState<SearchJob[]>([]);
  const [recentLists, setRecentLists] = useState<List[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // 最近の検索ジョブを取得
        const jobsResponse = await api.search.getJobs(5);
        setRecentJobs(jobsResponse.data);

        // 最近のリストを取得
        const listsResponse = await api.lists.getAll(5);
        setRecentLists(listsResponse.data);
      } catch (error) {
        console.error('Dashboard data fetch error:', error);
        setError('データの取得に失敗しました。再度お試しください。');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'processing':
        return <CircularProgress size={20} />;
      default:
        return <PendingIcon color="warning" />;
    }
  };

  const getJobTypeText = (jobType: string) => {
    switch (jobType) {
      case 'keyword':
        return 'キーワード検索';
      case 'industry_location':
        return '業種×住所検索';
      default:
        return jobType;
    }
  };

  return (
    <DashboardLayout title="ダッシュボード">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          ようこそ、{user?.full_name || 'ユーザー'}さん
        </Typography>
        <Typography variant="body1" color="text.secondary">
          リスマ（LisMa）でBtoB営業リストを効率的に作成しましょう。
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', p: 3 }}>
              <SearchIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom align="center">
                キーワード検索
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2 }}>
                キーワードを指定して企業リストを作成します
              </Typography>
              <Button 
                variant="contained" 
                fullWidth
                onClick={() => router.push('/search/keyword')}
              >
                検索を開始
              </Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', p: 3 }}>
              <LocationIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom align="center">
                業種×住所検索
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2 }}>
                業種と地域を指定して企業リストを作成します
              </Typography>
              <Button 
                variant="contained" 
                fullWidth
                onClick={() => router.push('/search/industry-location')}
              >
                検索を開始
              </Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', p: 3 }}>
              <ListIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom align="center">
                リスト管理
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2 }}>
                作成したリストの管理・編集・エクスポート
              </Typography>
              <Button 
                variant="contained" 
                fullWidth
                onClick={() => router.push('/lists')}
              >
                リストを表示
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="最近の検索ジョブ" />
            <CardContent>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : recentJobs.length > 0 ? (
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>種類</TableCell>
                        <TableCell>ステータス</TableCell>
                        <TableCell>結果数</TableCell>
                        <TableCell>日時</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recentJobs.map((job) => (
                        <TableRow key={job.id} hover onClick={() => router.push(`/search/jobs/${job.id}`)}>
                          <TableCell>{getJobTypeText(job.job_type)}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {getStatusIcon(job.status)}
                              <Typography variant="body2" sx={{ ml: 1 }}>
                                {job.status === 'completed' ? '完了' : 
                                 job.status === 'failed' ? '失敗' : 
                                 job.status === 'processing' ? '処理中' : '待機中'}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{job.result_count || '-'}</TableCell>
                          <TableCell>{new Date(job.created_at).toLocaleString('ja-JP')}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ p: 2 }}>
                  検索ジョブはまだありません
                </Typography>
              )}
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                <Button size="small" onClick={() => router.push('/search/jobs')}>
                  すべて表示
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="最近のリスト" />
            <CardContent>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : recentLists.length > 0 ? (
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>リスト名</TableCell>
                        <TableCell>レコード数</TableCell>
                        <TableCell>作成日</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recentLists.map((list) => (
                        <TableRow key={list.id} hover onClick={() => router.push(`/lists/${list.id}`)}>
                          <TableCell>{list.name}</TableCell>
                          <TableCell>{list.total_records}</TableCell>
                          <TableCell>{new Date(list.created_at).toLocaleString('ja-JP')}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ p: 2 }}>
                  リストはまだありません
                </Typography>
              )}
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                <Button size="small" onClick={() => router.push('/lists')}>
                  すべて表示
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};

export default Dashboard;

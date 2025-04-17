import { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Grid, 
  Paper, 
  Button,
  TextField,
  CircularProgress,
  Alert,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Tabs,
  Tab,
  Card,
  CardContent
} from '@mui/material';
import { 
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  FilterList as FilterListIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';
import { useRouter } from 'next/router';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';

interface ListDetail {
  id: number;
  name: string;
  description: string;
  total_records: number;
  created_at: string;
  updated_at: string;
  records: ListRecord[];
}

interface ListRecord {
  id: number;
  company_name: string;
  address: string;
  phone: string;
  industry: string;
  url?: string;
  email?: string;
  representative?: string;
  employee_size?: string;
  capital?: string;
  established_year?: string;
}

const validationSchema = Yup.object({
  name: Yup.string().required('リスト名は必須です'),
});

const ListDetailPage = () => {
  const router = useRouter();
  const { id } = router.query;
  const [listDetail, setListDetail] = useState<ListDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    if (id) {
      fetchListDetail();
    }
  }, [id]);

  const fetchListDetail = async () => {
    setLoading(true);
    try {
      // 実際のAPIエンドポイントに置き換える
      const response = await axios.get(`/api/lists/${id}`);
      setListDetail(response.data);
      formik.setValues({
        name: response.data.name,
        description: response.data.description || '',
      });
    } catch (error) {
      console.error('リスト詳細の取得に失敗しました:', error);
      setError('リスト詳細の取得に失敗しました。再度お試しください。');
      
      // ダミーデータ（実際の実装では削除）
      const dummyData: ListDetail = {
        id: Number(id),
        name: 'IT企業リスト（東京）',
        description: 'キーワード検索: IT, システム開発, ソフトウェア / 東京都',
        total_records: 1250,
        created_at: '2025-04-15T10:30:00Z',
        updated_at: '2025-04-15T10:30:00Z',
        records: [
          {
            id: 1,
            company_name: '株式会社システム開発センター',
            address: '東京都千代田区平河町2丁目',
            phone: '03-3239-1291',
            industry: 'IT・情報通信',
            url: 'https://example.com/company1',
            email: 'info@example1.com',
            representative: '山田太郎',
            employee_size: '50-100人',
            capital: '1000万円',
            established_year: '2005'
          },
          {
            id: 2,
            company_name: '株式会社千代田ビデオ',
            address: '東京都千代田区北の丸公園2',
            phone: '03-3215-2741',
            industry: 'IT・情報通信',
            url: 'https://example.com/company2',
            email: 'info@example2.com',
            representative: '佐藤次郎',
            employee_size: '10-50人',
            capital: '500万円',
            established_year: '2010'
          },
          {
            id: 3,
            company_name: '株式会社テクストプラス',
            address: '東京都千代田区外神田2丁目',
            phone: '03-5577-5266',
            industry: 'IT・情報通信',
            url: 'https://example.com/company3',
            email: 'info@example3.com',
            representative: '鈴木三郎',
            employee_size: '10-50人',
            capital: '300万円',
            established_year: '2015'
          },
          {
            id: 4,
            company_name: '株式会社翔洋',
            address: '東京都千代田区岩本町2丁目',
            phone: '03-3862-1566',
            industry: 'IT・情報通信',
            url: 'https://example.com/company4',
            email: 'info@example4.com',
            representative: '高橋四郎',
            employee_size: '10人未満',
            capital: '100万円',
            established_year: '2018'
          },
          {
            id: 5,
            company_name: 'パスロジ株式会社',
            address: '東京都千代田区神田神保町1',
            phone: '03-5283-2263',
            industry: 'IT・情報通信',
            url: 'https://example.com/company5',
            email: 'info@example5.com',
            representative: '田中五郎',
            employee_size: '10-50人',
            capital: '500万円',
            established_year: '2012'
          }
        ]
      };
      setListDetail(dummyData);
      formik.setValues({
        name: dummyData.name,
        description: dummyData.description || '',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const formik = useFormik({
    initialValues: {
      name: '',
      description: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        await axios.put(`/api/lists/${id}`, values);
        setSuccess('リスト情報が更新されました');
        setEditMode(false);
        if (listDetail) {
          setListDetail({
            ...listDetail,
            name: values.name,
            description: values.description,
          });
        }
        setTimeout(() => {
          setSuccess('');
        }, 3000);
      } catch (error) {
        console.error('リスト情報の更新に失敗しました:', error);
        setError('リスト情報の更新に失敗しました。再度お試しください。');
      }
    },
  });

  const handleExportCSV = async () => {
    try {
      const response = await axios.get(`/api/lists/${id}/export`, {
        responseType: 'blob'
      });
      
      // Blobを作成してダウンロード
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `list_${id}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('CSVエクスポートに失敗しました:', error);
      setError('CSVエクスポートに失敗しました。再度お試しください。');
    }
  };

  return (
    <DashboardLayout title="リスト詳細">
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      ) : listDetail ? (
        <>
          <Box sx={{ mb: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h4">
                {editMode ? '編集中: ' : ''}
                {listDetail.name}
              </Typography>
              <Box>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportCSV}
                  sx={{ mr: 1 }}
                >
                  CSVエクスポート
                </Button>
                {editMode ? (
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={() => formik.handleSubmit()}
                  >
                    保存
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    startIcon={<EditIcon />}
                    onClick={() => setEditMode(true)}
                  >
                    編集
                  </Button>
                )}
              </Box>
            </Box>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            {success && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {success}
              </Alert>
            )}
          </Box>

          <Paper sx={{ p: 3, mb: 4 }}>
            {editMode ? (
              <form onSubmit={formik.handleSubmit}>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      id="name"
                      name="name"
                      label="リスト名"
                      value={formik.values.name}
                      onChange={formik.handleChange}
                      error={formik.touched.name && Boolean(formik.errors.name)}
                      helperText={formik.touched.name && formik.errors.name}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      id="description"
                      name="description"
                      label="説明"
                      value={formik.values.description}
                      onChange={formik.handleChange}
                    />
                  </Grid>
                </Grid>
              </form>
            ) : (
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    リスト名
                  </Typography>
                  <Typography variant="body1">
                    {listDetail.name}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    説明
                  </Typography>
                  <Typography variant="body1">
                    {listDetail.description || '説明なし'}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    レコード数
                  </Typography>
                  <Typography variant="body1">
                    {listDetail.total_records.toLocaleString()} 件
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    作成日
                  </Typography>
                  <Typography variant="body1">
                    {new Date(listDetail.created_at).toLocaleString('ja-JP')}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary">
                    更新日
                  </Typography>
                  <Typography variant="body1">
                    {new Date(listDetail.updated_at).toLocaleString('ja-JP')}
                  </Typography>
                </Grid>
              </Grid>
            )}
          </Paper>

          <Paper sx={{ mb: 4 }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              variant="fullWidth"
            >
              <Tab label="企業リスト" />
              <Tab label="統計情報" />
            </Tabs>
            
            {tabValue === 0 && (
              <TableContainer>
                <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    startIcon={<FilterListIcon />}
                    size="small"
                  >
                    フィルター
                  </Button>
                </Box>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>企業名</TableCell>
                      <TableCell>住所</TableCell>
                      <TableCell>電話番号</TableCell>
                      <TableCell>業種</TableCell>
                      <TableCell>URL</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {listDetail.records.map((record) => (
                      <TableRow key={record.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {record.company_name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {record.address}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {record.phone}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip label={record.industry} size="small" />
                        </TableCell>
                        <TableCell>
                          {record.url ? (
                            <Button
                              href={record.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              size="small"
                            >
                              サイト
                            </Button>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              -
                            </Typography>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
            
            {tabValue === 1 && (
              <Box sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  統計情報
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle2" color="text.secondary">
                          業種別分布
                        </Typography>
                        <Typography variant="body1">
                          IT・情報通信: 80%
                        </Typography>
                        <Typography variant="body1">
                          製造業: 15%
                        </Typography>
                        <Typography variant="body1">
                          その他: 5%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle2" color="text.secondary">
                          地域別分布
                        </Typography>
                        <Typography variant="body1">
                          東京都: 65%
                        </Typography>
                        <Typography variant="body1">
                          神奈川県: 20%
                        </Typography>
                        <Typography variant="body1">
                          その他: 15%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle2" color="text.secondary">
                          従業員規模
                        </Typography>
                        <Typography variant="body1">
                          10人未満: 30%
                        </Typography>
                        <Typography variant="body1">
                          10-50人: 45%
                        </Typography>
                        <Typography variant="body1">
                          50-100人: 15%
                        </Typography>
                        <Typography variant="body1">
                          100人以上: 10%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Box>
            )}
          </Paper>
        </>
      ) : (
        <Alert severity="error">
          リストが見つかりませんでした。
        </Alert>
      )}
    </DashboardLayout>
  );
};

export default ListDetailPage;

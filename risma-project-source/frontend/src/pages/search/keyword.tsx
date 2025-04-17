import { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Grid, 
  Card, 
  CardContent,
  TextField,
  Button,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  CircularProgress,
  Paper,
  Divider,
  Alert
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import DashboardLayout from '../../components/DashboardLayout';
import { useRouter } from 'next/router';
import api from '../../utils/api';

const validationSchema = Yup.object({
  keywords: Yup.array()
    .min(1, '少なくとも1つのキーワードを入力してください')
    .required('キーワードは必須です'),
  exclude_keywords: Yup.array(),
  list_name: Yup.string()
    .required('リスト名は必須です'),
  max_results: Yup.number()
    .min(10, '最小10件の結果が必要です')
    .max(10000, '最大10,000件まで取得できます')
    .required('取得件数は必須です'),
});

const KeywordSearch = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [jobId, setJobId] = useState<number | null>(null);

  const formik = useFormik({
    initialValues: {
      keywords: [],
      exclude_keywords: [],
      list_name: '',
      description: '',
      max_results: 1000,
    },
    validationSchema,
    onSubmit: async (values) => {
      setLoading(true);
      setError('');
      setSuccess(false);
      
      try {
        // まずリストを作成
        const listResponse = await api.lists.create({
          name: values.list_name,
          description: values.description || `キーワード検索: ${values.keywords.join(', ')}`,
        });
        
        const listId = listResponse.data.id;
        
        // 検索ジョブを作成
        const searchResponse = await api.search.keyword({
          keywords: values.keywords,
          exclude_keywords: values.exclude_keywords,
          max_results: values.max_results,
        }, listId);
        
        setJobId(searchResponse.data.id);
        setSuccess(true);
        
        // 3秒後に検索ジョブの詳細ページに遷移
        setTimeout(() => {
          router.push(`/search/jobs/${searchResponse.data.id}`);
        }, 3000);
      } catch (err: any) {
        setError(
          err.response?.data?.detail || 
          '検索ジョブの作成に失敗しました。入力内容を確認してください。'
        );
      } finally {
        setLoading(false);
      }
    },
  });

  const handleKeywordInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && e.currentTarget.value) {
      e.preventDefault();
      const keyword = e.currentTarget.value.trim();
      if (keyword && !formik.values.keywords.includes(keyword)) {
        formik.setFieldValue('keywords', [...formik.values.keywords, keyword]);
        e.currentTarget.value = '';
      }
    }
  };

  const handleExcludeKeywordInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && e.currentTarget.value) {
      e.preventDefault();
      const keyword = e.currentTarget.value.trim();
      if (keyword && !formik.values.exclude_keywords.includes(keyword)) {
        formik.setFieldValue('exclude_keywords', [...formik.values.exclude_keywords, keyword]);
        e.currentTarget.value = '';
      }
    }
  };

  const handleDeleteKeyword = (keyword: string) => {
    formik.setFieldValue(
      'keywords',
      formik.values.keywords.filter((k) => k !== keyword)
    );
  };

  const handleDeleteExcludeKeyword = (keyword: string) => {
    formik.setFieldValue(
      'exclude_keywords',
      formik.values.exclude_keywords.filter((k) => k !== keyword)
    );
  };

  return (
    <DashboardLayout title="キーワード検索">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          キーワード検索
        </Typography>
        <Typography variant="body1" color="text.secondary">
          キーワードを指定して企業リストを作成します。複数のキーワードを入力すると、それらを含む企業を検索します。
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          検索ジョブが正常に作成されました。ジョブID: {jobId}
          <br />
          検索結果ページに移動します...
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 4 }}>
        <form onSubmit={formik.handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                検索条件
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="キーワードを入力（Enterで追加）"
                placeholder="例: システム開発、IT、ソフトウェア"
                onKeyDown={handleKeywordInputKeyDown}
                disabled={loading}
                error={formik.touched.keywords && Boolean(formik.errors.keywords)}
                helperText={formik.touched.keywords && formik.errors.keywords}
              />
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formik.values.keywords.map((keyword) => (
                  <Chip
                    key={keyword}
                    label={keyword}
                    onDelete={() => handleDeleteKeyword(keyword)}
                    color="primary"
                  />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="除外キーワードを入力（Enterで追加）"
                placeholder="例: 個人、フリーランス"
                onKeyDown={handleExcludeKeywordInputKeyDown}
                disabled={loading}
              />
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formik.values.exclude_keywords.map((keyword) => (
                  <Chip
                    key={keyword}
                    label={keyword}
                    onDelete={() => handleDeleteExcludeKeyword(keyword)}
                    color="secondary"
                  />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="max-results-label">取得件数</InputLabel>
                <Select
                  labelId="max-results-label"
                  id="max_results"
                  name="max_results"
                  value={formik.values.max_results}
                  onChange={formik.handleChange}
                  label="取得件数"
                  disabled={loading}
                >
                  <MenuItem value={100}>100件</MenuItem>
                  <MenuItem value={500}>500件</MenuItem>
                  <MenuItem value={1000}>1,000件</MenuItem>
                  <MenuItem value={5000}>5,000件</MenuItem>
                  <MenuItem value={10000}>10,000件</MenuItem>
                </Select>
                <FormHelperText>
                  取得する最大件数を選択してください
                </FormHelperText>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                リスト情報
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="list_name"
                name="list_name"
                label="リスト名"
                value={formik.values.list_name}
                onChange={formik.handleChange}
                error={formik.touched.list_name && Boolean(formik.errors.list_name)}
                helperText={formik.touched.list_name && formik.errors.list_name}
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                id="description"
                name="description"
                label="説明（任意）"
                value={formik.values.description}
                onChange={formik.handleChange}
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                <Button
                  type="button"
                  variant="outlined"
                  sx={{ mr: 2 }}
                  onClick={() => router.push('/dashboard')}
                  disabled={loading}
                >
                  キャンセル
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading || formik.values.keywords.length === 0}
                >
                  {loading ? <CircularProgress size={24} /> : '検索を開始'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </DashboardLayout>
  );
};

export default KeywordSearch;

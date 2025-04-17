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
  Alert,
  Autocomplete
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import DashboardLayout from '../../components/DashboardLayout';
import { useRouter } from 'next/router';
import axios from 'axios';

const validationSchema = Yup.object({
  industry_codes: Yup.array()
    .min(1, '少なくとも1つの業種を選択してください')
    .required('業種は必須です'),
  prefectures: Yup.array()
    .min(1, '少なくとも1つの都道府県を選択してください')
    .required('都道府県は必須です'),
  list_name: Yup.string()
    .required('リスト名は必須です'),
  max_results: Yup.number()
    .min(10, '最小10件の結果が必要です')
    .max(10000, '最大10,000件まで取得できます')
    .required('取得件数は必須です'),
});

// 業種リスト
const industryOptions = [
  { code: '233', label: 'IT・情報通信' },
  { code: '210', label: 'メーカー' },
  { code: '220', label: '商社' },
  { code: '221', label: '小売' },
  { code: '240', label: '金融' },
  { code: '241', label: '保険' },
  { code: '250', label: '不動産' },
  { code: '251', label: '建設' },
  { code: '260', label: '運輸・物流' },
  { code: '270', label: 'マスコミ' },
  { code: '271', label: '広告・マーケティング' },
  { code: '280', label: 'コンサルティング' },
  { code: '290', label: '人材・教育' },
  { code: '300', label: '医療・福祉' },
  { code: '310', label: '飲食・宿泊' },
  { code: '320', label: 'サービス' },
  { code: '330', label: '公的機関' },
  { code: '999', label: 'その他' },
];

// 都道府県リスト
const prefectureOptions = [
  '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
  '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
  '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
  '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
  '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
  '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
  '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
];

const IndustryLocationSearch = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [jobId, setJobId] = useState<number | null>(null);
  const [cities, setCities] = useState<string[]>([]);
  const [selectedPrefecture, setSelectedPrefecture] = useState<string | null>(null);

  // 選択された都道府県に基づいて市区町村リストを取得する
  useEffect(() => {
    const fetchCities = async () => {
      if (selectedPrefecture) {
        try {
          // 実際のAPIエンドポイントに置き換える
          const response = await axios.get(`/api/location/cities?prefecture=${selectedPrefecture}`);
          setCities(response.data);
        } catch (error) {
          console.error('市区町村データの取得に失敗しました:', error);
          // ダミーデータ（実際の実装では削除）
          if (selectedPrefecture === '東京都') {
            setCities(['千代田区', '中央区', '港区', '新宿区', '文京区', '台東区', '墨田区', '江東区', '品川区', '目黒区', '大田区', '世田谷区', '渋谷区', '中野区', '杉並区', '豊島区', '北区', '荒川区', '板橋区', '練馬区', '足立区', '葛飾区', '江戸川区']);
          } else if (selectedPrefecture === '大阪府') {
            setCities(['大阪市', '堺市', '岸和田市', '豊中市', '池田市', '吹田市', '泉大津市', '高槻市', '貝塚市', '守口市', '枚方市', '茨木市', '八尾市', '泉佐野市', '富田林市', '寝屋川市', '河内長野市', '松原市', '大東市', '和泉市', '箕面市', '柏原市', '羽曳野市', '門真市', '摂津市', '高石市', '藤井寺市', '東大阪市', '泉南市', '四條畷市', '交野市', '大阪狭山市', '阪南市']);
          } else {
            setCities([]);
          }
        }
      } else {
        setCities([]);
      }
    };

    fetchCities();
  }, [selectedPrefecture]);

  const formik = useFormik({
    initialValues: {
      industry_codes: [],
      prefectures: [],
      cities: [],
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
        const listResponse = await axios.post('/api/lists/', {
          name: values.list_name,
          description: values.description || `業種×住所検索: ${values.industry_codes.map(code => {
            const industry = industryOptions.find(opt => opt.code === code);
            return industry ? industry.label : code;
          }).join(', ')} / ${values.prefectures.join(', ')}`,
        });
        
        const listId = listResponse.data.id;
        
        // 検索ジョブを作成
        const searchResponse = await axios.post(`/api/search/industry-location?list_id=${listId}`, {
          industry_codes: values.industry_codes,
          prefectures: values.prefectures,
          cities: values.cities,
          max_results: values.max_results,
        });
        
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

  // 都道府県選択時の処理
  const handlePrefectureChange = (event: any, newValue: string[]) => {
    formik.setFieldValue('prefectures', newValue);
    // 最後に選択された都道府県を記録
    if (newValue.length > 0) {
      const lastSelected = newValue[newValue.length - 1];
      setSelectedPrefecture(lastSelected);
    } else {
      setSelectedPrefecture(null);
    }
    // 都道府県が変更されたら市区町村の選択をリセット
    formik.setFieldValue('cities', []);
  };

  return (
    <DashboardLayout title="業種×住所検索">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          業種×住所検索
        </Typography>
        <Typography variant="body1" color="text.secondary">
          業種と地域を指定して企業リストを作成します。複数の業種や地域を選択すると、それらに該当する企業を検索します。
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
              <Autocomplete
                multiple
                id="industry_codes"
                options={industryOptions}
                getOptionLabel={(option) => option.label}
                value={industryOptions.filter(option => formik.values.industry_codes.includes(option.code))}
                onChange={(event, newValue) => {
                  formik.setFieldValue(
                    'industry_codes',
                    newValue.map(item => item.code)
                  );
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="業種"
                    placeholder="業種を選択"
                    error={formik.touched.industry_codes && Boolean(formik.errors.industry_codes)}
                    helperText={formik.touched.industry_codes && formik.errors.industry_codes}
                  />
                )}
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Autocomplete
                multiple
                id="prefectures"
                options={prefectureOptions}
                value={formik.values.prefectures}
                onChange={handlePrefectureChange}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="都道府県"
                    placeholder="都道府県を選択"
                    error={formik.touched.prefectures && Boolean(formik.errors.prefectures)}
                    helperText={formik.touched.prefectures && formik.errors.prefectures}
                  />
                )}
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Autocomplete
                multiple
                id="cities"
                options={cities}
                value={formik.values.cities}
                onChange={(event, newValue) => {
                  formik.setFieldValue('cities', newValue);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="市区町村（任意）"
                    placeholder="市区町村を選択"
                  />
                )}
                disabled={loading || formik.values.prefectures.length === 0}
              />
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
                  disabled={loading || formik.values.industry_codes.length === 0 || formik.values.prefectures.length === 0}
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

export default IndustryLocationSearch;

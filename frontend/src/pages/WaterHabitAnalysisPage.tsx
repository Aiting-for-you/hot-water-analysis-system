import React, { useState, useEffect, useCallback } from 'react';
import {
  Typography,
  Select,
  Button,
  Card,
  Row,
  Col,
  Spin,
  Alert,
  Divider,
  Empty,
  message,
  List,
  Modal,
  Space,
  Tag
} from 'antd';
import { LineChartOutlined, FileTextOutlined, HistoryOutlined, DeleteOutlined, EyeOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { 
  getDatasetsForAnalysis,
  runAnalysis, 
  getAnalysisResult,
  getAnalysisHistory,
  deleteAnalysisResult,
  downloadAnalysisReport,
  DatasetForAnalysis,
  AnalysisResult,
  AnalysisHistoryItem
} from '../api/analysis';

const { Title, Paragraph } = Typography;
const { Option } = Select;
const { confirm } = Modal;

const WaterHabitAnalysisPage: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetForAnalysis[]>([]);
  const [selectedDatasets, setSelectedDatasets] = useState<string[]>([]);
  const [isLoadingDatasets, setIsLoadingDatasets] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);


  const fetchDatasets = useCallback(async () => {
    setIsLoadingDatasets(true);
    try {
      const data = await getDatasetsForAnalysis();
      setDatasets(data);
    } catch (err: any) {
      message.error(err.response?.data?.msg || '加载数据集失败');
    } finally {
      setIsLoadingDatasets(false);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    setIsLoadingHistory(true);
    try {
      const historyData = await getAnalysisHistory();
      setHistory(historyData);
    } catch (err: any) {
      message.error(err.response?.data?.msg || '加载分析历史失败');
    } finally {
      setIsLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    fetchDatasets();
    fetchHistory();
  }, [fetchDatasets, fetchHistory]);

  const handleStartAnalysis = async () => {
    if (selectedDatasets.length === 0) {
      message.warning('请至少选择一个数据集');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const { result_id } = await runAnalysis(selectedDatasets);
      message.success('分析任务已启动，正在获取结果...');
      
      const results = await getAnalysisResult(result_id);
      setAnalysisResult(results);
      message.success('成功获取分析报告！');
      fetchHistory(); // Refresh history list
      setSelectedDatasets([]); // Clear selection

    } catch (err: any) {
      setError(`分析失败: ${err.response?.data?.msg || err.message}`);
      message.error(err.response?.data?.msg || '分析过程中发生错误');
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  const handleViewHistory = async (resultId: string) => {
    setIsAnalyzing(true); // Reuse the spinner
    setAnalysisResult(null);
    setError(null);
    try {
        const results = await getAnalysisResult(resultId);
        setAnalysisResult(results);
        message.success("已加载历史分析结果。");
    } catch (err: any) {
        message.error(err.response?.data?.msg || "加载历史记录失败。");
    } finally {
        setIsAnalyzing(false);
    }
  };

  const handleDeleteHistory = (resultId: string) => {
    confirm({
        title: '您确定要删除这条分析记录吗？',
        icon: <ExclamationCircleOutlined />,
        content: '删除后，相关的报告和图表将永久消失，无法恢复。',
        okText: '确认删除',
        okType: 'danger',
        cancelText: '取消',
        onOk: async () => {
            try {
                await deleteAnalysisResult(resultId);
                message.success('分析记录已成功删除。');
                fetchHistory(); // Refresh list
                if (analysisResult?.id === resultId) {
                    setAnalysisResult(null); // Clear view if it was showing the deleted item
                }
            } catch (err: any) {
                message.error(err.response?.data?.msg || "删除失败。");
            }
        },
    });
  };
  
  const handleDownloadReport = (resultId: string, resultName: string) => {
      try {
        downloadAnalysisReport(resultId, `${resultName}.txt`);
        message.success('报告下载已开始。');
      } catch(error) {
        message.error('下载失败。');
      }
  };


  return (
    <div style={{ padding: '24px' }}>
        <Row gutter={24}>
            {/* Left side: Controls and History */}
            <Col xs={24} md={8}>
                <Title level={2}>用水习惯分析</Title>
                <Paragraph>支持选择一个或多个数据集进行合并分析。</Paragraph>
                
                <Card style={{ marginBottom: 24 }}>
                    <Typography.Text strong>1. 选择数据集</Typography.Text>
                    <Select
                      mode="multiple"
                      allowClear
                      style={{ width: '100%', marginTop: 8, marginBottom: 16 }}
                      placeholder="请选择一个或多个数据集"
                      value={selectedDatasets}
                      onChange={(value) => setSelectedDatasets(value)}
                      loading={isLoadingDatasets}
                      disabled={isAnalyzing}
                    >
                      {datasets.map((ds) => (
                        <Option key={ds.id} value={ds.id}>
                          {ds.name}
                        </Option>
                      ))}
                    </Select>
                    <Button
                      type="primary"
                      onClick={handleStartAnalysis}
                      loading={isAnalyzing}
                      disabled={selectedDatasets.length === 0 || isLoadingDatasets}
                      icon={<LineChartOutlined />}
                      block
                    >
                      开始分析
                    </Button>
                </Card>

                <Card>
                    <Title level={4}><HistoryOutlined /> 历史分析记录</Title>
                    <List
                        loading={isLoadingHistory}
                        dataSource={history}
                        renderItem={item => (
                            <List.Item
                                actions={[
                                    <Button type="link" icon={<EyeOutlined />} onClick={() => handleViewHistory(item.id)}>查看</Button>,
                                    <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDeleteHistory(item.id)}>删除</Button>
                                ]}
                            >
                                <List.Item.Meta
                                    title={item.name}
                                    description={`分析于: ${new Date(item.created_at).toLocaleString()}`}
                                />
                            </List.Item>
                        )}
                        locale={{ emptyText: '暂无历史记录' }}
                    />
                </Card>
            </Col>

            {/* Right side: Analysis Results */}
            <Col xs={24} md={16}>
                {error && <Alert message="错误" description={error} type="error" showIcon style={{ marginBottom: 24 }} />}
                
                {isAnalyzing && (
                    <div style={{ textAlign: 'center', padding: '100px 50px' }}>
                    <Spin size="large" />
                    <p style={{ marginTop: '20px' }}>正在处理，请稍候...</p>
                    </div>
                )}

                {analysisResult ? (
                    <div>
                    <Card style={{ marginBottom: 24 }}>
                        <Space>
                            <Title level={3} style={{ margin: 0 }}>{analysisResult.name}</Title>
                            <Tag color="blue">分析于: {new Date(analysisResult.created_at).toLocaleString()}</Tag>
                        </Space>
                        <Divider />
                        <Button 
                            icon={<FileTextOutlined />} 
                            onClick={() => handleDownloadReport(analysisResult.id, analysisResult.name)}
                        >
                            下载分析报告
                        </Button>
                    </Card>
                    
                    <Title level={4}><LineChartOutlined /> 可视化图表</Title>
                    <Row gutter={[16, 16]}>
                        {analysisResult.charts.map(chart => (
                        <Col xs={24} lg={24} key={chart.id}>
                            <Card title={chart.title} bordered={false} hoverable>
                            <img src={chart.image_base64} alt={chart.title} style={{ width: '100%', height: 'auto' }}/>
                            </Card>
                        </Col>
                        ))}
                    </Row>
                    </div>
                ) : (
                    !isAnalyzing && (
                    <Empty description="请先选择数据集开始分析，或从左侧历史记录中查看以往的分析结果。" style={{ marginTop: 100 }} />
                    )
                )}
            </Col>
        </Row>
    </div>
  );
};

export default WaterHabitAnalysisPage;

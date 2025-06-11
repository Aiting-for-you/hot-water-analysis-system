import React, { useState, useEffect, useCallback } from 'react';
import { Card, List, Button, Spin, Alert, message, Typography, Tag } from 'antd';
import { SyncOutlined } from '@ant-design/icons';
import api from '../../api';

const { Title, Text, Paragraph } = Typography;

const LogViewerPage = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchLogs = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.get('/admin/logs');
            // Each item in response.data.logs is a JSON string, so we need to parse it.
            const parsedLogs = response.data.logs.map((logString, index) => {
                try {
                    return { id: index, ...JSON.parse(logString) };
                } catch (e) {
                    // Handle cases where a line is not valid JSON
                    return { id: index, level: 'ERROR', message: `Unparsable log entry: ${logString}` };
                }
            });
            setLogs(parsedLogs);
        } catch (err) {
            const errorMessage = err.response?.data?.error || '无法加载日志';
            setError(errorMessage);
            message.error(errorMessage);
            console.error('Fetch logs error:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchLogs();
    }, [fetchLogs]);

    const getTagColor = (level) => {
        switch (level) {
            case 'INFO':
                return 'cyan';
            case 'WARNING':
                return 'orange';
            case 'ERROR':
                return 'red';
            default:
                return 'default';
        }
    };

    return (
        <Card
            title="系统日志查看器"
            extra={
                <Button icon={<SyncOutlined />} onClick={fetchLogs} loading={loading}>
                    刷新
                </Button>
            }
        >
            <Title level={4}>最近 200 条日志记录</Title>
            {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />}
            <Spin spinning={loading}>
                <List
                    bordered
                    dataSource={logs}
                    renderItem={item => (
                        <List.Item>
                            <Paragraph style={{ margin: 0, width: '100%' }}>
                                <Tag color={getTagColor(item.level)}>{item.level || 'UNKNOWN'}</Tag>
                                <Text strong>{new Date(item.timestamp * 1000).toLocaleString()}</Text>
                                <Text code style={{ marginLeft: 8 }}>{item.name}</Text>
                                <br />
                                <Text>{item.message}</Text>
                            </Paragraph>
                        </List.Item>
                    )}
                    style={{ background: '#f5f5f5', maxHeight: '70vh', overflowY: 'auto' }}
                />
            </Spin>
        </Card>
    );
};

export default LogViewerPage; 
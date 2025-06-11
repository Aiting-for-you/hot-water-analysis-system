import React, { useState, useEffect } from 'react';
import { Typography, Row, Col, Card, Statistic, Spin, Alert } from 'antd';
import { UserOutlined, DatabaseOutlined, ExperimentOutlined, CheckCircleOutlined, SyncOutlined, CloseCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { getDashboardStats } from '../api/dashboard';

const { Title } = Typography;

const DashboardPage: React.FC = () => {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                setLoading(true);
                const data = await getDashboardStats();
                setStats(data);
            } catch (err) {
                setError('无法加载仪表板数据。');
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return <Spin size="large" style={{ display: 'block', marginTop: '50px' }} />;
    }

    if (error) {
        return <Alert message="错误" description={error} type="error" showIcon />;
    }

    return (
        <div>
            <Title level={2}>主控台</Title>
            <p>欢迎来到热水系统智能分析平台。以下是系统的当前状态总览。</p>
            
            <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={8} lg={6}>
                    <Card>
                        <Statistic title="注册用户总数" value={stats.users} prefix={<UserOutlined />} />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={6}>
                    <Card>
                        <Statistic title="数据集总数" value={stats.datasets} prefix={<DatabaseOutlined />} />
                    </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={6}>
                    <Card>
                        <Statistic title="分析任务总数" value={stats.total_tasks} prefix={<ExperimentOutlined />} />
                    </Card>
                </Col>
            </Row>

            <Title level={3} style={{ marginTop: '32px' }}>任务状态分布</Title>
            <Row gutter={[16, 16]}>
                <Col xs={12} sm={12} md={6}>
                    <Card>
                        <Statistic title="已完成" value={stats.tasks_by_status.completed} prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />} />
                    </Card>
                </Col>
                <Col xs={12} sm={12} md={6}>
                    <Card>
                        <Statistic title="运行中" value={stats.tasks_by_status.running} prefix={<SyncOutlined spin style={{ color: '#1890ff' }} />} />
                    </Card>
                </Col>
                <Col xs={12} sm={12} md={6}>
                    <Card>
                        <Statistic title="已失败" value={stats.tasks_by_status.failed} prefix={<CloseCircleOutlined style={{ color: '#ff4d4f' }} />} />
                    </Card>
                </Col>
                <Col xs={12} sm={12} md={6}>
                    <Card>
                        <Statistic title="待处理" value={stats.tasks_by_status.pending} prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />} />
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default DashboardPage; 
import React, { useState, useEffect, useCallback } from 'react';
import { Card, Table, Button, Form, Input, Checkbox, message, Spin, Empty, Typography } from 'antd';
import { FilePdfOutlined } from '@ant-design/icons';
import api from '../api';

const { Title } = Typography;
const { TextArea } = Input;

const ReportPage = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [selectedTaskIds, setSelectedTaskIds] = useState([]);
    const [form] = Form.useForm();

    const fetchCompletedTasks = useCallback(async () => {
        setLoading(true);
        try {
            const response = await api.get('/analysis/tasks');
            const completedTasks = response.data.filter(task => task.status === 'completed');
            setTasks(completedTasks);
        } catch (error) {
            message.error('无法加载分析任务列表');
            console.error('Fetch tasks error:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchCompletedTasks();
    }, [fetchCompletedTasks]);

    const handleGenerateReport = async (values) => {
        if (selectedTaskIds.length === 0) {
            message.warning('请至少选择一个分析任务来生成报告。');
            return;
        }

        setGenerating(true);
        try {
            const response = await api.post('/reports/generate', {
                task_ids: selectedTaskIds,
                title: values.title,
                description: values.description
            }, {
                responseType: 'blob', // Important for file download
            });

            const blob = new Blob([response.data], { type: 'application/pdf' });
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = `analysis_report_${Date.now()}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(link.href);

            message.success('报告已成功生成并开始下载！');
        } catch (error) {
            message.error('生成报告失败');
            console.error('Generate report error:', error);
        } finally {
            setGenerating(false);
        }
    };

    const columns = [
        { title: '任务名称', dataIndex: 'task_name', key: 'task_name' },
        { title: '任务类型', dataIndex: 'task_type', key: 'task_type' },
        { title: '创建时间', dataIndex: 'created_at', key: 'created_at', render: (text) => new Date(text).toLocaleString() },
    ];

    const rowSelection = {
        onChange: (selectedRowKeys) => {
            setSelectedTaskIds(selectedRowKeys);
        },
    };

    return (
        <Card>
            <Title level={3}>自动报告生成</Title>
            <Spin spinning={loading}>
                <Title level={4}>1. 选择已完成的分析任务</Title>
                <Table
                    rowKey="id"
                    rowSelection={rowSelection}
                    columns={columns}
                    dataSource={tasks}
                    locale={{ emptyText: <Empty description="没有已完成的分析任务" /> }}
                    style={{ marginBottom: 24 }}
                />

                <Title level={4}>2. 填写报告信息</Title>
                <Form form={form} layout="vertical" onFinish={handleGenerateReport}>
                    <Form.Item
                        name="title"
                        label="报告标题"
                        rules={[{ required: true, message: '请输入报告标题' }]}
                    >
                        <Input placeholder="例如：2023年度第四季度供水系统关联性分析报告" />
                    </Form.Item>
                    <Form.Item
                        name="description"
                        label="报告描述/结论"
                        rules={[{ required: true, message: '请输入报告的描述或结论' }]}
                    >
                        <TextArea rows={4} placeholder="在此输入对报告的整体描述或关键结论..." />
                    </Form.Item>
                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            icon={<FilePdfOutlined />}
                            loading={generating}
                            disabled={selectedTaskIds.length === 0}
                        >
                            生成并下载PDF报告
                        </Button>
                    </Form.Item>
                </Form>
            </Spin>
        </Card>
    );
};

export default ReportPage; 
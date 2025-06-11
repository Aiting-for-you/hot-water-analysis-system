import React, { useState, useEffect, useCallback } from 'react';
import { Button, Select, Table, message, Tag, Space, Popconfirm, Card, Typography, Tooltip } from 'antd';
import { UploadOutlined, DownloadOutlined, DeleteOutlined, SyncOutlined } from '@ant-design/icons';
import { getDatasets } from '../api/dataset';
import { getConversionTasks, runConversion, deleteConvertedDataset, downloadConvertedDataset, ConversionTask, ConvertedDataset } from '../api/conversion';
import { Dataset } from '../types/dataset';
import { filesize } from 'filesize';

const { Option } = Select;
const { Title, Text } = Typography;

const DataConversionPage: React.FC = () => {
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
    const [tasks, setTasks] = useState<ConversionTask[]>([]);
    const [loading, setLoading] = useState(false);
    const [runLoading, setRunLoading] = useState(false);

    const fetchTasks = useCallback(async () => {
        setLoading(true);
        try {
            const fetchedTasks = await getConversionTasks();
            setTasks(fetchedTasks);
        } catch (error) {
            message.error('加载转换任务失败');
            console.error(error);
        } finally {
            setLoading(false);
        }
    }, []);

    const fetchOriginalDatasets = useCallback(async () => {
        try {
            const fetchedDatasets = await getDatasets();
            // Filter for excel files, assuming format is in the name
            const excelDatasets = fetchedDatasets.filter(d => d.name.endsWith('.xlsx') || d.name.endsWith('.xls'));
            setDatasets(excelDatasets);
        } catch (error) {
            message.error('加载原始数据集失败');
        }
    }, []);

    useEffect(() => {
        fetchOriginalDatasets();
        fetchTasks();
        const interval = setInterval(fetchTasks, 10000); // Poll every 10 seconds
        return () => clearInterval(interval);
    }, [fetchOriginalDatasets, fetchTasks]);

    const handleRunConversion = async () => {
        if (!selectedDataset) {
            message.warning('请先选择一个原始数据集');
            return;
        }
        setRunLoading(true);
        try {
            await runConversion(selectedDataset);
            message.success('转换任务已启动！结果将在下方更新。');
            fetchTasks(); // Immediately fetch tasks after starting a new one
        } catch (error) {
            message.error('启动转换任务失败');
        } finally {
            setRunLoading(false);
        }
    };

    const handleDelete = async (datasetId: string) => {
        try {
            await deleteConvertedDataset(datasetId);
            message.success('删除成功');
            fetchTasks(); // Refresh the list
        } catch (error) {
            message.error('删除失败');
        }
    };
    
    const handleDownload = async (dataset: ConvertedDataset) => {
        try {
            // Add .csv extension for download
            await downloadConvertedDataset(dataset.id, `${dataset.name}.csv`);
        } catch (error) {
            message.error('下载失败');
        }
    };

    const expandedRowRender = (task: ConversionTask) => {
        const columns = [
            { title: '文件名', dataIndex: 'name', key: 'name', render: (name:string) => `${name}.csv` },
            { title: '文件大小', dataIndex: 'file_size', key: 'file_size', render: (size:number) => filesize(size) },
            { title: '创建时间', dataIndex: 'created_at', key: 'created_at', render: (date:string) => new Date(date).toLocaleString() },
            {
                title: '操作',
                key: 'action',
                render: (_: any, record: ConvertedDataset) => (
                    <Space size="middle">
                        <Tooltip title="下载">
                            <Button icon={<DownloadOutlined />} onClick={() => handleDownload(record)} />
                        </Tooltip>
                        <Popconfirm title="确定删除吗？" onConfirm={() => handleDelete(record.id)}>
                            <Tooltip title="删除">
                                <Button icon={<DeleteOutlined />} danger />
                            </Tooltip>
                        </Popconfirm>
                    </Space>
                ),
            },
        ];

        return <Table columns={columns} dataSource={task.converted_datasets} pagination={false} rowKey="id" />;
    };

    const taskColumns = [
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (status: string) => {
                let color = 'geekblue';
                if (status === 'completed') color = 'green';
                if (status === 'failed') color = 'volcano';
                if (status === 'processing') color = 'gold';
                return <Tag color={color} icon={status === 'processing' ? <SyncOutlined spin /> : null}>{status.toUpperCase()}</Tag>;
            },
        },
        { title: '原始文件', key: 'original_file', render: (_:any, task: ConversionTask) => {
            const original = datasets.find(d => d.id === task.original_dataset_id);
            return original ? original.name : '未知文件';
        }},
        { title: '任务启动时间', dataIndex: 'created_at', key: 'created_at', render: (date:string) => new Date(date).toLocaleString() },
        { title: '生成文件数', key: 'file_count', render: (_: any, task: ConversionTask) => task.converted_datasets.length },
    ];

    return (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Card>
                <Title level={4}>第一步：选择原始数据文件并开始转换</Title>
                <Space>
                    <Select
                        showSearch
                        style={{ width: 300 }}
                        placeholder="选择一个Excel数据集"
                        onChange={setSelectedDataset}
                        value={selectedDataset}
                        optionFilterProp="children"
                        filterOption={(input, option) =>
                          (option?.children as unknown as string).toLowerCase().includes(input.toLowerCase())
                        }
                    >
                        {datasets.map(d => <Option key={d.id} value={d.id}>{d.name}</Option>)}
                    </Select>
                    <Button
                        type="primary"
                        icon={<UploadOutlined />}
                        onClick={handleRunConversion}
                        loading={runLoading}
                        disabled={!selectedDataset}
                    >
                        开始转换
                    </Button>
                </Space>
                <Text type="secondary" style={{display: 'block', marginTop: '10px'}}>
                    请选择一个已上传的 Excel 文件 (.xls, .xlsx) 以启动数据格式转换。转换过程将在后台运行。
                </Text>
            </Card>

            <Card>
                 <Title level={4}>第二步：查看、下载或删除转换结果</Title>
                 <Text type="secondary" style={{display: 'block', marginBottom: '20px'}}>
                    下方列表展示了所有的转换任务和结果。列表将自动刷新。
                </Text>
                <Table
                    columns={taskColumns}
                    dataSource={tasks}
                    rowKey="id"
                    loading={loading}
                    expandable={{ expandedRowRender }}
                    title={() => (
                        <Button onClick={fetchTasks} icon={<SyncOutlined />} loading={loading}>
                            刷新
                        </Button>
                    )}
                />
            </Card>
        </Space>
    );
};

export default DataConversionPage;

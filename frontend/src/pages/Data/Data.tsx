import React, { useState, useEffect } from 'react';
import { Table, Button, Space, message, Modal, Upload, Typography, Progress } from 'antd';
import { UploadOutlined, DeleteOutlined } from '@ant-design/icons';
import { getDatasets, deleteDataset, uploadDataset } from '../../api/dataset';
import { Dataset } from '../../types/dataset';
import type { UploadProps } from 'antd';

const { confirm } = Modal;
const { Title } = Typography;

const DataPage: React.FC = () => {
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);

    const fetchDatasets = async () => {
        setLoading(true);
        try {
            const data = await getDatasets();
            setDatasets(data);
        } catch (error) {
            message.error('获取数据集列表失败');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDatasets();
    }, []);

    const handleDelete = (id: string) => {
        confirm({
            title: '确定要删除这个数据集吗?',
            content: '此操作将永久删除文件和所有相关的分析任务，且无法恢复。',
            okText: '确定删除',
            okType: 'danger',
            cancelText: '取消',
            onOk: async () => {
                try {
                    await deleteDataset(id);
                    message.success('数据集删除成功');
                    fetchDatasets(); // Refresh list
                } catch (error) {
                    message.error('删除失败');
                }
            },
        });
    };

    const handleUpload: UploadProps['customRequest'] = async (options) => {
        const { file, onSuccess, onError } = options;
        const actualFile = file as File;
        setUploading(true);
        setUploadProgress(0);
        try {
            await uploadDataset(actualFile, (event) => {
                const percent = Math.round((event.loaded * 100) / event.total);
                setUploadProgress(percent);
            });
            if (onSuccess) onSuccess("Ok");
            message.success(`${actualFile.name} 文件上传成功`);
            fetchDatasets();
        } catch (error) {
            if (onError) onError(new Error('上传失败'));
            message.error(`${actualFile.name} 文件上传失败.`);
        } finally {
            setUploading(false);
        }
    };

    const columns = [
        { title: '文件名', dataIndex: 'name', key: 'name' },
        { title: '文件大小', dataIndex: 'file_size', key: 'file_size', render: (size: number) => size ? `${(size / 1024 / 1024).toFixed(2)} MB` : 'N/A' },
        { title: '上传日期', dataIndex: 'created_at', key: 'created_at', render: (date: string) => new Date(date).toLocaleString() },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: Dataset) => (
                <Space size="middle">
                    <Button type="primary" danger onClick={() => handleDelete(record.id)} icon={<DeleteOutlined />}>
                        删除
                    </Button>
                </Space>
            ),
        },
    ];

    return (
        <div style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <Title level={2}>数据管理</Title>
                <Upload customRequest={handleUpload} showUploadList={false} disabled={uploading}>
                    <Button icon={<UploadOutlined />} loading={uploading}>
                        {uploading ? `上传中... ${uploadProgress}%` : '上传新数据集'}
                    </Button>
                </Upload>
            </div>
            {uploading && <Progress percent={uploadProgress} />}
            <Table
                columns={columns}
                dataSource={datasets}
                loading={loading}
                rowKey="id"
                style={{ marginTop: uploading ? '16px' : '0' }}
            />
        </div>
    );
};

export default DataPage; 
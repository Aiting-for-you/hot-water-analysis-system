import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, message, Popconfirm, Space } from 'antd';
import { getAllDatasets, deleteDataset } from '../../api/admin';

const DatasetManagementPage: React.FC = () => {
    const [datasets, setDatasets] = useState<any[]>([]);
    const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
    const [loading, setLoading] = useState(false);

    const fetchDatasets = useCallback(async (page = 1, pageSize = 10) => {
        setLoading(true);
        try {
            const data = await getAllDatasets(page, pageSize);
            setDatasets(data.datasets);
            setPagination({ current: data.current_page, pageSize: pageSize, total: data.total });
        } catch (error) {
            message.error('加载数据集列表失败');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDatasets();
    }, [fetchDatasets]);

    const handleTableChange = (pagination: any) => {
        fetchDatasets(pagination.current, pagination.pageSize);
    };

    const handleDelete = async (datasetId: string) => {
        try {
            await deleteDataset(datasetId);
            message.success('数据集已删除');
            fetchDatasets(pagination.current, pagination.pageSize);
        } catch (error) {
            message.error('删除失败');
        }
    };

    const columns = [
        { title: '名称', dataIndex: 'name', key: 'name' },
        { title: '文件名', dataIndex: 'file_name', key: 'file_name' },
        { title: '类型', dataIndex: 'file_type', key: 'file_type' },
        { title: '大小 (Bytes)', dataIndex: 'file_size', key: 'file_size' },
        { title: '创建者ID', dataIndex: 'creator_id', key: 'creator_id' },
        { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: any) => (
                <Space>
                    <Popconfirm title="确定要删除这个数据集吗？此操作不可恢复！" onConfirm={() => handleDelete(record.id)}>
                        <Button type="link" danger>删除</Button>
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    return (
        <Table
            columns={columns}
            rowKey="id"
            dataSource={datasets}
            pagination={pagination}
            loading={loading}
            onChange={handleTableChange}
            scroll={{ x: 1300 }}
        />
    );
};

export default DatasetManagementPage; 
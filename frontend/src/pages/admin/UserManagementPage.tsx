import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, message, Popconfirm, Modal, Form, Input, Select, Tag, Space } from 'antd';
import { getUsers, updateUser, deleteUser } from '../../api/admin';

const { Option } = Select;

const UserManagementPage: React.FC = () => {
    const [users, setUsers] = useState<any[]>([]);
    const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
    const [loading, setLoading] = useState(false);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [editingUser, setEditingUser] = useState<any | null>(null);
    const [form] = Form.useForm();

    const fetchUsers = useCallback(async (page = 1, pageSize = 10) => {
        setLoading(true);
        try {
            const data = await getUsers(page, pageSize);
            setUsers(data.users);
            setPagination({ current: data.current_page, pageSize: pageSize, total: data.total });
        } catch (error) {
            message.error('加载用户列表失败');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    const handleTableChange = (pagination: any) => {
        fetchUsers(pagination.current, pagination.pageSize);
    };

    const handleEdit = (user: any) => {
        setEditingUser(user);
        form.setFieldsValue(user);
        setIsModalVisible(true);
    };

    const handleDelete = async (userId: string) => {
        try {
            await deleteUser(userId);
            message.success('用户已停用');
            fetchUsers(pagination.current, pagination.pageSize);
        } catch (error) {
            message.error('操作失败');
        }
    };

    const handleModalOk = async () => {
        try {
            const values = await form.validateFields();
            await updateUser(editingUser.id, values);
            setIsModalVisible(false);
            setEditingUser(null);
            message.success('用户信息更新成功');
            fetchUsers(pagination.current, pagination.pageSize);
        } catch (error: any) {
            message.error(error.response?.data?.msg || '更新失败');
        }
    };

    const columns = [
        { title: '用户名', dataIndex: 'username', key: 'username' },
        { title: '电子邮箱', dataIndex: 'email', key: 'email' },
        { title: '角色', dataIndex: 'role', key: 'role', render: (role: string) => <Tag color={role === 'admin' ? 'volcano' : 'geekblue'}>{role.toUpperCase()}</Tag> },
        { title: '状态', dataIndex: 'is_active', key: 'is_active', render: (isActive: boolean) => <Tag color={isActive ? 'green' : 'red'}>{isActive ? '正常' : '停用'}</Tag> },
        { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
        {
            title: '操作',
            key: 'action',
            render: (_: any, record: any) => (
                <Space>
                    <Button type="link" onClick={() => handleEdit(record)}>编辑</Button>
                    <Popconfirm title="确定要停用此用户吗？" onConfirm={() => handleDelete(record.id)}>
                        <Button type="link" danger>停用</Button>
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    return (
        <div>
            <Table
                columns={columns}
                rowKey="id"
                dataSource={users}
                pagination={pagination}
                loading={loading}
                onChange={handleTableChange}
            />
            <Modal
                title="编辑用户"
                visible={isModalVisible}
                onOk={handleModalOk}
                onCancel={() => setIsModalVisible(false)}
            >
                <Form form={form} layout="vertical">
                    <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name="email" label="电子邮箱" rules={[{ required: true, type: 'email' }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name="role" label="角色" rules={[{ required: true }]}>
                        <Select>
                            <Option value="user">User</Option>
                            <Option value="admin">Admin</Option>
                        </Select>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default UserManagementPage; 
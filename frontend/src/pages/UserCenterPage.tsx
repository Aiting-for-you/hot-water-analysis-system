import React, { useState, useEffect } from 'react';
import { Typography, Form, Input, Button, message, Card, Row, Col, Spin } from 'antd';
import { getUserProfile, updateUserProfile, changePassword } from '../api/user';

const { Title } = Typography;

const UserCenterPage: React.FC = () => {
    const [profileForm] = Form.useForm();
    const [passwordForm] = Form.useForm();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const profile = await getUserProfile();
                profileForm.setFieldsValue(profile);
            } catch (error) {
                message.error('加载用户信息失败');
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [profileForm]);

    const handleUpdateProfile = async (values: any) => {
        try {
            await updateUserProfile(values);
            message.success('个人信息更新成功！');
        } catch (error: any) {
            message.error(error.response?.data?.msg || '更新失败');
        }
    };

    const handleChangePassword = async (values: any) => {
        if (values.new_password !== values.confirm_password) {
            message.error('两次输入的新密码不一致！');
            return;
        }
        try {
            await changePassword({ old_password: values.old_password, new_password: values.new_password });
            message.success('密码修改成功！');
            passwordForm.resetFields();
        } catch (error: any) {
            message.error(error.response?.data?.msg || '密码修改失败');
        }
    };

    if (loading) {
        return <Spin size="large" />;
    }

    return (
        <div>
            <Title level={2}>用户中心</Title>
            <Row gutter={[16, 16]}>
                <Col xs={24} md={12}>
                    <Card title="个人信息">
                        <Form form={profileForm} layout="vertical" onFinish={handleUpdateProfile}>
                            <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
                                <Input />
                            </Form.Item>
                            <Form.Item name="email" label="电子邮箱" rules={[{ required: true, type: 'email' }]}>
                                <Input />
                            </Form.Item>
                            <Form.Item>
                                <Button type="primary" htmlType="submit">更新信息</Button>
                            </Form.Item>
                        </Form>
                    </Card>
                </Col>
                <Col xs={24} md={12}>
                    <Card title="修改密码">
                        <Form form={passwordForm} layout="vertical" onFinish={handleChangePassword}>
                            <Form.Item name="old_password" label="旧密码" rules={[{ required: true }]}>
                                <Input.Password />
                            </Form.Item>
                            <Form.Item name="new_password" label="新密码" rules={[{ required: true }]}>
                                <Input.Password />
                            </Form.Item>
                            <Form.Item name="confirm_password" label="确认新密码" rules={[{ required: true }]} dependencies={['new_password']}>
                                <Input.Password />
                            </Form.Item>
                            <Form.Item>
                                <Button type="primary" htmlType="submit">修改密码</Button>
                            </Form.Item>
                        </Form>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default UserCenterPage; 
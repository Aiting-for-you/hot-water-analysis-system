import React from 'react';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Typography, Grid } from 'antd';
import {
    HomeOutlined,
    DatabaseOutlined,
    LineChartOutlined,
    UserOutlined,
    SettingOutlined,
    LogoutOutlined,
    TeamOutlined,
    FileTextOutlined,
    ApiOutlined,
    FileSearchOutlined,
    FileDoneOutlined,
    AreaChartOutlined,
    CommentOutlined,
    CloudOutlined,
} from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';

const { Header, Content, Sider } = Layout;
const { SubMenu } = Menu;
const { Title } = Typography;
const { useBreakpoint } = Grid;

const AppLayout = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const screens = useBreakpoint();

    const isAdmin = user && user.role === 'admin';

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const userMenu = (
        <Menu>
            <Menu.Item key="user-center" icon={<UserOutlined />}>
                <Link to="/user-center">个人中心</Link>
            </Menu.Item>
            <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
                退出登录
            </Menu.Item>
        </Menu>
    );

    const sider = (
         <Sider
            breakpoint="lg"
            collapsedWidth="0"
            style={{
                height: '100vh',
                position: 'fixed',
                left: 0,
            }}
        >
            <div style={{ height: '32px', margin: '16px', background: 'rgba(255, 255, 255, 0.2)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                 <Title level={4} style={{ color: 'white', margin: 0, fontSize: '16px' }}>热水系统</Title>
            </div>
            <Menu theme="dark" mode="inline" selectedKeys={[location.pathname]}>
                <Menu.Item key="/dashboard" icon={<HomeOutlined />}>
                    <Link to="/dashboard">主控台</Link>
                </Menu.Item>
                <Menu.Item key="/data" icon={<DatabaseOutlined />}>
                    <Link to="/data">数据管理</Link>
                </Menu.Item>
                <Menu.Item key="/data-conversion" icon={<LineChartOutlined />}>
                    <Link to="/data-conversion">数据格式转换</Link>
                </Menu.Item>
                <Menu.Item key="/water-habit-analysis" icon={<AreaChartOutlined />}>
                    <Link to="/water-habit-analysis">用水习惯分析</Link>
                </Menu.Item>
                <Menu.Item key="/reports" icon={<FileDoneOutlined />}>
                    <Link to="/reports">自动报告</Link>
                </Menu.Item>
                <Menu.Item key="/weather" icon={<CloudOutlined />}>
                    <Link to="/weather">天气查询</Link>
                </Menu.Item>
                <Menu.Item key="/assistant" icon={<CommentOutlined />}>
                    <Link to="/assistant">AI助手</Link>
                </Menu.Item>
                
                {isAdmin && (
                    <SubMenu key="admin" icon={<SettingOutlined />} title="系统管理">
                        <Menu.Item key="/admin/user-management" icon={<TeamOutlined />}>
                            <Link to="/admin/user-management">用户管理</Link>
                        </Menu.Item>
                        <Menu.Item key="/admin/dataset-management" icon={<FileTextOutlined />}>
                            <Link to="/admin/dataset-management">数据集管理</Link>
                        </Menu.Item>
                        <Menu.Item key="/admin/logs" icon={<FileSearchOutlined />}>
                            <Link to="/admin/logs">系统日志</Link>
                        </Menu.Item>
                    </SubMenu>
                )}
            </Menu>
        </Sider>
    );


    return (
        <Layout style={{ minHeight: '100vh' }}>
            {sider}
            <Layout style={{ marginLeft: screens.lg ? 200 : 0, transition: 'margin-left 0.2s' }}>
                <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', borderBottom: '1px solid #f0f0f0' }}>
                    <Dropdown overlay={userMenu} placement="bottomRight">
                        <a onClick={e => e.preventDefault()} style={{display: 'flex', alignItems: 'center'}}>
                            <Avatar icon={<UserOutlined />} style={{ marginRight: 8 }} />
                            <Typography.Text>{user?.username || '用户'}</Typography.Text>
                        </a>
                    </Dropdown>
                </Header>
                <Content style={{ margin: '24px 16px 0', overflow: 'initial' }}>
                    <div style={{ padding: 24, background: '#fff', minHeight: 'calc(100vh - 112px)' }}>
                        <Outlet />
                    </div>
                </Content>
            </Layout>
        </Layout>
    );
};

export default AppLayout; 
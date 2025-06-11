import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Paragraph } = Typography;

const DashboardPage: React.FC = () => {
    return (
        <div style={{ padding: '24px' }}>
            <Title level={2}>欢迎来到热水系统智能分析平台</Title>
            <Card>
                <Paragraph>
                    这里是您的主控台。您可以在这里找到系统的关键指标、最近的分析报告以及快速访问常用功能。
                </Paragraph>
            </Card>
        </div>
    );
};

export default DashboardPage; 
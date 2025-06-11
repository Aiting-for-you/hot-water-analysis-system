import React from 'react';
import { Typography, Result } from 'antd';

const { Title, Paragraph } = Typography;

const ReportsPage = () => {
    return (
        <div>
            <Title level={2}>自动报告</Title>
            <Paragraph>
                此功能正在开发中。您将能够在这里生成和查看自动化的数据分析报告。
            </Paragraph>
            <Result
                status="info"
                title="即将推出"
                subTitle="自动报告功能正在紧张开发中，敬请期待！"
            />
        </div>
    );
};

export default ReportsPage; 
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Input, Button, List, Spin, Avatar, Card, Typography, Row, Col, Popover, Tooltip, message as antdMessage } from 'antd';
import { UserOutlined, RobotOutlined, SettingOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;
const { TextArea } = Input;

const AssistantPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState(localStorage.getItem('bailian_api_key') || '');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const addMessage = useCallback((sender, text) => {
    setMessages(prev => [...prev, { sender, text }]);
  }, []);

  useEffect(() => {
    addMessage('ai', '您好！我是您的智能助手。请在右上角设置您的API密钥后开始对话。');
  }, [addMessage]);
  
  const handleApiKeyChange = (e) => {
    const newApiKey = e.target.value;
    setApiKey(newApiKey);
    localStorage.setItem('bailian_api_key', newApiKey);
  };

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;
    if (!apiKey) {
      antdMessage.error('请先在右上角设置中输入您的API密钥。');
      return;
    }

    addMessage('user', inputValue);
    setInputValue('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('/api/ai/chat', 
        { message: inputValue, apiKey: apiKey },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      addMessage('ai', response.data.reply);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error.response?.data?.reply || '抱歉，我暂时遇到了一些问题，无法回复您。请稍后再试。';
      addMessage('ai', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const apiKeyInputContent = (
    <div style={{ width: 300 }}>
      <p>请输入阿里云百炼API密钥：</p>
      <Input.Password
        placeholder="sk-..."
        value={apiKey}
        onChange={handleApiKeyChange}
      />
       <small>密钥将仅保存在您的浏览器中。</small>
    </div>
  );

  const cardTitle = (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Title level={4} style={{ margin: 0 }}>智能AI助手</Title>
    </div>
  );
  
  const cardExtra = (
      <Popover content={apiKeyInputContent} title="API密钥设置" trigger="click" placement="bottomRight">
        <Tooltip title="设置API密钥">
            <Button shape="circle" icon={<SettingOutlined />} />
        </Tooltip>
      </Popover>
  );

  return (
    <Card title={cardTitle} extra={cardExtra} style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flexGrow: 1, overflowY: 'auto', padding: '16px' }}>
        <List
          dataSource={messages}
          renderItem={(item) => (
            <List.Item style={{ border: 'none', justifyContent: item.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', maxWidth: '80%' }}>
                {item.sender === 'ai' && <Avatar icon={<RobotOutlined />} style={{ marginRight: 8, backgroundColor: '#1890ff' }} />}
                <div
                  style={{
                    background: item.sender === 'user' ? '#d9f7be' : '#f0f0f0',
                    padding: '8px 12px',
                    borderRadius: '12px',
                  }}
                >
                  {item.text}
                </div>
                {item.sender === 'user' && <Avatar icon={<UserOutlined />} style={{ marginLeft: 8 }} />}
              </div>
            </List.Item>
          )}
        />
        {loading && <Spin style={{ display: 'block' }} />}
        <div ref={messagesEndRef} />
      </div>
      <div style={{ padding: '16px', borderTop: '1px solid #f0f0f0' }}>
        <Row gutter={16}>
          <Col flex="auto">
            <TextArea
              rows={2}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onPressEnter={(e) => {
                if (!e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="请输入您的问题..."
              disabled={loading}
            />
          </Col>
          <Col flex="none">
            <Button type="primary" onClick={handleSendMessage} loading={loading}>
              发送
            </Button>
          </Col>
        </Row>
      </div>
    </Card>
  );
};

export default AssistantPage; 
import React, { useState } from 'react';
import { Card, Input, Button, Form, message, Spin, Descriptions } from 'antd';
import { getWeatherByCity } from '../api/weather';

const WeatherPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [weatherData, setWeatherData] = useState(null);

  const handleSearch = async (values) => {
    setLoading(true);
    setWeatherData(null);
    try {
      const response = await getWeatherByCity(values.city);
      if (response && response.result) {
        setWeatherData(response.result);
        message.success('天气数据获取成功');
      } else {
        message.error(response.msg || '未能获取天气数据');
      }
    } catch (error) {
      console.error("Failed to fetch weather data:", error);
      message.error('查询天气失败，请检查网络或联系管理员');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <Card title="天气查询">
        <Form form={form} layout="inline" onFinish={handleSearch} style={{ marginBottom: '20px' }}>
          <Form.Item
            name="city"
            rules={[{ required: true, message: '请输入城市名称！' }]}
          >
            <Input placeholder="例如：北京" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              查询
            </Button>
          </Form.Item>
        </Form>
        
        {loading && <Spin />}

        {weatherData && (
          <Descriptions title="天气详情" bordered>
            <Descriptions.Item label="城市">{weatherData.city}</Descriptions.Item>
            <Descriptions.Item label="天气状况">{weatherData.weather}</Descriptions.Item>
            <Descriptions.Item label="温度">{weatherData.temp}°C</Descriptions.Item>
            <Descriptions.Item label="最低温">{weatherData.templow}°C</Descriptions.Item>
            <Descriptions.Item label="最高温">{weatherData.temphigh}°C</Descriptions.Item>
            <Descriptions.Item label="风向">{weatherData.winddirect}</Descriptions.Item>
            <Descriptions.Item label="风力">{weatherData.windpower}</Descriptions.Item>
            <Descriptions.Item label="湿度">{weatherData.humidity}</Descriptions.Item>
            <Descriptions.Item label="更新时间">{weatherData.updatetime}</Descriptions.Item>
          </Descriptions>
        )}
      </Card>
    </div>
  );
};

export default WeatherPage; 
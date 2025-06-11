import React, { useState } from 'react';
import { searchCities, getHourlyWeather } from '../api/weather';
import { Input, Button, Table, Spin, Alert, List, Typography } from 'antd';

const { Title } = Typography;

const WeatherPage = () => {
  const [city, setCity] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [cityResults, setCityResults] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);

  const handleSearch = async () => {
    if (!city) return;
    setLoading(true);
    setError(null);
    setWeatherData(null);
    setCityResults([]);
    setSelectedCity(null);
    try {
      const results = await searchCities(city);
      if (results && results.length > 0) {
        setCityResults(results);
      } else {
        setError('未找到相关城市，请检查输入。');
      }
    } catch (err) {
      setError('搜索城市失败，请稍后再试。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCitySelect = async (selected) => {
    setSelectedCity(selected);
    setCityResults([]);
    setLoading(true);
    setError(null);
    try {
      const data = await getHourlyWeather(selected.areacode);
      setWeatherData(data);
    } catch (err) {
      setError('获取天气数据失败，请稍后再试。');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: '时间', dataIndex: 'data_time', key: 'data_time' },
    { title: '天气', dataIndex: 'text', key: 'text' },
    { title: '温度 (°C)', dataIndex: 'temp_fc', key: 'temp_fc' },
    { title: '风向', dataIndex: 'wind_dir', key: 'wind_dir' },
    { title: '风力等级', dataIndex: 'wind_class', key: 'wind_class' },
    { title: '相对湿度 (%)', dataIndex: 'rh', key: 'rh' },
  ];

  return (
    <div>
      <Title level={2}>天气查询</Title>
      <div style={{ marginBottom: 20, display: 'flex', gap: '10px' }}>
        <Input
          placeholder="请输入城市名称，例如：北京"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          onPressEnter={handleSearch}
          style={{ maxWidth: 300 }}
        />
        <Button type="primary" onClick={handleSearch} loading={loading}>
          搜索
        </Button>
      </div>

      {loading && <Spin />}

      {error && <Alert message={error} type="error" showIcon />}

      {cityResults.length > 0 && (
        <List
          header={<Title level={4}>请选择一个城市：</Title>}
          bordered
          dataSource={cityResults}
          renderItem={(item) => (
            <List.Item
              onClick={() => handleCitySelect(item)}
              style={{ cursor: 'pointer' }}
            >
              {item.path} ({item.name})
            </List.Item>
          )}
        />
      )}
      
      {selectedCity && weatherData && (
        <div>
          <Title level={3}>{selectedCity.name} - 逐小时天气预报</Title>
          <Table
            dataSource={weatherData.hourly_fcsts}
            columns={columns}
            rowKey="data_time"
            pagination={{ pageSize: 12 }}
          />
        </div>
      )}
    </div>
  );
};

export default WeatherPage; 
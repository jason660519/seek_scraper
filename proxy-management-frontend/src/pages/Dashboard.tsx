/**
 * 儀表板組件
 * @author TRAE
 * @description 系統主控制台，顯示統計數據、圖表和快捷操作
 */

import React, { useState } from 'react';
import { Row, Col, Card, Statistic, Button, Space, Table, Tag } from 'antd';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined,
  ReloadOutlined,
  GlobalOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { EChartsOption } from 'echarts';
import ReactECharts from 'echarts-for-react';
import { useResponsive } from '../utils/responsive';
import { useWebSocket } from '../hooks/useWebSocket';

/**
 * 儀表板頁面組件
 * @description 顯示系統概覽、統計數據、圖表和最近活動
 */
const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const { isMobile, getSpacing, getCardPadding } = useResponsive();
  const { isConnected: wsConnected } = useWebSocket();
  const [refreshing, setRefreshing] = useState(false);

  // 模擬數據
  const [statistics, setStatistics] = useState({
    totalProxies: 1247,
    validProxies: 892,
    invalidProxies: 355,
    successRate: 71.5
  });

  const [recentActivity] = useState([
    {
      key: '1',
      time: '2024-01-15 14:30:25',
      action: '代理驗證完成',
      details: '驗證了 156 個代理，其中 132 個有效',
      status: 'success'
    },
    {
      key: '2',
      time: '2024-01-15 14:25:10',
      action: '導入代理',
      details: '從 API 導入 89 個新代理',
      status: 'info'
    },
    {
      key: '3',
      time: '2024-01-15 14:20:45',
      action: '清理無效代理',
      details: '刪除了 23 個長時間無效的代理',
      status: 'warning'
    },
    {
      key: '4',
      time: '2024-01-15 14:15:30',
      action: '系統檢查',
      details: '系統資源使用正常，內存佔用 45%',
      status: 'success'
    }
  ]);

  // 代理數量趨勢圖配置
  const proxyTrendOption: EChartsOption = {
    title: {
      text: t('dashboard.proxyTrend'),
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['總代理數', '有效代理數'],
      bottom: 0
    },
    xAxis: {
      type: 'category',
      data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
    },
    yAxis: {
      type: 'value',
      name: '數量'
    },
    series: [
      {
        name: '總代理數',
        type: 'line',
        data: [1200, 1180, 1195, 1230, 1247, 1235, 1220],
        smooth: true,
        itemStyle: {
          color: '#1890ff'
        }
      },
      {
        name: '有效代理數',
        type: 'line',
        data: [850, 840, 860, 875, 892, 880, 865],
        smooth: true,
        itemStyle: {
          color: '#52c41a'
        }
      }
    ]
  };

  // 有效性分佈餅圖配置
  const validityDistributionOption: EChartsOption = {
    title: {
      text: t('dashboard.validityDistribution'),
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '代理狀態',
        type: 'pie',
        radius: '50%',
        data: [
          { value: statistics.validProxies, name: t('proxy.status.valid') },
          { value: statistics.invalidProxies, name: t('proxy.status.invalid') },
          { value: 45, name: t('proxy.status.temporarily_invalid') },
          { value: 125, name: t('proxy.status.untested') }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };

  // 地理分佈圖配置
  const geographicDistributionOption: EChartsOption = {
    title: {
      text: t('dashboard.geographicDistribution'),
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ['美國', '中國', '日本', '德國', '英國', '法國', '加拿大', '其他'],
      axisLabel: {
        interval: 0,
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '代理數量'
    },
    series: [
      {
        name: '代理數量',
        type: 'bar',
        data: [320, 280, 150, 120, 100, 80, 70, 127],
        itemStyle: {
          color: new (window as any).echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }
    ]
  };

  // 刷新數據
  const handleRefresh = async () => {
    setRefreshing(true);
    // 模擬API調用
    setTimeout(() => {
      setStatistics(prev => ({
        ...prev,
        totalProxies: prev.totalProxies + Math.floor(Math.random() * 10 - 5),
        validProxies: prev.validProxies + Math.floor(Math.random() * 6 - 3),
        invalidProxies: prev.invalidProxies + Math.floor(Math.random() * 4 - 2),
        successRate: Math.max(0, Math.min(100, prev.successRate + (Math.random() * 2 - 1)))
      }));
      setRefreshing(false);
    }, 1000);
  };

  // 獲取狀態標籤顏色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'processing';
    }
  };

  // 獲取狀態圖標
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircleOutlined />;
      case 'warning': return <ClockCircleOutlined />;
      case 'error': return <CloseCircleOutlined />;
      default: return <CheckCircleOutlined />;
    }
  };

  // 最近活動表格列配置
  const activityColumns = [
    {
      title: t('logs.timestamp'),
      dataIndex: 'time',
      key: 'time',
      width: 180
    },
    {
      title: t('logs.action'),
      dataIndex: 'action',
      key: 'action',
      width: 150
    },
    {
      title: t('common.details'),
      dataIndex: 'details',
      key: 'details',
      ellipsis: true
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
          {t(`common.${status}`)}
        </Tag>
      )
    }
  ];

  return (
    <div style={{ padding: getCardPadding() }}>
      {/* 頁面標題和快捷操作 */}
      <div style={{ 
        marginBottom: getSpacing(), 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        flexDirection: isMobile ? 'column' : 'row',
        gap: isMobile ? getSpacing() : 0
      }}>
        <h1>{t('dashboard.title')}</h1>
        <Space direction={isMobile ? 'vertical' : 'horizontal'} size="middle">
          <Button 
            type="primary" 
            icon={<ReloadOutlined spin={refreshing} />}
            onClick={handleRefresh}
            loading={refreshing}
            size={isMobile ? 'small' : 'middle'}
          >
            {t('common.refresh')}
          </Button>
          <Button 
            icon={<GlobalOutlined />}
            size={isMobile ? 'small' : 'middle'}
          >
            {t('dashboard.quickActions')}
          </Button>
          {wsConnected && (
            <Tag color="green">
              實時連接
            </Tag>
          )}
        </Space>
      </div>

      {/* 統計卡片 */}
      <Row gutter={getSpacing()} style={{ marginBottom: getSpacing() }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={t('dashboard.totalProxies')}
              value={statistics.totalProxies}
              valueStyle={{ color: '#1890ff' }}
              prefix={<GlobalOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={t('dashboard.validProxies')}
              value={statistics.validProxies}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
              suffix={`${((statistics.validProxies / statistics.totalProxies) * 100).toFixed(1)}%`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={t('dashboard.invalidProxies')}
              value={statistics.invalidProxies}
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<CloseCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={t('dashboard.successRate')}
              value={statistics.successRate}
              precision={1}
              valueStyle={{ color: statistics.successRate >= 70 ? '#52c41a' : '#ff4d4f' }}
              suffix="%"
              prefix={statistics.successRate >= 70 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 圖表網格 */}
      <Row gutter={getSpacing()} style={{ marginBottom: getSpacing() }}>
        <Col xs={24} lg={12}>
          <Card title={t('dashboard.proxyTrend')}>
            <ReactECharts 
              option={proxyTrendOption} 
              style={{ height: isMobile ? '250px' : '300px' }}
              opts={{ renderer: 'canvas' }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title={t('dashboard.validityDistribution')}>
            <ReactECharts 
              option={validityDistributionOption} 
              style={{ height: isMobile ? '250px' : '300px' }}
              opts={{ renderer: 'canvas' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={getSpacing()} style={{ marginBottom: getSpacing() }}>
        <Col span={24}>
          <Card title={t('dashboard.geographicDistribution')}>
            <ReactECharts 
              option={geographicDistributionOption} 
              style={{ height: isMobile ? '250px' : '300px' }}
              opts={{ renderer: 'canvas' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近活動 */}
      <Row gutter={getSpacing()}>
        <Col span={24}>
          <Card title={t('dashboard.recentActivity')}>
            <Table
              columns={activityColumns}
              dataSource={recentActivity}
              pagination={{
                pageSize: isMobile ? 3 : 5,
                showSizeChanger: false,
                showQuickJumper: !isMobile,
                simple: isMobile
              }}
              size={isMobile ? 'small' : 'middle'}
              rowKey="key"
              scroll={isMobile ? { x: 600 } : undefined}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
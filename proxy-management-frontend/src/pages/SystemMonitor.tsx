/**
 * 系統監控頁面組件
 * @author TRAE
 * @description 顯示系統狀態、任務隊列、錯誤日誌和系統指標
 */

import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Button, Space, Tabs, Empty, Alert } from 'antd';
import { ReloadOutlined, CheckCircleOutlined, CloseCircleOutlined, SyncOutlined, ClockCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { Line } from '@ant-design/charts';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import type { ChartData } from '../types';
import { 
  fetchSystemStatus, 
  fetchTaskQueue, 
  fetchSystemMetrics,
  fetchErrorLogs,
  fetchOperationLogs,
  selectSystemStatus,
  selectTaskQueue,
  selectErrorLogs,
  selectOperationLogs,
  selectSystemLoading,
  selectSystemError,
  selectSystemMetrics
} from '../store/slices/systemSlice';

const { TabPane } = Tabs;

/**
 * 系統監控頁面組件
 */
const SystemMonitor: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  
  const systemStatus = useAppSelector(selectSystemStatus);
  const taskQueues = useAppSelector(selectTaskQueue);
  const errorLogs = useAppSelector(selectErrorLogs);
  const operationLogs = useAppSelector(selectOperationLogs);
  const loading = useAppSelector(selectSystemLoading);
  const error = useAppSelector(selectSystemError);
  const systemMetrics = useAppSelector(selectSystemMetrics);
  
  const [activeTab, setActiveTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  // 加載數據
  const loadData = async () => {
    dispatch(fetchSystemStatus());
    dispatch(fetchTaskQueue());
    dispatch(fetchErrorLogs());
    dispatch(fetchOperationLogs());
    dispatch(fetchSystemMetrics('cpu'));
    dispatch(fetchSystemMetrics('memory'));
    dispatch(fetchSystemMetrics('network'));
  };

  // 初始化加載
  useEffect(() => {
    loadData();
  }, []);

  // 自動刷新
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadData();
      }, 5000);
      setRefreshInterval(interval);
    } else {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
    }

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [autoRefresh]);

  // 任務狀態標籤
  const getTaskStatusTag = (status: string) => {
    const statusMap = {
      running: { color: 'processing', icon: <SyncOutlined spin /> },
      pending: { color: 'warning', icon: <ClockCircleOutlined /> },
      completed: { color: 'success', icon: <CheckCircleOutlined /> },
      failed: { color: 'error', icon: <CloseCircleOutlined /> }
    };
    
    const config = statusMap[status as keyof typeof statusMap] || { color: 'default', icon: null };
    
    return (
      <Tag color={config.color} icon={config.icon}>
        {t(`system.taskStatus.${status}`)}
      </Tag>
    );
  };

  // 日誌級別標籤
  const getLogLevelTag = (level: string) => {
    const levelMap = {
      ERROR: { color: 'error', icon: <CloseCircleOutlined /> },
      WARNING: { color: 'warning', icon: <ExclamationCircleOutlined /> },
      INFO: { color: 'processing', icon: <CheckCircleOutlined /> }
    };
    
    const config = levelMap[level as keyof typeof levelMap] || { color: 'default', icon: null };
    
    return (
      <Tag color={config.color} icon={config.icon}>
        {level}
      </Tag>
    );
  };

  // 任務隊表格列 - 基於 TaskQueue 結構
  const taskColumns = [
    {
      title: t('system.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getTaskStatusTag(status)
    },
    {
      title: t('system.waiting'),
      dataIndex: 'waiting',
      key: 'waiting',
      width: 100,
      render: (waiting: number) => <Tag color="orange">{waiting}</Tag>
    },
    {
      title: t('system.running'),
      dataIndex: 'running',
      key: 'running',
      width: 100,
      render: (running: number) => <Tag color="processing">{running}</Tag>
    },
    {
      title: t('system.completed'),
      dataIndex: 'completed',
      key: 'completed',
      width: 100,
      render: (completed: number) => <Tag color="success">{completed}</Tag>
    },
    {
      title: t('system.failed'),
      dataIndex: 'failed',
      key: 'failed',
      width: 100,
      render: (failed: number) => <Tag color="error">{failed}</Tag>
    },
    {
      title: t('system.total'),
      dataIndex: 'total',
      key: 'total',
      width: 100,
      render: (total: number) => <Tag color="blue">{total}</Tag>
    }
  ];

  // 錯誤日誌表格列
  const errorLogColumns = [
    {
      title: t('system.timestamp'),
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString()
    },
    {
      title: t('system.level'),
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: (level: string) => getLogLevelTag(level.toUpperCase())
    },
    {
      title: t('system.message'),
      dataIndex: 'message',
      key: 'message',
      ellipsis: true
    },
    {
      title: t('system.stack'),
      dataIndex: 'stack',
      key: 'stack',
      ellipsis: true,
      width: 300
    }
  ];

  // 操作日誌表格列
  const operationLogColumns = [
    {
      title: t('system.timestamp'),
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString()
    },
    {
      title: t('system.user'),
      dataIndex: 'userId',
      key: 'userId',
      width: 120
    },
    {
      title: t('system.action'),
      dataIndex: 'action',
      key: 'action',
      width: 150,
      render: (action: string) => (
        <Tag color="blue">{action}</Tag>
      )
    },
    {
      title: t('system.target'),
      dataIndex: 'target',
      key: 'target',
      width: 150,
      render: (target: string) => (
        <Tag color="green">{target}</Tag>
      )
    },
    {
      title: t('system.details'),
      dataIndex: 'details',
      key: 'details',
      ellipsis: true,
      width: 400,
      render: (details: any) => (
        <div>
          {details && (
            <div>
              <div>結果: {details.result}</div>
              <div>訊息: {details.message}</div>
            </div>
          )}
        </div>
      )
    }
  ];

  // 圖表配置 - 處理 ChartData 類型數據
  const getChartConfig = (data: ChartData[], title: string, color: string) => {
    if (!data || data.length === 0 || !data[0].series || data[0].series.length === 0) {
      return {
        data: [],
        xField: 'time',
        yField: 'value',
        title: {
          text: title,
          style: {
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        smooth: true,
        color,
        point: {
          size: 3,
          shape: 'circle'
        },
        tooltip: {
          showMarkers: true
        },
        xAxis: {
          type: 'time',
          tickCount: 5
        },
        yAxis: {
          label: {
            formatter: (value: number) => `${value.toFixed(1)}`
          }
        }
      };
    }
    
    // 將 ChartData 轉換為圖表需要的格式
    const chartData = data[0].xAxis.map((time: string, index: number) => ({
      time: time,
      value: data[0].series[0].data[index] || 0
    }));
    
    return {
      data: chartData,
      xField: 'time',
      yField: 'value',
      title: {
        text: title,
        style: {
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      smooth: true,
      color,
      point: {
        size: 3,
        shape: 'circle'
      },
      tooltip: {
        showMarkers: true
      },
      xAxis: {
        type: 'time',
        tickCount: 5
      },
      yAxis: {
        label: {
          formatter: (value: number) => `${value.toFixed(1)}`
        }
      }
    };
  };

  return (
    <div className="system-monitor">
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            onClick={loadData}
            loading={loading}
          >
            {t('common.refresh')}
          </Button>
          <Button
            type={autoRefresh ? 'primary' : 'default'}
            icon={<SyncOutlined spin={autoRefresh} />}
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {t('common.autoRefresh')}
          </Button>
        </Space>
      </div>

      {error && (
        <Alert
          message={t('common.error')}
          description={error}
          type="error"
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab={t('system.overview')} key="overview">
          <Row gutter={[16, 16]}>
            {/* 系統狀態卡片 */}
            {systemStatus && (
              <>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title={t('system.cpuUsage')}
                      value={systemStatus.cpuUsage}
                      precision={1}
                      suffix="%"
                      valueStyle={{ color: systemStatus.cpuUsage > 80 ? '#cf1322' : '#3f8600' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title={t('system.memoryUsage')}
                      value={systemStatus.memoryUsage}
                      precision={1}
                      suffix="%"
                      valueStyle={{ color: systemStatus.memoryUsage > 80 ? '#cf1322' : '#3f8600' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title={t('system.diskUsage')}
                      value={systemStatus.diskUsage}
                      precision={1}
                      suffix="%"
                      valueStyle={{ color: systemStatus.diskUsage > 80 ? '#cf1322' : '#3f8600' }}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title={t('system.activeTasks')}
                      value={systemStatus.activeTasks}
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Card>
                </Col>
              </>
            )}

            {/* 系統指標圖表 */}
            <Col xs={24} lg={8}>
              <Card title={t('system.cpuUsageTrend')}>
                {systemMetrics.cpuUsage.length > 0 ? (
                  <Line {...getChartConfig(systemMetrics.cpuUsage, t('system.cpuUsage'), '#1890ff')} height={200} />
                ) : (
                  <Empty description={t('common.noData')} />
                )}
              </Card>
            </Col>
            <Col xs={24} lg={8}>
              <Card title={t('system.memoryUsageTrend')}>
                {systemMetrics.memoryUsage.length > 0 ? (
                  <Line {...getChartConfig(systemMetrics.memoryUsage, t('system.memoryUsage'), '#52c41a')} height={200} />
                ) : (
                  <Empty description={t('common.noData')} />
                )}
              </Card>
            </Col>
            <Col xs={24} lg={8}>
              <Card title={t('system.networkTrafficTrend')}>
                {systemMetrics.networkTraffic.length > 0 ? (
                  <Line {...getChartConfig(systemMetrics.networkTraffic, t('system.networkTraffic'), '#fa8c16')} height={200} />
                ) : (
                  <Empty description={t('common.noData')} />
                )}
              </Card>
            </Col>

            {/* 任務隊列 */}
            <Col xs={24}>
              <Card title={t('system.taskQueue')}>
                <Table
                  columns={taskColumns}
                  dataSource={taskQueues.length > 0 ? [taskQueues[0]] : []}
                  rowKey={(record) => `task-queue-${record.total}`}
                  loading={loading}
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    showTotal: (total) => t('common.totalItems', { total })
                  }}
                  locale={{ emptyText: <Empty description={t('common.noData')} /> }}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane tab={t('system.errorLogs')} key="errorLogs">
          <Table
            columns={errorLogColumns}
            dataSource={errorLogs}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => t('common.totalItems', { total })
            }}
            locale={{ emptyText: <Empty description={t('common.noData')} /> }}
          />
        </TabPane>

        <TabPane tab={t('system.operationLogs')} key="operationLogs">
          <Table
            columns={operationLogColumns}
            dataSource={operationLogs}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => t('common.totalItems', { total })
            }}
            locale={{ emptyText: <Empty description={t('common.noData')} /> }}
          />
        </TabPane>
      </Tabs>
    </div>
  );
};

export default SystemMonitor;
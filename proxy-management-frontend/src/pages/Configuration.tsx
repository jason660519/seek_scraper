/**
 * 配置中心頁面組件
 * @author TRAE
 * @description 管理系統配置，包括調度器、來源、通知和導出配置
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  InputNumber, 
  Select, 
  Switch, 
  Button, 
  Space, 
  Tabs, 
  Table, 
  Tag, 
  Modal, 
  message,
  Row,
  Col,
  Checkbox
} from 'antd';
import { 
  SaveOutlined, 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 

  ReloadOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
// import { useAppDispatch, useAppSelector } from '../../hooks/redux';
// import type { SystemConfig } from '../../types';

const { TabPane } = Tabs;
const { Option } = Select;

/**
 * 配置中心頁面組件
 */
const Configuration: React.FC = () => {
  const { t } = useTranslation();
  // const dispatch = useAppDispatch();
  
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState<any>(null);
  
  // 來源管理狀態
  const [sources, setSources] = useState<any[]>([]);
  const [sourceModalVisible, setSourceModalVisible] = useState(false);
  const [editingSource, setEditingSource] = useState<any>(null);
  
  // 通知配置狀態
  // const [notifications, setNotifications] = useState<any[]>([]);
  // const [notificationModalVisible, setNotificationModalVisible] = useState(false);

  // 模擬配置數據
  const mockConfig: any = {
    scheduler: {
      enabled: true,
      interval: 300,
      maxConcurrentTasks: 10,
      retryAttempts: 3,
      retryDelay: 60,
      workingHours: {
        start: '09:00',
        end: '18:00',
        days: [1, 2, 3, 4, 5] // 週一到週五
      }
    },
    sources: {
      enabled: true,
      autoDiscovery: true,
      validationTimeout: 30,
      maxSources: 50,
      blacklist: ['suspicious-proxy.com', 'untrusted-source.net']
    },
    notifications: {
      enabled: true,
      email: {
        enabled: true,
        smtp: {
          host: 'smtp.gmail.com',
          port: 587,
          username: 'your-email@gmail.com',
          password: 'your-app-password',
          secure: true
        },
        recipients: ['admin@example.com'],
        templates: {
          systemAlert: 'System Alert: {{message}}',
          proxyValidationComplete: 'Proxy validation completed. Valid: {{valid}}, Invalid: {{invalid}}'
        }
      },
      webhook: {
        enabled: false,
        url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
        headers: {
          'Content-Type': 'application/json'
        }
      },
      desktop: {
        enabled: true,
        showSystemAlerts: true,
        showTaskUpdates: true,
        showProxyUpdates: false
      }
    },
    export: {
      defaultFormat: 'csv',
      includeMetadata: true,
      autoExport: {
        enabled: true,
        interval: 3600, // 1小時
        formats: ['csv', 'json'],
        destination: 'local'
      },
      filters: {
        excludeInvalid: false,
        excludeExpired: true,
        minAnonymity: 'medium'
      }
    },
    security: {
      rateLimiting: {
        enabled: true,
        maxRequests: 100,
        windowMs: 60000 // 1分鐘
      },
      cors: {
        enabled: true,
        origins: ['http://localhost:3000', 'http://localhost:5173']
      },
      auth: {
        tokenExpiration: 3600,
        refreshTokenExpiration: 604800, // 7天
        requireCaptcha: false
      }
    }
  };

  // 模擬來源數據
  const mockSources = [
    {
      id: '1',
      name: 'Free Proxy List',
      url: 'https://free-proxy-list.net/',
      type: 'web_scraping',
      enabled: true,
      lastSync: '2024-01-15 14:30:00',
      proxyCount: 156,
      successRate: 85.5,
      status: 'active'
    },
    {
      id: '2',
      name: 'Proxy API',
      url: 'https://api.proxyscrape.com/v2/',
      type: 'api',
      enabled: true,
      lastSync: '2024-01-15 14:25:00',
      proxyCount: 89,
      successRate: 92.3,
      status: 'active'
    },
    {
      id: '3',
      name: 'Premium Proxy Source',
      url: 'https://premium-proxies.example.com/api',
      type: 'api',
      enabled: false,
      lastSync: '2024-01-15 10:00:00',
      proxyCount: 0,
      successRate: 0,
      status: 'inactive'
    }
  ];

  // 加載配置
  useEffect(() => {
    loadConfig();
    loadSources();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      // 模擬 API 調用
      await new Promise(resolve => setTimeout(resolve, 500));
      setConfig(mockConfig);
      form.setFieldsValue(mockConfig);
    } catch (error) {
      message.error(t('config.loadError'));
    } finally {
      setLoading(false);
    }
  };

  const loadSources = async () => {
    // 模擬 API 調用
    await new Promise(resolve => setTimeout(resolve, 300));
    setSources(mockSources);
  };

  // 保存配置
  const handleSave = async (values: any) => {
    setLoading(true);
    try {
      // 模擬 API 調用
      await new Promise(resolve => setTimeout(resolve, 1000));
      setConfig(values);
      message.success(t('config.saveSuccess'));
    } catch (error) {
      message.error(t('config.saveError'));
    } finally {
      setLoading(false);
    }
  };

  // 來源管理
  const handleAddSource = () => {
    setEditingSource(null);
    setSourceModalVisible(true);
  };

  const handleEditSource = (source: any) => {
    setEditingSource(source);
    setSourceModalVisible(true);
  };

  const handleDeleteSource = (sourceId: string) => {
    Modal.confirm({
      title: t('config.confirmDelete'),
      content: t('config.deleteSourceConfirm'),
      onOk: async () => {
        try {
          // 模擬 API 調用
          await new Promise(resolve => setTimeout(resolve, 300));
          setSources(sources.filter(s => s.id !== sourceId));
          message.success(t('config.deleteSuccess'));
        } catch (error) {
          message.error(t('config.deleteError'));
        }
      }
    });
  };

  const handleSourceModalOk = async (values: any) => {
    try {
      // 模擬 API 調用
      await new Promise(resolve => setTimeout(resolve, 500));
      
      if (editingSource) {
        // 編輯現有來源
        setSources(sources.map(s => 
          s.id === editingSource.id 
            ? { ...s, ...values, lastSync: new Date().toLocaleString() }
            : s
        ));
      } else {
        // 添加新來源
        const newSource = {
          id: Date.now().toString(),
          ...values,
          lastSync: new Date().toLocaleString(),
          proxyCount: 0,
          successRate: 0,
          status: 'active'
        };
        setSources([...sources, newSource]);
      }
      
      setSourceModalVisible(false);
      message.success(t('config.saveSuccess'));
    } catch (error) {
      message.error(t('config.saveError'));
    }
  };

  // 來源表格列
  const sourceColumns = [
    {
      title: t('config.sourceName'),
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: t('config.sourceType'),
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => (
        <Tag color={type === 'api' ? 'blue' : 'green'}>
          {t(`config.sourceTypes.${type}`)}
        </Tag>
      )
    },
    {
      title: t('config.proxyCount'),
      dataIndex: 'proxyCount',
      key: 'proxyCount',
      align: 'center' as const
    },
    {
      title: t('config.successRate'),
      dataIndex: 'successRate',
      key: 'successRate',
      render: (rate: number) => (
        <span style={{ color: rate > 80 ? '#52c41a' : rate > 60 ? '#faad14' : '#ff4d4f' }}>
          {rate.toFixed(1)}%
        </span>
      )
    },
    {
      title: t('config.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {t(`config.status.${status}`)}
        </Tag>
      )
    },
    {
      title: t('config.lastSync'),
      dataIndex: 'lastSync',
      key: 'lastSync'
    },
    {
      title: t('common.actions'),
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEditSource(record)}
          >
            {t('common.edit')}
          </Button>
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteSource(record.id)}
          >
            {t('common.delete')}
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div className="configuration">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={config || mockConfig}
      >
        <Tabs defaultActiveKey="scheduler">
          <TabPane tab={t('config.scheduler')} key="scheduler">
            <Row gutter={16}>
              <Col xs={24} lg={12}>
                <Card title={t('config.basicSettings')}>
                  <Form.Item
                    label={t('config.enableScheduler')}
                    name={['scheduler', 'enabled']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.validationInterval')}
                    name={['scheduler', 'interval']}
                    rules={[{ required: true, message: t('config.validationIntervalRequired') }]}
                  >
                    <InputNumber
                      min={60}
                      max={3600}
                      style={{ width: '100%' }}
                      addonAfter={t('config.seconds')}
                    />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.maxConcurrentTasks')}
                    name={['scheduler', 'maxConcurrentTasks']}
                    rules={[{ required: true, message: t('config.maxConcurrentTasksRequired') }]}
                  >
                    <InputNumber
                      min={1}
                      max={50}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Card>
              </Col>
              
              <Col xs={24} lg={12}>
                <Card title={t('config.retrySettings')}>
                  <Form.Item
                    label={t('config.retryAttempts')}
                    name={['scheduler', 'retryAttempts']}
                    rules={[{ required: true, message: t('config.retryAttemptsRequired') }]}
                  >
                    <InputNumber
                      min={0}
                      max={10}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.retryDelay')}
                    name={['scheduler', 'retryDelay']}
                    rules={[{ required: true, message: t('config.retryDelayRequired') }]}
                  >
                    <InputNumber
                      min={10}
                      max={600}
                      style={{ width: '100%' }}
                      addonAfter={t('config.seconds')}
                    />
                  </Form.Item>
                </Card>
              </Col>
            </Row>
          </TabPane>

          <TabPane tab={t('config.sources')} key="sources">
            <Card
              title={t('config.sourceManagement')}
              extra={
                <Space>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleAddSource}
                  >
                    {t('config.addSource')}
                  </Button>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={loadSources}
                  >
                    {t('common.refresh')}
                  </Button>
                </Space>
              }
            >
              <Table
                columns={sourceColumns}
                dataSource={sources}
                rowKey="id"
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showTotal: (total) => t('common.totalItems', { total })
                }}
              />
            </Card>
          </TabPane>

          <TabPane tab={t('config.notifications')} key="notifications">
            <Row gutter={16}>
              <Col xs={24} lg={12}>
                <Card title={t('config.emailSettings')}>
                  <Form.Item
                    label={t('config.enableEmail')}
                    name={['notifications', 'email', 'enabled']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.smtpHost')}
                    name={['notifications', 'email', 'smtp', 'host']}
                  >
                    <Input />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.smtpPort')}
                    name={['notifications', 'email', 'smtp', 'port']}
                  >
                    <InputNumber style={{ width: '100%' }} />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.smtpUsername')}
                    name={['notifications', 'email', 'smtp', 'username']}
                  >
                    <Input />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.smtpPassword')}
                    name={['notifications', 'email', 'smtp', 'password']}
                  >
                    <Input.Password />
                  </Form.Item>
                </Card>
              </Col>
              
              <Col xs={24} lg={12}>
                <Card title={t('config.desktopNotifications')}>
                  <Form.Item
                    label={t('config.enableDesktopNotifications')}
                    name={['notifications', 'desktop', 'enabled']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.showSystemAlerts')}
                    name={['notifications', 'desktop', 'showSystemAlerts']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.showTaskUpdates')}
                    name={['notifications', 'desktop', 'showTaskUpdates']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.showProxyUpdates')}
                    name={['notifications', 'desktop', 'showProxyUpdates']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                </Card>
              </Col>
            </Row>
          </TabPane>

          <TabPane tab={t('config.export')} key="export">
            <Row gutter={16}>
              <Col xs={24} lg={12}>
                <Card title={t('config.exportSettings')}>
                  <Form.Item
                    label={t('config.defaultFormat')}
                    name={['export', 'defaultFormat']}
                    rules={[{ required: true }]}
                  >
                    <Select>
                      <Option value="csv">CSV</Option>
                      <Option value="json">JSON</Option>
                      <Option value="txt">TXT</Option>
                    </Select>
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.includeMetadata')}
                    name={['export', 'includeMetadata']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.excludeInvalid')}
                    name={['export', 'filters', 'excludeInvalid']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.excludeExpired')}
                    name={['export', 'filters', 'excludeExpired']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.minAnonymity')}
                    name={['export', 'filters', 'minAnonymity']}
                  >
                    <Select>
                      <Option value="low">{t('config.anonymityLow')}</Option>
                      <Option value="medium">{t('config.anonymityMedium')}</Option>
                      <Option value="high">{t('config.anonymityHigh')}</Option>
                    </Select>
                  </Form.Item>
                </Card>
              </Col>
              
              <Col xs={24} lg={12}>
                <Card title={t('config.autoExport')}>
                  <Form.Item
                    label={t('config.enableAutoExport')}
                    name={['export', 'autoExport', 'enabled']}
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.exportInterval')}
                    name={['export', 'autoExport', 'interval']}
                  >
                    <InputNumber
                      min={300}
                      max={86400}
                      style={{ width: '100%' }}
                      addonAfter={t('config.seconds')}
                    />
                  </Form.Item>
                  
                  <Form.Item
                    label={t('config.exportFormats')}
                    name={['export', 'autoExport', 'formats']}
                  >
                    <Checkbox.Group>
                      <Checkbox value="csv">CSV</Checkbox>
                      <Checkbox value="json">JSON</Checkbox>
                      <Checkbox value="txt">TXT</Checkbox>
                    </Checkbox.Group>
                  </Form.Item>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </Tabs>

        <div style={{ marginTop: 24, textAlign: 'right' }}>
          <Space>
            <Button onClick={() => form.resetFields()}>
              {t('common.reset')}
            </Button>
            <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
              {t('common.save')}
            </Button>
          </Space>
        </div>
      </Form>

      {/* 來源編輯模態框 */}
      <Modal
        title={editingSource ? t('config.editSource') : t('config.addSource')}
        visible={sourceModalVisible}
        onCancel={() => setSourceModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          initialValues={editingSource || { enabled: true, type: 'api' }}
          onFinish={handleSourceModalOk}
          layout="vertical"
        >
          <Form.Item
            label={t('config.sourceName')}
            name="name"
            rules={[{ required: true, message: t('config.sourceNameRequired') }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            label={t('config.sourceUrl')}
            name="url"
            rules={[{ required: true, message: t('config.sourceUrlRequired') }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item
            label={t('config.sourceType')}
            name="type"
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="api">API</Option>
              <Option value="web_scraping">Web Scraping</Option>
              <Option value="file">File</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            label={t('config.enabled')}
            name="enabled"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setSourceModalVisible(false)}>
                {t('common.cancel')}
              </Button>
              <Button type="primary" htmlType="submit">
                {t('common.save')}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Configuration;